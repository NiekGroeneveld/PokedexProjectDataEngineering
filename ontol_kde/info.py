import requests
import rdflib

url = "https://pokeapi.co/api/v2/pokemon/pikachu"
data = requests.get(url).json()

# print(data["name"])        # pikachu
# print(data["id"])          # 25


from rdflib import Namespace

EX = Namespace("http://example.org/pokemon/")

pikachu_uri = EX.Pikachu


from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD

g = Graph()
g.parse(r"C:\Users\LENOVO\OneDrive\Documents\UU Master's Data Science\Period 2\Knowledge and Data Engineering - INFOMKDE\Project\ontol_kde\ontol_kde\global_turtle_data\pokemon_abilities_aligned.ttl")
g.parse(r"C:\Users\LENOVO\OneDrive\Documents\UU Master's Data Science\Period 2\Knowledge and Data Engineering - INFOMKDE\Project\ontol_kde\ontol_kde\global_turtle_data\pokemon_simple.ttl")
g.parse(r"C:\Users\LENOVO\OneDrive\Documents\UU Master's Data Science\Period 2\Knowledge and Data Engineering - INFOMKDE\Project\ontol_kde\ontol_kde\global_turtle_data\pokemon_evolution_links.ttl")
g.parse(r"C:\Users\LENOVO\OneDrive\Documents\UU Master's Data Science\Period 2\Knowledge and Data Engineering - INFOMKDE\Project\ontol_kde\ontol_kde\global_turtle_data\pokemon_type_effectiveness_aligned.ttl")

import requests
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

# Namespaces
POKEMON = Namespace("http://example.org/pokemon/")
EX = Namespace("http://example.org/ontology/")

# Create graph
g = Graph()
g.bind("pokemon", POKEMON)
g.bind("ex", EX)

# Step 1: find total number of Pokemon
count_url = "https://pokeapi.co/api/v2/pokemon?limit=1"
total_pokemon = requests.get(count_url).json()["count"]

print(f"Total Pokemon found: {total_pokemon}")

# Step 2: loop over ALL Pokemon
import time

for i in range(1, total_pokemon + 1):
    url = f"https://pokeapi.co/api/v2/pokemon/{i}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Retrying Pokemon ID {i}")
        time.sleep(2)
        response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed Pokemon ID {i}")
        continue

    data = response.json()
    ...
    
    time.sleep(0.2)  # time-lag so that API pull request doesnt crash

    name = data["name"]

    pokemon_uri = URIRef(POKEMON[name])

    # Declare Pokemon instance
    g.add((pokemon_uri, RDF.type, EX.Pokemon))
    g.add((pokemon_uri, EX.name, Literal(name, datatype=XSD.string)))

    # Add stats
    for stat in data["stats"]:
        stat_name = stat["stat"]["name"].replace("-", "_")
        stat_value = stat["base_stat"]

        g.add((
            pokemon_uri,
            EX[stat_name],
            Literal(stat_value, datatype=XSD.integer)
        ))

    if i % 50 == 0:
        print(f"Processed {i}/{total_pokemon}")

# Step 3: save Turtle file
output_file = "pokemon_stats_all.ttl"
g.serialize(destination=output_file, format="turtle")

print(f"RDF saved to {output_file}")
print("Total triples:", len(g))

print("Done")

