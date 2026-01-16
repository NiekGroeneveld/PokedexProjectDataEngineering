"""Service for interacting with the PokeAPI external service"""
import requests
from typing import Dict

#Data not available in our RDF store, we fetch from PokeAPI, for compoleteness. It is basically simple data that is coupled to 1 single pokemon only.
#No difficult queries needed here.
def fetch_pokeapi_species_data(pokemon_id: int) -> Dict[str, any]:
    """Fetch height, weight, and category from PokeAPI
    
    Args:
        pokemon_id: The Pokemon's national dex number
        
    Returns:
        Dict with keys: height, weight, category
    """
    try:
        # Get species data for category
        species_response = requests.get(
            f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}", 
            timeout=5
        )
        if species_response.status_code == 200:
            species_data = species_response.json()
            
            # Get category (genus) from English entry
            category = "Pokemon"
            for genus in species_data.get("genera", []):
                if genus.get("language", {}).get("name") == "en":
                    category = genus.get("genus", "Pokemon")
                    break
            
            # Get Pokemon data for height/weight
            pokemon_response = requests.get(
                f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}", 
                timeout=5
            )
            if pokemon_response.status_code == 200:
                pokemon_data = pokemon_response.json()
                return {
                    "height": pokemon_data.get("height", 0),  # in decimeters
                    "weight": pokemon_data.get("weight", 0),  # in hectograms
                    "category": category
                }
    except Exception as e:
        print(f"PokeAPI fetch error for ID {pokemon_id}: {e}")
    
    return {"height": 0, "weight": 0, "category": "Pokemon"}
