#!/usr/bin/env bash
set -euo pipefail

ENDPOINT="http://localhost:9999/bigdata/namespace/kb/sparql"

FILES=(
  "pokemon_simple.ttl"
  "pokemon_evolution_links.ttl"
  "pokemon_abilities_aligned.ttl"
  "pokemon_type_effectiveness_aligned.ttl"
  "poke_ontology.ttl"
)

for f in "${FILES[@]}"
do
  echo "Loading $f..."
  curl -X POST -H "Content-Type: text/turtle" --data-binary "@$f" "$ENDPOINT"
done

echo "Done."
