"""SPARQL query service for interacting with the GraphDB"""
from typing import List
import requests
from fastapi import HTTPException

from config import GRAPHDB_ENDPOINT, SPARQL_PREFIXES
from utils import extract_value_from_uri, is_base_form


# Global cache for Pokemon forms to avoid repeated SPARQL queries
_pokemon_forms_cache = {}


def execute_sparql_query(query: str) -> dict:
    """Execute SPARQL query against GraphDB
    
    Args:
        query: SPARQL query string (prefixes will be prepended automatically)
        
    Returns:
        JSON response from the SPARQL endpoint
        
    Raises:
        HTTPException: If the query fails
    """
    full_query = SPARQL_PREFIXES + query
    
    try:
        response = requests.post(
            GRAPHDB_ENDPOINT,
            data=full_query,
            headers={
                "Content-Type": "application/sparql-query",
                "Accept": "application/sparql-results+json"
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"SPARQL Error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database query failed: {str(e)}"
        )


def get_pokemon_forms_from_sparql(pokemon_id: int) -> list:
    """Get all forms for a Pokemon ID from the RDF data, sorted with base form first
    
    Args:
        pokemon_id: The Pokemon's national dex number
        
    Returns:
        List of dicts with keys: name, type2, is_base
    """
    if pokemon_id in _pokemon_forms_cache:
        return _pokemon_forms_cache[pokemon_id]
    
    query = f"""
    SELECT DISTINCT ?name ?type2
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number {pokemon_id} ;
               ex:name ?name .
      OPTIONAL {{ ?pokemon ex:type2 ?type2 . }}
    }}
    ORDER BY ?name
    """
    
    data = execute_sparql_query(query)
    forms = []
    
    for binding in data["results"]["bindings"]:
        raw_name = binding.get("name", {}).get("value", "")
        
        # Extract type2 if present
        type2 = None
        if "type2" in binding:
            type2 = extract_value_from_uri(binding["type2"]["value"])
        
        # Add form if not already in list (handle duplicates from cartesian products)
        if not any(f["name"] == raw_name for f in forms):
            forms.append({
                "name": raw_name,
                "type2": type2,
                "is_base": is_base_form(raw_name)
            })
    
    # Sort: base forms first, then alphabetically
    forms.sort(key=lambda x: (not x["is_base"], x["name"]))
    
    _pokemon_forms_cache[pokemon_id] = forms
    return forms


def get_evolution_chain_from_sparql(pokemon_id: int) -> List[int]:
    """Get the complete evolution chain for a Pokemon
    
    Args:
        pokemon_id: The Pokemon's national dex number
        
    Returns:
        List of Pokemon IDs in the evolution chain, ordered from base to final
    """
    query = f"""
    SELECT DISTINCT ?fromId ?toId
    WHERE {{
      ?link a ex:EvolutionLink ;
            ex:evolvesFrom ?from ;
            ex:evolvesTo ?to .
      ?from ex:number ?fromId .
      ?to ex:number ?toId .
    }}
    """
    
    data = execute_sparql_query(query)
    
    # Build evolution graph
    evolution_map = {}
    reverse_map = {}
    
    for binding in data["results"]["bindings"]:
        from_id = int(binding["fromId"]["value"])
        to_id = int(binding["toId"]["value"])
        
        if from_id not in evolution_map:
            evolution_map[from_id] = []
        evolution_map[from_id].append(to_id)
        reverse_map[to_id] = from_id
    
    # Find the base of the chain
    current = pokemon_id
    while current in reverse_map:
        current = reverse_map[current]
    base_pokemon = current
    
    # Build chain from base forward
    chain = [base_pokemon]
    current = base_pokemon
    
    while current in evolution_map:
        # Take first evolution (handles branching by picking first path)
        next_evolution = evolution_map[current][0]
        chain.append(next_evolution)
        current = next_evolution
    
    return chain


def clear_forms_cache():
    """Clear the Pokemon forms cache (useful for testing or data updates)"""
    _pokemon_forms_cache.clear()
