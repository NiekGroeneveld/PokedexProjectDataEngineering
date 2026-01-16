"""Configuration settings for the Pokemon API"""
import os

# GraphDB endpoints - can be Fuseki or Blazegraph
GRAPHDB_ENDPOINT = os.getenv(
    "GRAPHDB_ENDPOINT", 
    "http://blazegraph:8080/bigdata/namespace/kb/sparql"
)

# SPARQL prefixes used across all queries
SPARQL_PREFIXES = """
PREFIX ex: <http://example.org/>
PREFIX poke: <http://example.org/pokemon/>
PREFIX poke_simple: <http://example.org/pokemon/simple/>
"""

# CORS settings
CORS_ORIGINS = ["*"]  # In production, specify exact origins
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# API settings
API_TITLE = "Pokemon API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "FastAPI backend for Pokemon data"

# External search for Images
POKEMON_COM_IMAGE_BASE_URL = "https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full"
RECOMMENDER_URL = os.getenv("RECOMMENDER_URL", "http://localhost:3001")
