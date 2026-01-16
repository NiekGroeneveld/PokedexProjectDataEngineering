from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import List, Optional
import os

app = FastAPI(title="Pokemon API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphDB endpoints - can be Fuseki or Blazegraph
GRAPHDB_ENDPOINT = os.getenv("GRAPHDB_ENDPOINT", "http://blazegraph:8080/bigdata/namespace/kb/sparql")

# SPARQL prefixes
PREFIXES = """
PREFIX ex: <http://example.org/>
PREFIX poke: <http://example.org/pokemon/>
PREFIX poke_simple: <http://example.org/pokemon/simple/>
"""

def run_sparql(query: str):
    """Execute SPARQL query against GraphDB"""
    try:
        response = requests.post(
            GRAPHDB_ENDPOINT,
            data=query,
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
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

# Global cache for Pokemon forms to avoid repeated SPARQL queries
_pokemon_forms_cache = {}

def is_base_form(pokemon_name: str) -> bool:
    """Determine if a Pokemon name is a base form (not a variant)"""
    form_keywords = ["Mega", "Gmax", "Gigantamax", "Primal", "Heat", "Wash", "Frost", "Fan", "Mow",
                     "Sandy", "Trash", "Attack", "Defense", "Speed", "Origin", "Sky", "Cloak",
                     "Alola", "Galar", "Hisui", "Paldea", "Blade", "Therian", "Resolute",
                     "White", "Black", "Unbound", "Aria", "Pirouette", "Shield", "Sword"]
    name_lower = pokemon_name.lower()
    return not any(keyword.lower() in name_lower for keyword in form_keywords)


def get_pokemon_forms_from_data(pokemon_id: int) -> list:
    """Get all forms for a Pokemon ID from the RDF data, sorted with base form first"""
    if pokemon_id in _pokemon_forms_cache:
        return _pokemon_forms_cache[pokemon_id]
    
    # Query all names for this Pokemon ID
    query = PREFIXES + f"""
    SELECT DISTINCT ?name ?type2
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number {pokemon_id} ;
               ex:name ?name .
      OPTIONAL {{ ?pokemon ex:type2 ?type2 . }}
    }}
    ORDER BY ?name
    """
    
    data = run_sparql(query)
    forms = []
    
    for binding in data["results"]["bindings"]:
        raw_name = binding.get("name", {}).get("value", "")
        formatted_name = format_pokemon_name(raw_name)
        
        # Extract type2 if present
        type2 = None
        if "type2" in binding:
            type2_value = binding["type2"]["value"]
            if "/" in type2_value:
                type2_value = type2_value.split("/")[-1]
            type2 = type2_value
        
        # Add form if not already in list (handle duplicates from cartesian products)
        if not any(f["name"] == formatted_name for f in forms):
            forms.append({
                "name": formatted_name,
                "type2": type2,
                "is_base": is_base_form(formatted_name)
            })
    
    # Sort: base forms first, then alphabetically
    forms.sort(key=lambda x: (not x["is_base"], x["name"]))
    
    _pokemon_forms_cache[pokemon_id] = forms
    return forms


def get_pokemon_com_image_url(pokemon_id: int, pokemon_name: str = None) -> str:
    """Get Pokemon image URL from pokemon.com with form-specific suffixes based on data"""
    # Base URL pattern
    base_url = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{pokemon_id:03d}"
    
    if not pokemon_name:
        return f"{base_url}.png"
    
    # Get all forms for this Pokemon from the data
    forms = get_pokemon_forms_from_data(pokemon_id)
    
    # If only one form, it's the base form
    if len(forms) <= 1:
        return f"{base_url}.png"
    
    # Find which form this is (by matching the name)
    for idx, form in enumerate(forms):
        if form["name"] == pokemon_name:
            # First form (index 0) is base, subsequent forms get _f2, _f3, etc.
            if idx == 0:
                return f"{base_url}.png"
            else:
                return f"{base_url}_f{idx + 1}.png"
    
    # Fallback to base form
    return f"{base_url}.png"


def get_pokeapi_image_url(pokemon_id: int, pokemon_name: str = None) -> str:
    """Wrapper that uses pokemon.com URLs"""
    return get_pokemon_com_image_url(pokemon_id, pokemon_name)

def get_pokeapi_data(pokemon_id: int) -> dict:
    """Fetch height, weight, and category from PokeAPI"""
    try:
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}", timeout=5)
        if response.status_code == 200:
            species_data = response.json()
            # Get category (genus) from English entry
            category = "Pokemon"
            for genus in species_data.get("genera", []):
                if genus.get("language", {}).get("name") == "en":
                    category = genus.get("genus", "Pokemon")
                    break
            
            # Get Pokemon data for height/weight
            pokemon_response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}", timeout=5)
            if pokemon_response.status_code == 200:
                pokemon_data = pokemon_response.json()
                return {
                    "height": pokemon_data.get("height", 0),  # in decimeters
                    "weight": pokemon_data.get("weight", 0),  # in hectograms
                    "category": category
                }
    except:
        pass
    
    return {"height": 0, "weight": 0, "category": "Pokemon"}

