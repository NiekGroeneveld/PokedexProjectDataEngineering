Files Used

Core Data Files used are-

pokemon_simple.ttl
pokemon_evolution_links.ttl
pokemon_abilities_aligned.ttl
pokemon_type_effectiveness_aligned.ttl
--------------------------------------------
Ontology File

pokemon_ontology.ttl

---------------------------------------

Core Ontology Concepts

-> Classes

The main classes defined in the ontology are:

* ex:Pokemon
* ex:PokemonType
* ex:Ability
---------------------------------------
-> Evolution

The evolution model uses:

* ex:evolvesTo (from Pokémon to Pokémon)
* ex:evolvesFrom (defined as the inverse of ex:evolvesTo)

This supports querying for previous evolutions, next evolutions, and full evolution chains using SPARQL property paths.
---------------------------------------
-> Types

Pokémon types are modeled using:

* ex:type1
* ex:type2
* ex:hasType (as a super-property)

This allows inference over mono-type and dual-type Pokémon and enables type-based filtering.
---------------------------------------
-> Abilities

Abilities are modeled using:

* ex:possessedBy (from Ability to Pokémon)
* ex:hasAbility (defined as the inverse property)

This allows abilities to be queried from either direction.
---------------------------------------
-> Weaknesses and Resistances

The ontology models weaknesses and resistances using:

* ex:weakTo
* ex:resistantTo
* Damage multiplier properties such as ex:against_fire, ex:against_water, and others


---------------------------------------
-> Inference Examples

The ontology supports several types of inference, including:

* Inferring previous evolutions using inverse properties
* Inferring full evolution chains using transitive SPARQL paths
* Inferring Pokémon abilities through inverse relationships
* Grouping Pokémon by type or weakness using object properties

---------------------------------------

-> Loading into Blazegraph

All files should be loaded into the same Blazegraph namespace, preferably using triples mode.

The recommended load order is:

1. pokemon_simple.ttl
2. pokemon_evolution_links.ttl
3. pokemon_abilities_aligned.ttl
4. pokemon_type_effectiveness_aligned.ttl
5. pokemon_ontology.ttl

RDFS or OWL inference should be enabled.

---------------------------------------

-> Example Queries 

You can query for:

* The next evolution of a Pokémon
* The previous evolution of a Pokémon
* All abilities of a Pokémon
* The weaknesses of a Pokémon

Example Queries

#Next evolution

SELECT ?next WHERE {
  poke_simple:1 ex:evolvesTo ?next .
}


#Previous evolution

SELECT ?prev WHERE {
  ?prev ex:evolvesTo poke_simple:2 .
}


#Abilities

SELECT ?a WHERE {
  poke_simple:25 ex:hasAbility ?a .
}


#Weaknesses

SELECT ?t WHERE {
  poke_simple:6 ex:weakTo ?t .
}


