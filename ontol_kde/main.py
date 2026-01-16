from fastapi import FastAPI
import requests

FUSEKI_ENDPOINT = "http://localhost:3030/pokemon/sparql"

PREFIX = """
PREFIX ex: <http://example.org/>
"""

app = FastAPI()


def run_sparql(query: str):
    response = requests.get(
        FUSEKI_ENDPOINT,
        params={"query": query},
        headers={"Accept": "application/sparql+json"}
    )

    print("STATUS:", response.status_code)
    print("RAW RESPONSE:", response.text)

    response.raise_for_status()
    return response.json()



@app.get("/search")
def search_pokemon(q: str):
    query = PREFIX + f"""
    SELECT ?pokemon ?name
    WHERE {{
      GRAPH <http://example.org/pokemon> {{
        ?pokemon a ex:Pokemon ;
                 ex:name ?name .
        FILTER(CONTAINS(LCASE(?name), "{q.lower()}"))
      }}
    }}
    """

    data = run_sparql(query)

    results = []
    for b in data["results"]["bindings"]:
        uri = b["pokemon"]["value"]
        pid = uri.split("/")[-1]
        results.append({
            "id": int(pid),
            "name": b["name"]["value"]
        })

    return results


@app.get("/pokemon/{pid}/header")
def pokemon_header(pid: int):
    uri = f"http://example.org/pokemon/simple/{pid}"

    query = PREFIX + f"""
    SELECT ?name ?number ?generation
    WHERE {{
      GRAPH <http://example.org/pokemon> {{
        <{uri}> ex:name ?name ;
                 ex:number ?number ;
                 ex:generation ?generation .
      }}
    }}
    """

    data = run_sparql(query)
    if not data["results"]["bindings"]:
        return {}

    row = data["results"]["bindings"][0]
    return {
        "name": row["name"]["value"],
        "number": int(row["number"]["value"]),
        "generation": int(row["generation"]["value"])
    }


@app.get("/pokemon/{pid}/stats")
def pokemon_stats(pid: int):
    uri = f"http://example.org/pokemon/simple/{pid}"

    query = PREFIX + f"""
    SELECT ?hp ?attack ?defense ?spAttack ?spDefense ?speed ?total
    WHERE {{
      GRAPH <http://example.org/pokemon> {{
        <{uri}>
            ex:hp ?hp ;
            ex:attack ?attack ;
            ex:defense ?defense ;
            ex:sp_attack ?spAttack ;
            ex:sp_defense ?spDefense ;
            ex:speed ?speed ;
            ex:total ?total .
      }}
    }}
    """

    data = run_sparql(query)
    if not data["results"]["bindings"]:
        return {}

    r = data["results"]["bindings"][0]
    return {
        "hp": int(r["hp"]["value"]),
        "attack": int(r["attack"]["value"]),
        "defense": int(r["defense"]["value"]),
        "sp_attack": int(r["spAttack"]["value"]),
        "sp_defense": int(r["spDefense"]["value"]),
        "speed": int(r["speed"]["value"]),
        "total": int(r["total"]["value"])
    }