def format_pokemon_name(name: str) -> str:
    """Format Pokemon name to handle size variations and duplicate base names"""
    # Remove duplicate base name prefix patterns:
    # "CharizardMega Charizard X" -> "Mega Charizard X"
    # "RotomHeat Rotom" -> "Heat Rotom"
    # "WormadamPlant Cloak" -> "Wormadam (Plant Cloak)"
    
    # Special handling for Cloak forms (Wormadam, Burmy)
    if "Cloak" in name:
        # Pattern: WormadamPlant Cloak -> Wormadam (Plant Cloak)
        if "Wormadam" in name or "Burmy" in name:
            base = "Wormadam" if "Wormadam" in name else "Burmy"
            # Extract the cloak type
            cloak_part = name.replace(base, "").strip()
            if cloak_part and cloak_part != "Cloak":
                return f"{base} ({cloak_part})"
            return base
    
    # Special handling for Rotom forms (RotomHeat Rotom -> Heat Rotom)
    if "Rotom" in name and name != "Rotom":
        # Pattern: RotomXXX Rotom -> XXX Rotom
        if name.endswith(" Rotom"):
            prefix = name.replace(" Rotom", "").replace("Rotom", "").strip()
            if prefix:
                name = f"{prefix} Rotom"
    
    # Special handling for Mega/Gmax/Primal forms
    # "CharizardMega Charizard X" -> "Mega Charizard X"
    elif "Mega" in name or "Gmax" in name or "Gigantamax" in name or "Primal" in name:
        # Find the base name by looking at the repeated part
        parts = name.split()
        if len(parts) >= 2:
            # Extract the form identifier (Mega, Gmax, etc.)
            form_keywords = ["Mega", "Gmax", "Gigantamax", "Primal"]
            for keyword in form_keywords:
                if keyword in name:
                    # Pattern: BaseMega Base X -> Mega Base X
                    if parts[0].replace(keyword, "") and any(parts[0].replace(keyword, "") in p for p in parts[1:]):
                        # Remove the concatenated first word
                        base = parts[0].replace(keyword, "")
                        rest = ' '.join(parts[1:])
                        name = f"{keyword} {rest}"
                        break
    
    # Handle size variations (e.g., PumpkabooAverage Size -> Pumpkaboo (Average Size))
    size_keywords = ["Average Size", "Large Size", "Small Size", "Super Size"]
    for size in size_keywords:
        size_no_space = size.replace(" ", "")
        if size_no_space in name:
            base_name = name.replace(size_no_space, "").replace(size, "").strip()
            return f"{base_name} ({size})"
    
    return name

