"""Main FastAPI application with Pokemon API routes"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from urllib.parse import unquote
import requests

from config import (
    API_TITLE, API_VERSION, API_DESCRIPTION,
    CORS_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS,
    RECOMMENDER_URL
)
from services.sparql_service import (
    execute_sparql_query,
    get_pokemon_forms_from_sparql,
    get_evolution_chain_from_sparql,
    _pokemon_forms_cache
)
from services.pokeapi_service import fetch_pokeapi_species_data
from domain.pokemon_logic import get_correct_type2_for_form, parse_abilities_from_string
from utils import format_pokemon_name, extract_value_from_uri, get_pokemon_image_url, is_base_form

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)


# ============================================================================
# Helper Functions
# ============================================================================

def parse_pokemon_from_binding(
    binding: dict, 
    include_stats: bool = False, 
    fetch_pokeapi: bool = False
) -> dict:
    """Parse SPARQL binding into Pokemon dict
    
    Args:
        binding: SPARQL query result binding
        include_stats: Whether to include stat fields
        fetch_pokeapi: Whether to fetch additional data from PokeAPI
        
    Returns:
        Dict with Pokemon data
    """
    pokemon_id = int(binding.get("id", {}).get("value", 0))
    raw_name = binding.get("name", {}).get("value", "Unknown")
    
    # Fetch PokeAPI data if requested
    if fetch_pokeapi:
        pokeapi_data = fetch_pokeapi_species_data(pokemon_id)
    else:
        pokeapi_data = {"height": 0, "weight": 0, "category": "Pokemon"}
    
    pokemon = {
        "id": pokemon_id,
        "name": raw_name,
        "types": [],
        "imageUrl": "",  # Will be set later
        "height": pokeapi_data["height"],
        "weight": pokeapi_data["weight"],
        "abilities": [],
        "category": pokeapi_data["category"],
        "evolutionChain": [],
    }
    
    # Parse types
    if "type1" in binding:
        pokemon["types"].append(extract_value_from_uri(binding["type1"]["value"]))
    if "type2" in binding:
        pokemon["types"].append(extract_value_from_uri(binding["type2"]["value"]))
    
    # Parse abilities
    if "abilities" in binding:
        abilities_str = binding["abilities"]["value"]
        pokemon["abilities"] = parse_abilities_from_string(abilities_str)
    
    # Parse stats if requested
    if include_stats:
        pokemon["stats"] = {
            "hp": int(binding.get("hp", {}).get("value", 0)),
            "attack": int(binding.get("attack", {}).get("value", 0)),
            "defense": int(binding.get("defense", {}).get("value", 0)),
            "specialAttack": int(binding.get("spAttack", {}).get("value", 0)),
            "specialDefense": int(binding.get("spDefense", {}).get("value", 0)),
            "speed": int(binding.get("speed", {}).get("value", 0)),
        }
    
    return pokemon


# ============================================================================
# API Routes
# ============================================================================

@app.get("/")
def root():
    """API health check"""
    return {"status": "ok", "message": "Pokemon API is running"}


@app.get("/api/pokemon/search")
def get_search_list(limit: int = Query(default=1000, le=2000)):
    """Lightweight endpoint for search - returns all distinct forms with correct types"""
    query = f"""
    SELECT ?id ?name ?type1 ?type2
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number ?id ;
               ex:name ?name .
      
      OPTIONAL {{ ?pokemon ex:type1 ?type1 . }}
      OPTIONAL {{ ?pokemon ex:type2 ?type2 . }}
    }}
    ORDER BY ?id ?name
    LIMIT {limit}
    """
    
    data = execute_sparql_query(query)
    
    # First pass: collect all forms per Pokemon ID to build the form order
    pokemon_forms_order = {}
    
    for binding in data["results"]["bindings"]:
        pokemon_id = int(binding.get("id", {}).get("value", 0))
        pokemon_name = binding.get("name", {}).get("value", "Unknown")
        
        if pokemon_id not in pokemon_forms_order:
            pokemon_forms_order[pokemon_id] = []
        
        if pokemon_name not in pokemon_forms_order[pokemon_id]:
            pokemon_forms_order[pokemon_id].append(pokemon_name)
    
    # Sort each Pokemon's forms: base first, then alphabetically
    # Also populate the cache for get_pokemon_forms_from_sparql
    for pokemon_id in pokemon_forms_order:
        forms = pokemon_forms_order[pokemon_id]
        forms.sort(key=lambda name: (not is_base_form(name), name))
        
        # Populate cache
        _pokemon_forms_cache[pokemon_id] = [
            {"name": name, "type2": None, "is_base": is_base_form(name)} 
            for name in forms
        ]
    
    # Second pass: group by (id, formatted_name) to collect type data
    form_data = {}
    
    for binding in data["results"]["bindings"]:
        pokemon_id = int(binding.get("id", {}).get("value", 0))
        pokemon_name = binding.get("name", {}).get("value", "Unknown")
        
        key = (pokemon_id, pokemon_name)
        
        if key not in form_data:
            form_data[key] = {
                "id": pokemon_id,
                "name": pokemon_name,
                "type1": None,
                "type2s": set()
            }
        
        if "type1" in binding and not form_data[key]["type1"]:
            form_data[key]["type1"] = extract_value_from_uri(binding["type1"]["value"])
        
        if "type2" in binding:
            form_data[key]["type2s"].add(extract_value_from_uri(binding["type2"]["value"]))
    
    # Build results
    results = []
    for key, form_info in form_data.items():
        types = []
        if form_info["type1"]:
            types.append(form_info["type1"])
        
        if form_info["type2s"]:
            if len(form_info["type2s"]) == 1:
                types.append(list(form_info["type2s"])[0])
            else:
                correct_type2 = get_correct_type2_for_form(
                    form_info["name"], 
                    list(form_info["type2s"])
                )
                if correct_type2:
                    types.append(correct_type2)
        
        # Generate image URL
        pokemon_id = form_info["id"]
        pokemon_name = form_info["name"]
        form_order = pokemon_forms_order[pokemon_id]
        form_index = form_order.index(pokemon_name) if pokemon_name in form_order else 0
        
        from config import POKEMON_COM_IMAGE_BASE_URL
        base_url = f"{POKEMON_COM_IMAGE_BASE_URL}/{pokemon_id:03d}"
        imageUrl = f"{base_url}.png" if form_index == 0 else f"{base_url}_f{form_index + 1}.png"
        
        results.append({
            "id": pokemon_id,
            "name": pokemon_name,
            "types": types,
            "imageUrl": imageUrl
        })
    
    # Sort by ID, then by form order
    def sort_key(item):
        pokemon_id = item["id"]
        pokemon_name = item["name"]
        form_order = pokemon_forms_order.get(pokemon_id, [])
        form_index = form_order.index(pokemon_name) if pokemon_name in form_order else 999
        return (pokemon_id, form_index)
    
    results.sort(key=sort_key)
    return results


@app.get("/api/pokemon")
def get_all_pokemon(
    limit: int = Query(default=151, le=1000), 
    offset: int = Query(default=0, ge=0)
):
    """Get all Pokemon with pagination - returns only base forms"""
    id_query = f"""
    SELECT DISTINCT ?id
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number ?id .
    }}
    ORDER BY ?id
    OFFSET {offset}
    LIMIT {limit}
    """
    
    id_data = execute_sparql_query(id_query)
    results = []
    
    for id_binding in id_data["results"]["bindings"]:
        pokemon_id = int(id_binding["id"]["value"])
        
        detail_query = f"""
        SELECT ?id ?name ?type1 ?type2
        WHERE {{
          ?pokemon a ex:Pokemon ;
                   ex:number ?id ;
                   ex:name ?name .
          
          FILTER(?id = {pokemon_id})
          
          OPTIONAL {{ ?pokemon ex:type1 ?type1 . }}
          OPTIONAL {{ ?pokemon ex:type2 ?type2 . }}
        }}
        ORDER BY ?name
        LIMIT 1
        """
        
        detail_data = execute_sparql_query(detail_query)
        
        if detail_data["results"]["bindings"]:
            binding = detail_data["results"]["bindings"][0]
            pokemon = parse_pokemon_from_binding(binding)
            
            # Set image URL
            forms = get_pokemon_forms_from_sparql(pokemon_id)
            pokemon["imageUrl"] = get_pokemon_image_url(pokemon_id, pokemon["name"], forms)
            
            results.append(pokemon)
    
    return results


@app.get("/api/pokemon/{pokemon_id}")
def get_pokemon_by_id(pokemon_id: int):
    """Get specific Pokemon by ID with full details"""
    query = f"""
    SELECT DISTINCT ?id ?name ?type1 ?type2
           ?hp ?attack ?defense ?spAttack ?spDefense ?speed
           (GROUP_CONCAT(DISTINCT ?abilityName; separator=",") AS ?abilities)
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number ?id ;
               ex:name ?name .
      
      FILTER(?id = {pokemon_id})
      
      OPTIONAL {{ ?pokemon ex:type1 ?type1 . }}
      OPTIONAL {{ ?pokemon ex:type2 ?type2 . }}
      OPTIONAL {{ ?pokemon ex:hp ?hp . }}
      OPTIONAL {{ ?pokemon ex:attack ?attack . }}
      OPTIONAL {{ ?pokemon ex:defense ?defense . }}
      OPTIONAL {{ ?pokemon ex:sp_attack ?spAttack . }}
      OPTIONAL {{ ?pokemon ex:sp_defense ?spDefense . }}
      OPTIONAL {{ ?pokemon ex:speed ?speed . }}
      OPTIONAL {{ 
        ?ability a ex:Ability ;
                 ex:possessedBy ?pokemon ;
                 ex:abilityName ?abilityName .
      }}
    }}
    GROUP BY ?id ?name ?type1 ?type2 ?hp ?attack ?defense ?spAttack ?spDefense ?speed
    LIMIT 1
    """
    
    data = execute_sparql_query(query)
    
    if not data["results"]["bindings"]:
        raise HTTPException(status_code=404, detail=f"Pokemon with ID {pokemon_id} not found")
    
    binding = data["results"]["bindings"][0]
    pokemon = parse_pokemon_from_binding(binding, include_stats=True, fetch_pokeapi=True)
    
    # Set image URL and evolution chain
    forms = get_pokemon_forms_from_sparql(pokemon_id)
    pokemon["imageUrl"] = get_pokemon_image_url(pokemon_id, pokemon["name"], forms)
    pokemon["evolutionChain"] = get_evolution_chain_from_sparql(pokemon_id)
    
    return pokemon


@app.get("/api/pokemon/name/{pokemon_name}")
def get_pokemon_by_name(pokemon_name: str):
    """Get specific Pokemon by formatted name with full details"""
    pokemon_name = unquote(pokemon_name)
    
    query = f"""
    SELECT DISTINCT ?id ?name ?type1 ?type2
           ?hp ?attack ?defense ?spAttack ?spDefense ?speed
           (GROUP_CONCAT(DISTINCT ?abilityName; separator=",") AS ?abilities)
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number ?id ;
               ex:name ?name .
      
      OPTIONAL {{ ?pokemon ex:type1 ?type1 . }}
      OPTIONAL {{ ?pokemon ex:type2 ?type2 . }}
      OPTIONAL {{ ?pokemon ex:hp ?hp . }}
      OPTIONAL {{ ?pokemon ex:attack ?attack . }}
      OPTIONAL {{ ?pokemon ex:defense ?defense . }}
      OPTIONAL {{ ?pokemon ex:sp_attack ?spAttack . }}
      OPTIONAL {{ ?pokemon ex:sp_defense ?spDefense . }}
      OPTIONAL {{ ?pokemon ex:speed ?speed . }}
      OPTIONAL {{ 
        ?ability a ex:Ability ;
                 ex:possessedBy ?pokemon ;
                 ex:abilityName ?abilityName .
      }}
    }}
    GROUP BY ?id ?name ?type1 ?type2 ?hp ?attack ?defense ?spAttack ?spDefense ?speed
    """
    
    data = execute_sparql_query(query)
    
    # Find matching form and collect type2s
    form_data = {}
    pokemon_id = None
    
    for binding in data["results"]["bindings"]:
        raw_name = binding.get("name", {}).get("value", "")
        
        if raw_name == pokemon_name:
            current_id = int(binding.get("id", {}).get("value", 0))
            if pokemon_id is None:
                pokemon_id = current_id
            
            key = (current_id, raw_name)
            if key not in form_data:
                form_data[key] = {"binding": binding, "type2s": set()}
            
            if "type2" in binding:
                form_data[key]["type2s"].add(
                    extract_value_from_uri(binding["type2"]["value"])
                )
    
    if not form_data:
        raise HTTPException(
            status_code=404, 
            detail=f"Pokemon with name '{pokemon_name}' not found"
        )
    
    # Parse Pokemon
    key = list(form_data.keys())[0]
    form_info = form_data[key]
    pokemon = parse_pokemon_from_binding(
        form_info["binding"], 
        include_stats=True, 
        fetch_pokeapi=True
    )
    
    # Fix types
    types = []
    if "type1" in form_info["binding"]:
        types.append(extract_value_from_uri(form_info["binding"]["type1"]["value"]))
    
    if form_info["type2s"]:
        if len(form_info["type2s"]) == 1:
            types.append(list(form_info["type2s"])[0])
        else:
            correct_type2 = get_correct_type2_for_form(
                pokemon_name, 
                list(form_info["type2s"])
            )
            if correct_type2:
                types.append(correct_type2)
    
    pokemon["types"] = types
    
    # Fix image URL
    forms = get_pokemon_forms_from_sparql(pokemon_id)
    form_index = next((i for i, f in enumerate(forms) if f["name"] == pokemon_name), 0)
    
    from config import POKEMON_COM_IMAGE_BASE_URL
    base_url = f"{POKEMON_COM_IMAGE_BASE_URL}/{pokemon_id:03d}"
    pokemon["imageUrl"] = f"{base_url}.png" if form_index == 0 else f"{base_url}_f{form_index + 1}.png"
    
    # Add evolution chain
    pokemon["evolutionChain"] = get_evolution_chain_from_sparql(pokemon_id)
    
    return pokemon


@app.get("/api/pokemon/{pokemon_id}/forms")
def get_pokemon_forms_by_id(pokemon_id: int):
    """Get all forms of a Pokemon by ID"""
    query = f"""
    SELECT DISTINCT ?id ?name ?type1 ?type2
           ?hp ?attack ?defense ?spAttack ?spDefense ?speed
           (GROUP_CONCAT(DISTINCT ?abilityName; separator=",") AS ?abilities)
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number ?id ;
               ex:name ?name .
      
      FILTER(?id = {pokemon_id})
      
      OPTIONAL {{ ?pokemon ex:type1 ?type1 . }}
      OPTIONAL {{ ?pokemon ex:type2 ?type2 . }}
      OPTIONAL {{ ?pokemon ex:hp ?hp . }}
      OPTIONAL {{ ?pokemon ex:attack ?attack . }}
      OPTIONAL {{ ?pokemon ex:defense ?defense . }}
      OPTIONAL {{ ?pokemon ex:sp_attack ?spAttack . }}
      OPTIONAL {{ ?pokemon ex:sp_defense ?spDefense . }}
      OPTIONAL {{ ?pokemon ex:speed ?speed . }}
      OPTIONAL {{ 
        ?ability a ex:Ability ;
                 ex:possessedBy ?pokemon ;
                 ex:abilityName ?abilityName .
      }}
    }}
    GROUP BY ?id ?name ?type1 ?type2 ?hp ?attack ?defense ?spAttack ?spDefense ?speed
    ORDER BY ?name
    """
    
    data = execute_sparql_query(query)
    
    if not data["results"]["bindings"]:
        raise HTTPException(
            status_code=404, 
            detail=f"No forms found for Pokemon with ID {pokemon_id}"
        )
    
    # Collect all type2 values
    available_type2s = set()
    for binding in data["results"]["bindings"]:
        if "type2" in binding:
            available_type2s.add(extract_value_from_uri(binding["type2"]["value"]))
    
    # Parse all forms
    forms_dict = {}
    
    for binding in data["results"]["bindings"]:
        pokemon = parse_pokemon_from_binding(binding, include_stats=True, fetch_pokeapi=False)
        pokemon_name = pokemon["name"]
        
        if pokemon_name not in forms_dict:
            # Assign correct type2
            if len(pokemon["types"]) == 2:
                correct_type2 = get_correct_type2_for_form(
                    pokemon_name, 
                    list(available_type2s)
                )
                if correct_type2 and pokemon["types"][1] != correct_type2:
                    pokemon["types"] = [pokemon["types"][0], correct_type2]
            elif len(pokemon["types"]) == 1 and available_type2s:
                correct_type2 = get_correct_type2_for_form(
                    pokemon_name, 
                    list(available_type2s)
                )
                if correct_type2:
                    pokemon["types"].append(correct_type2)
            
            forms_dict[pokemon_name] = pokemon
    
    forms = list(forms_dict.values())
    
    # Get evolution chain and PokeAPI data for first form
    evolution_chain = get_evolution_chain_from_sparql(pokemon_id)
    
    if forms:
        try:
            poke_data = fetch_pokeapi_species_data(pokemon_id)
            if poke_data:
                forms[0]["height"] = poke_data["height"]
                forms[0]["weight"] = poke_data["weight"]
                forms[0]["category"] = poke_data["category"]
        except Exception as e:
            print(f"Failed to fetch PokeAPI data for Pokemon {pokemon_id}: {e}")
    
    # Add evolution chain and image URLs to each form
    all_forms = get_pokemon_forms_from_sparql(pokemon_id)
    for form in forms:
        form["evolutionChain"] = evolution_chain
        form["imageUrl"] = get_pokemon_image_url(pokemon_id, form["name"], all_forms)
    
    return forms


@app.get("/api/pokemon/{pokemon_id}/card")
def get_pokemon_card_by_id(pokemon_id: int):
    """Get lightweight Pokemon card data for display"""
    query = f"""
    SELECT ?id ?name ?type1 ?type2
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number ?id ;
               ex:name ?name .
      
      FILTER(?id = {pokemon_id})
      
      OPTIONAL {{ ?pokemon ex:type1 ?type1 . }}
      OPTIONAL {{ ?pokemon ex:type2 ?type2 . }}
    }}
    LIMIT 1
    """
    
    data = execute_sparql_query(query)
    
    if not data["results"]["bindings"]:
        raise HTTPException(
            status_code=404, 
            detail=f"Pokemon with ID {pokemon_id} not found"
        )
    
    binding = data["results"]["bindings"][0]
    pokemon = parse_pokemon_from_binding(binding)
    
    # Set image URL
    forms = get_pokemon_forms_from_sparql(pokemon_id)
    pokemon["imageUrl"] = get_pokemon_image_url(pokemon_id, pokemon["name"], forms)
    
    return pokemon


@app.get("/api/pokemon/type/{type_name}")
def get_pokemon_by_type(type_name: str):
    """Get all Pokemon of a specific type"""
    type_formatted = type_name.capitalize()
    
    query = f"""
    SELECT DISTINCT ?id ?name ?type1 ?type2
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number ?id ;
               ex:name ?name .
      
      {{ ?pokemon ex:type1 "{type_formatted}" . }}
      UNION
      {{ ?pokemon ex:type2 "{type_formatted}" . }}
      
      OPTIONAL {{ ?pokemon ex:type1 ?type1 . }}
      OPTIONAL {{ ?pokemon ex:type2 ?type2 . }}
    }}
    ORDER BY ?id
    LIMIT 100
    """
    
    data = execute_sparql_query(query)
    results = []
    
    for binding in data["results"]["bindings"]:
        try:
            pokemon = parse_pokemon_from_binding(binding)
            pokemon_id = pokemon["id"]
            forms = get_pokemon_forms_from_sparql(pokemon_id)
            pokemon["imageUrl"] = get_pokemon_image_url(pokemon_id, pokemon["name"], forms)
            results.append(pokemon)
        except Exception as e:
            print(f"Error parsing pokemon: {e}")
            continue
    
    return results


@app.get("/api/pokemon/evolution-chain/{pokemon_id}")
def get_evolution_chain_endpoint(pokemon_id: int):
    """Get evolution chain for a Pokemon"""
    chain_ids = get_evolution_chain_from_sparql(pokemon_id)
    
    pokemon_list = []
    for pid in chain_ids:
        try:
            pokemon = get_pokemon_by_id(pid)
            pokemon_list.append(pokemon)
        except:
            continue
    
    return pokemon_list


@app.get("/api/recommendations")
def get_recommendations(
    pokemon_id: Optional[int] = Query(None),
    limit: int = Query(default=5, le=20)
):
    """Get Pokemon recommendations based on type effectiveness - proxied to Recommender service"""
    
    if not pokemon_id:
        raise HTTPException(
            status_code=400, 
            detail="pokemon_id must be provided"
        )
    
    # Get the target Pokemon name first
    try:
        target = get_pokemon_by_id(pokemon_id)
        pokemon_name = target["name"]
    except:
        raise HTTPException(status_code=404, detail=f"Pokemon with ID {pokemon_id} not found")
    
    # Call the Recommender service
    try:
        response = requests.get(
            f"{RECOMMENDER_URL}/api/recommend",
            params={"name": pokemon_name, "limit": limit},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Recommender service error: {e}")
        # Fallback to empty recommendations
        return {
            "target": {"id": pokemon_id, "name": pokemon_name},
            "best": [],
            "worst": []
        }


@app.get("/api/stats")
def get_stats():
    """Get database statistics"""
    query = """
    SELECT (COUNT(DISTINCT ?pokemon) AS ?count)
    WHERE {
      ?pokemon a ex:Pokemon .
    }
    """
    
    data = execute_sparql_query(query)
    count = 0
    
    if data["results"]["bindings"]:
        count = int(data["results"]["bindings"][0]["count"]["value"])
    
    return {"totalPokemon": count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