def get_correct_type2_for_form(pokemon_name: str, available_types: list) -> str:
    """
    Determine correct type2 based on Pokemon form name.
    Some Pokemon have multiple forms with different types stored in RDF.
    This function uses domain knowledge to assign the correct type.
    """
    # Mega Charizard X is Fire/Dragon
    if "Mega Charizard X" in pokemon_name:
        if "Dragon" in available_types:
            return "Dragon"
    # Charizard and Mega Charizard Y are Fire/Flying
    elif "Charizard" in pokemon_name:
        if "Flying" in available_types:
            return "Flying"
    
    # Rotom forms have different secondary types
    if "Rotom" in pokemon_name:
        if "Heat" in pokemon_name and "Fire" in available_types:
            return "Fire"
        elif "Wash" in pokemon_name and "Water" in available_types:
            return "Water"
        elif "Frost" in pokemon_name and "Ice" in available_types:
            return "Ice"
        elif "Fan" in pokemon_name and "Flying" in available_types:
            return "Flying"
        elif "Mow" in pokemon_name and "Grass" in available_types:
            return "Grass"
        # Base Rotom is Electric/Ghost
        elif "Ghost" in available_types:
            return "Ghost"
    
    # If no special case, return the first available type
    return available_types[0] if available_types else None

def parse_pokemon_from_sparql(binding: dict, include_stats: bool = False, fetch_pokeapi: bool = False) -> dict:
    """Parse SPARQL binding into Pokemon object"""
    pokemon_id = int(binding.get("id", {}).get("value", 0))
    raw_name = binding.get("name", {}).get("value", "Unknown")
    formatted_name = format_pokemon_name(raw_name)
    
    # Only fetch PokeAPI data for detail views, not for lists
    if fetch_pokeapi:
        pokeapi_data = get_pokeapi_data(pokemon_id)
    else:
        pokeapi_data = {"height": 0, "weight": 0, "category": "Pokemon"}
    
    pokemon = {
        "id": pokemon_id,
        "name": formatted_name,
        "types": [],
        "imageUrl": get_pokeapi_image_url(pokemon_id, formatted_name),
        "height": pokeapi_data["height"],
        "weight": pokeapi_data["weight"],
        "abilities": [],
        "category": pokeapi_data["category"],
        "evolutionChain": [],
    }
    
    # Parse types - extract just the type name from URI if needed
    if "type1" in binding:
        type1_value = binding["type1"]["value"]
        # Extract type name from URI (e.g., http://example.org/types/Water -> Water)
        if "/" in type1_value:
            type1_value = type1_value.split("/")[-1]
        pokemon["types"].append(type1_value)
    if "type2" in binding:
        type2_value = binding["type2"]["value"]
        # Extract type name from URI
        if "/" in type2_value:
            type2_value = type2_value.split("/")[-1]
        pokemon["types"].append(type2_value)
    
    # Parse abilities - extract from URI or comma-separated list
    if "abilities" in binding:
        abilities_str = binding["abilities"]["value"]
        abilities = []
        for a in abilities_str.split(","):
            a = a.strip()
            if a:
                # Extract ability name from URI if needed
                if "/" in a:
                    a = a.split("/")[-1]
                # Replace underscores with spaces and title case
                a = a.replace("_", " ").replace("-", " ").title()
                abilities.append(a)
        pokemon["abilities"] = abilities
    
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


@app.get("/")
def root():
    """API health check"""
    return {"status": "ok", "message": "Pokemon API is running"}


@app.get("/api/pokemon/search")
def get_search_list(limit: int = Query(default=1000, le=2000)):
    """Lightweight endpoint for search - returns all distinct forms with correct types from data"""
    query = PREFIXES + f"""
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
    
    data = run_sparql(query)
    
    # First pass: collect all forms per Pokemon ID to build the form order
    pokemon_forms_order = {}  # pokemon_id -> list of formatted names in order
    
    for binding in data["results"]["bindings"]:
        pokemon_id = int(binding.get("id", {}).get("value", 0))
        pokemon_name = binding.get("name", {}).get("value", "Unknown")
        formatted_name = format_pokemon_name(pokemon_name)
        
        if pokemon_id not in pokemon_forms_order:
            pokemon_forms_order[pokemon_id] = []
        
        # Add if not already in list
        if formatted_name not in pokemon_forms_order[pokemon_id]:
            pokemon_forms_order[pokemon_id].append(formatted_name)
    
    # Sort each Pokemon's forms: base first, then alphabetically
    # Also populate the cache for get_pokemon_forms_from_data
    for pokemon_id in pokemon_forms_order:
        forms = pokemon_forms_order[pokemon_id]
        forms.sort(key=lambda name: (not is_base_form(name), name))
        
        # Populate cache in the format expected by get_pokemon_forms_from_data
        _pokemon_forms_cache[pokemon_id] = [{"name": name, "type2": None, "is_base": is_base_form(name)} for name in forms]
    
    # Second pass: group by (id, formatted_name) to collect type data per form
    form_data = {}
    
    for binding in data["results"]["bindings"]:
        pokemon_id = int(binding.get("id", {}).get("value", 0))
        pokemon_name = binding.get("name", {}).get("value", "Unknown")
        formatted_name = format_pokemon_name(pokemon_name)
        
        key = (pokemon_id, formatted_name)
        
        if key not in form_data:
            form_data[key] = {
                "id": pokemon_id,
                "name": formatted_name,
                "type1": None,
                "type2s": set()
            }
        
        # Extract type1 (should be consistent for all rows)
        if "type1" in binding and not form_data[key]["type1"]:
            type1_value = binding["type1"]["value"]
            if "/" in type1_value:
                type1_value = type1_value.split("/")[-1]
            form_data[key]["type1"] = type1_value
        
        # Collect all type2 values (may have multiple due to cartesian product)
        if "type2" in binding:
            type2_value = binding["type2"]["value"]
            if "/" in type2_value:
                type2_value = type2_value.split("/")[-1]
            form_data[key]["type2s"].add(type2_value)
    
    # Build results - match each form to its correct type2 from the data
    results = []
    for key, form_info in form_data.items():
        types = []
        if form_info["type1"]:
            types.append(form_info["type1"])
        
        # For type2, use the data directly - match form name to type2
        if form_info["type2s"]:
            # If only one type2, use it
            if len(form_info["type2s"]) == 1:
                types.append(list(form_info["type2s"])[0])
            else:
                # Multiple type2s due to cartesian product - use domain logic to pick correct one
                correct_type2 = get_correct_type2_for_form(form_info["name"], list(form_info["type2s"]))
                if correct_type2:
                    types.append(correct_type2)
        
        # Generate image URL based on form order
        pokemon_id = form_info["id"]
        pokemon_name = form_info["name"]
        form_order = pokemon_forms_order[pokemon_id]
        form_index = form_order.index(pokemon_name) if pokemon_name in form_order else 0
        
        base_url = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{pokemon_id:03d}"
        if form_index == 0:
            imageUrl = f"{base_url}.png"
        else:
            imageUrl = f"{base_url}_f{form_index + 1}.png"
        
        results.append({
            "id": form_info["id"],
            "name": form_info["name"],
            "types": types,
            "imageUrl": imageUrl
        })
    
    # Sort by ID, then by form order (base first, then alphabetically)
    def sort_key(item):
        pokemon_id = item["id"]
        pokemon_name = item["name"]
        form_order = pokemon_forms_order.get(pokemon_id, [])
        form_index = form_order.index(pokemon_name) if pokemon_name in form_order else 999
        return (pokemon_id, form_index)
    
    results.sort(key=sort_key)
    
    return results


@app.get("/api/pokemon")
def get_all_pokemon(limit: int = Query(default=151, le=1000), offset: int = Query(default=0, ge=0)):
    """Get all Pokemon with pagination - returns only base forms"""
    # Get unique Pokemon IDs first
    id_query = PREFIXES + f"""
    SELECT DISTINCT ?id
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number ?id .
    }}
    ORDER BY ?id
    OFFSET {offset}
    LIMIT {limit}
    """
    
    id_data = run_sparql(id_query)
    results = []
    
    # For each unique ID, get the first (alphabetically) name entry that's not a special form
    for id_binding in id_data["results"]["bindings"]:
        pokemon_id = int(id_binding["id"]["value"])
        
        # Query for this specific ID, ordered by name to get consistent results
        detail_query = PREFIXES + f"""
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
        
        try:
            detail_data = run_sparql(detail_query)
            if detail_data["results"]["bindings"]:
                binding = detail_data["results"]["bindings"][0]
                pokemon_name = binding.get("name", {}).get("value", "Unknown")
                
                # Skip special forms
                if any(keyword in pokemon_name for keyword in ["Mega", "Gmax", "Gigantamax", "Primal"]):
                    continue
                
                pokemon = parse_pokemon_from_sparql(binding)
                results.append(pokemon)
        except Exception as e:
            print(f"Error parsing pokemon: {e}")
            continue
    
    return results


@app.get("/api/pokemon/{pokemon_id}")
def get_pokemon_by_id(pokemon_id: int):
    """Get specific Pokemon by ID with full details including stats"""
    query = PREFIXES + f"""
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
    """
    
    data = run_sparql(query)
    
    if not data["results"]["bindings"]:
        raise HTTPException(status_code=404, detail=f"Pokemon with ID {pokemon_id} not found")
    
    binding = data["results"]["bindings"][0]
    pokemon = parse_pokemon_from_sparql(binding, include_stats=True, fetch_pokeapi=True)
    
    # Get evolution chain
    evolution_chain = get_evolution_chain(pokemon_id)
    pokemon["evolutionChain"] = evolution_chain
    
    return pokemon


@app.get("/api/pokemon/name/{pokemon_name}")
def get_pokemon_by_name(pokemon_name: str):
    """Get specific Pokemon by formatted name with full details including stats"""
    # URL decode the name (spaces come as %20)
    from urllib.parse import unquote
    pokemon_name = unquote(pokemon_name)
    
    # Fetch all Pokemon with their names and find the one that matches after formatting
    query = PREFIXES + f"""
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
    
    data = run_sparql(query)
    
    # Collect all type2 values for matching Pokemon ID and formatted name
    form_data = {}
    pokemon_id = None
    
    for binding in data["results"]["bindings"]:
        raw_name = binding.get("name", {}).get("value", "")
        formatted_name = format_pokemon_name(raw_name)
        
        if formatted_name == pokemon_name:
            current_id = int(binding.get("id", {}).get("value", 0))
            if pokemon_id is None:
                pokemon_id = current_id
            
            key = (current_id, formatted_name)
            if key not in form_data:
                form_data[key] = {
                    "binding": binding,
                    "type2s": set()
                }
            
            # Collect all type2 values
            if "type2" in binding:
                type2_value = binding["type2"]["value"]
                if "/" in type2_value:
                    type2_value = type2_value.split("/")[-1]
                form_data[key]["type2s"].add(type2_value)
    
    if not form_data:
        raise HTTPException(status_code=404, detail=f"Pokemon with name '{pokemon_name}' not found")
    
    # Get the first (should be only one) matching form
    key = list(form_data.keys())[0]
    form_info = form_data[key]
    matching_binding = form_info["binding"]
    
    # Parse the pokemon but fix the types and image URL
    pokemon = parse_pokemon_from_sparql(matching_binding, include_stats=True, fetch_pokeapi=True)
    
    # Fix types using the same logic as search endpoint
    types = []
    if "type1" in matching_binding:
        type1_value = matching_binding["type1"]["value"]
        if "/" in type1_value:
            type1_value = type1_value.split("/")[-1]
        types.append(type1_value)
    
    # Get correct type2 from the collected set
    if form_info["type2s"]:
        if len(form_info["type2s"]) == 1:
            types.append(list(form_info["type2s"])[0])
        else:
            # Multiple type2s - use domain logic
            correct_type2 = get_correct_type2_for_form(pokemon_name, list(form_info["type2s"]))
            if correct_type2:
                types.append(correct_type2)
    
    pokemon["types"] = types
    
    # Fix image URL using the same logic as search endpoint
    # Get all forms for this Pokemon to determine correct image suffix
    forms = get_pokemon_forms_from_data(pokemon_id)
    form_index = next((i for i, f in enumerate(forms) if f["name"] == pokemon_name), 0)
    
    base_url = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{pokemon_id:03d}"
    if form_index == 0:
        pokemon["imageUrl"] = f"{base_url}.png"
    else:
        pokemon["imageUrl"] = f"{base_url}_f{form_index + 1}.png"
    
    # Get evolution chain using the Pokemon ID
    evolution_chain = get_evolution_chain(pokemon_id)
    pokemon["evolutionChain"] = evolution_chain
    
    return pokemon


@app.get("/api/pokemon/{pokemon_id}/forms")
def get_pokemon_forms_by_id(pokemon_id: int):
    """Get all forms of a Pokemon by ID (base, Mega, Gigantamax, regional variants, etc.)"""
    query = PREFIXES + f"""
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
    
    data = run_sparql(query)
    
    if not data["results"]["bindings"]:
        raise HTTPException(status_code=404, detail=f"No forms found for Pokemon with ID {pokemon_id}")
    
    # Collect all type2 values for this Pokemon
    available_type2s = set()
    for binding in data["results"]["bindings"]:
        if "type2" in binding:
            type2_value = binding["type2"]["value"]
            if "/" in type2_value:
                type2_value = type2_value.split("/")[-1]
            available_type2s.add(type2_value)
    
    # Parse all forms and assign correct types
    forms_dict = {}  # Use dict to deduplicate by name
    
    for binding in data["results"]["bindings"]:
        pokemon = parse_pokemon_from_sparql(binding, include_stats=True, fetch_pokeapi=False)
        pokemon_name = pokemon["name"]
        
        # If we haven't seen this form yet, or if this one has better type assignment
        if pokemon_name not in forms_dict:
            # Assign the correct type2 based on form name
            if len(pokemon["types"]) == 2:
                # Already has type2, check if it's correct
                correct_type2 = get_correct_type2_for_form(pokemon_name, list(available_type2s))
                if correct_type2 and pokemon["types"][1] != correct_type2:
                    # Replace with correct type2
                    pokemon["types"] = [pokemon["types"][0], correct_type2]
            elif len(pokemon["types"]) == 1 and available_type2s:
                # Has only type1, need to add correct type2
                correct_type2 = get_correct_type2_for_form(pokemon_name, list(available_type2s))
                if correct_type2:
                    pokemon["types"].append(correct_type2)
            
            forms_dict[pokemon_name] = pokemon
    
    forms = list(forms_dict.values())
    
    # Get evolution chain (same for all forms)
    evolution_chain = get_evolution_chain(pokemon_id)
    
    # Fetch PokeAPI data only for the first form (base form)
    if forms:
        try:
            poke_data = get_pokeapi_data(pokemon_id)
            if poke_data:
                forms[0]["height"] = poke_data["height"]
                forms[0]["weight"] = poke_data["weight"]
                forms[0]["category"] = poke_data["category"]
        except Exception as e:
            print(f"Failed to fetch PokeAPI data for Pokemon {pokemon_id}: {e}")
    
    # Add evolution chain to each form
    for form in forms:
        form["evolutionChain"] = evolution_chain
    
    return forms


@app.get("/api/pokemon/{pokemon_id}/card")
def get_pokemon_card_by_id(pokemon_id: int):
    """Get minimal Pokemon data for card display (name, types, image only)"""
    query = PREFIXES + f"""
    SELECT DISTINCT ?id ?name ?type1 ?type2
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
    
    data = run_sparql(query)
    
    if not data["results"]["bindings"]:
        raise HTTPException(status_code=404, detail=f"Pokemon with ID {pokemon_id} not found")
    
    binding = data["results"]["bindings"][0]
    pokemon_id = int(binding.get("id", {}).get("value", 0))
    
    # Extract types
    types = []
    if "type1" in binding:
        type1_value = binding["type1"]["value"]
        if "/" in type1_value:
            type1_value = type1_value.split("/")[-1]
        types.append(type1_value)
    if "type2" in binding:
        type2_value = binding["type2"]["value"]
        if "/" in type2_value:
            type2_value = type2_value.split("/")[-1]
        types.append(type2_value)
    
    pokemon_name = binding.get("name", {}).get("value", "Unknown")
    formatted_name = format_pokemon_name(pokemon_name)
    
    return {
        "id": pokemon_id,
        "name": formatted_name,
        "types": types,
        "imageUrl": get_pokeapi_image_url(pokemon_id, formatted_name)
    }


@app.get("/api/pokemon/search")
def search_pokemon_by_name(name: str = Query(..., min_length=1)):
    """Search Pokemon by name (partial match, case-insensitive)"""
    query = PREFIXES + f"""
    SELECT DISTINCT ?id ?name ?type1 ?type2
    WHERE {{
      ?pokemon a ex:Pokemon ;
               ex:number ?id ;
               ex:name ?name .
      
      FILTER(CONTAINS(LCASE(?name), "{name.lower()}"))
      
      OPTIONAL {{ ?pokemon ex:type1 ?type1 . }}
      OPTIONAL {{ ?pokemon ex:type2 ?type2 . }}
    }}
    ORDER BY ?id
    LIMIT 20
    """
    
    data = run_sparql(query)
    results = []
    
    for binding in data["results"]["bindings"]:
        try:
            pokemon = parse_pokemon_from_sparql(binding)
            results.append(pokemon)
        except Exception as e:
            print(f"Error parsing pokemon: {e}")
            continue
    
    return results


@app.get("/api/pokemon/type/{type_name}")
def get_pokemon_by_type(type_name: str):
    """Get all Pokemon of a specific type"""
    # Capitalize first letter to match ontology format
    type_formatted = type_name.capitalize()
    
    query = PREFIXES + f"""
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
    
    data = run_sparql(query)
    results = []
    
    for binding in data["results"]["bindings"]:
        try:
            pokemon = parse_pokemon_from_sparql(binding)
            results.append(pokemon)
        except Exception as e:
            print(f"Error parsing pokemon: {e}")
            continue
    
    return results


def get_evolution_chain(pokemon_id: int) -> List[int]:
    """Get evolution chain for a Pokemon"""
    # Query to find all Pokemon in the evolution chain
    # We'll use a recursive approach: find base, then find all evolutions
    query = PREFIXES + f"""
    SELECT DISTINCT ?id
    WHERE {{
      # Start from the current Pokemon
      {{
        poke_simple:{pokemon_id} ex:evolvesTo* ?pokemon .
        ?pokemon ex:number ?id .
      }}
      UNION
      {{
        ?base ex:evolvesTo* poke_simple:{pokemon_id} .
        ?base ex:evolvesTo* ?pokemon .
        ?pokemon ex:number ?id .
      }}
    }}
    ORDER BY ?id
    """
    
    try:
        data = run_sparql(query)
        chain = set()
        
        for binding in data["results"]["bindings"]:
            chain.add(int(binding["id"]["value"]))
        
        # Always include the current Pokemon
        chain.add(pokemon_id)
        
        return sorted(list(chain))
    except Exception as e:
        print(f"Evolution chain error: {e}")
        return [pokemon_id]


@app.get("/api/pokemon/evolution-chain/{pokemon_id}")
def get_evolution_chain_endpoint(pokemon_id: int):
    """Get evolution chain for a Pokemon"""
    chain_ids = get_evolution_chain(pokemon_id)
    
    # Get full Pokemon data for each in the chain
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
    name: Optional[str] = Query(None),
    limit: int = Query(default=5, le=20)
):
    """Get Pokemon recommendations based on type effectiveness"""
    
    # If name provided, find the Pokemon ID
    if name and not pokemon_id:
        search_results = search_pokemon_by_name(name)
        if not search_results:
            raise HTTPException(status_code=404, detail=f"Pokemon '{name}' not found")
        pokemon_id = search_results[0]["id"]
    
    if not pokemon_id:
        raise HTTPException(status_code=400, detail="Either pokemon_id or name must be provided")
    
    # Get the target Pokemon to find its types
    target = get_pokemon_by_id(pokemon_id)
    
    # Query for Pokemon that are strong against this Pokemon (weakTo)
    weak_to_query = PREFIXES + f"""
    SELECT ?candId (SAMPLE(?candName) AS ?name) (COUNT(?type) AS ?score)
    WHERE {{
      BIND(poke_simple:{pokemon_id} AS ?target)
      ?target ex:weakTo ?type .
      
      ?cand a ex:Pokemon ;
            ex:number ?candId ;
            ex:name ?candName .
      
      {{ ?cand ex:type1 ?type . }}
      UNION
      {{ ?cand ex:type2 ?type . }}
      
      FILTER(?cand != ?target)
    }}
    GROUP BY ?candId
    ORDER BY DESC(?score) ASC(?candId)
    LIMIT {limit}
    """
    
    # Query for Pokemon that this Pokemon is strong against (resistantTo)
    resistant_to_query = PREFIXES + f"""
    SELECT ?candId (SAMPLE(?candName) AS ?name) (COUNT(?type) AS ?score)
    WHERE {{
      BIND(poke_simple:{pokemon_id} AS ?target)
      ?target ex:resistantTo ?type .
      
      ?cand a ex:Pokemon ;
            ex:number ?candId ;
            ex:name ?candName .
      
      {{ ?cand ex:type1 ?type . }}
      UNION
      {{ ?cand ex:type2 ?type . }}
      
      FILTER(?cand != ?target)
    }}
    GROUP BY ?candId
    ORDER BY DESC(?score) ASC(?candId)
    LIMIT {limit}
    """
    
    try:
        best_data = run_sparql(weak_to_query)
        worst_data = run_sparql(resistant_to_query)
        
        best = [
            {
                "id": int(b["candId"]["value"]),
                "name": b["name"]["value"],
                "score": int(b["score"]["value"])
            }
            for b in best_data["results"]["bindings"]
        ]
        
        worst = [
            {
                "id": int(b["candId"]["value"]),
                "name": b["name"]["value"],
                "score": int(b["score"]["value"])
            }
            for b in worst_data["results"]["bindings"]
        ]
        
        return {
            "target": {
                "id": target["id"],
                "name": target["name"]
            },
            "best": best,
            "worst": worst
        }
    except Exception as e:
        print(f"Recommendation error: {e}")
        return {
            "target": {
                "id": target["id"],
                "name": target["name"]
            },
            "best": [],
            "worst": []
        }


@app.get("/api/stats")
def get_stats():
    """Get database statistics"""
    query = PREFIXES + """
    SELECT (COUNT(DISTINCT ?pokemon) AS ?count)
    WHERE {
      ?pokemon a ex:Pokemon .
    }
    """
    
    data = run_sparql(query)
    count = 0
    
    if data["results"]["bindings"]:
        count = int(data["results"]["bindings"][0]["count"]["value"])
    
    return {"totalPokemon": count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
