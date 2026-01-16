import express from "express";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

// Blazegraph endpoint
const SPARQL_ENDPOINT = process.env.GRAPHDB_ENDPOINT || "http://localhost:9999/bigdata/namespace/kb/sparql";

const esc = (s) => String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"');

//send query abd receive resulstt
async function sparql(query) {
  const res = await fetch(SPARQL_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/sparql-query",
      Accept: "application/sparql-results+json",
    },
    body: query,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// Fixed prefixes that are used in the queries
const PREFIXES = `
PREFIX ex: <http://example.org/>
PREFIX poke_simple: <http://example.org/pokemon/simple/>
`;

// turns data into array rows
function rows(data, mapper) {
  return data.results.bindings.map(mapper);
}

// Function + query
async function findPokemonByNameLike(name, limit = 1) {
  const q = `
${PREFIXES}
SELECT ?id (SAMPLE(?name) AS ?name)
WHERE {
  ?p a ex:Pokemon ;
     ex:number ?id ;
     ex:name ?name .
  FILTER(CONTAINS(LCASE(STR(?name)), LCASE("${esc(name)}")))
}
GROUP BY ?id
ORDER BY ?id
LIMIT ${Number(limit)}
`;
  return sparql(q);
}

// Recommendation query builder
function recommendQuery({ targetId, relation, limit }) {
  return `
${PREFIXES}
SELECT ?candId ?candName (SUM(?match) AS ?score)
WHERE {
  BIND(poke_simple:${Number(targetId)} AS ?target)
  ?target ex:${relation} ?type .

  ?cand a ex:Pokemon ;
        ex:number ?candId ;
        ex:name ?candName .
  OPTIONAL { ?cand ex:type1 ?t1 . }
  OPTIONAL { ?cand ex:type2 ?t2 . }

  BIND(
    (IF(BOUND(?t1) && ?t1 = ?type, 1, 0)) +
    (IF(BOUND(?t2) && ?t2 = ?type, 1, 0))
    AS ?match
  )

  FILTER(?match > 0)
  FILTER(?cand != ?target)
}
GROUP BY ?candId ?candName
ORDER BY DESC(?score) ASC(?candId)
LIMIT ${Number(limit)}
`;
}
function getParam(req, name, def = "") {
  return String(req.query[name] ?? def).trim();
}

function sendError(res, err) {
  res.status(500).json({ error: String(err.message || err) });
}

function mapRows(data, mapper) {
  return rows(data, mapper);
}

// try http://localhost:3001/api/search?q=charizard or http://localhost:3001/api/search?q=char
app.get("/api/search", async (req, res) => {
  const q = getParam(req, "q");
  if (!q) return res.json([]);

  const data = await findPokemonByNameLike(q, 20); //give pokemon that look like q (input)

  //send json response back to frontend 
  res.json(
    mapRows(data, b => ({
      id: Number(b.id.value),
      name: b.name.value
    }))
  );
});


// try http://localhost:3001/api/recommend?name=charizard&limit=5
app.get("/api/recommend", async (req, res) => {
  const name = getParam(req, "name");
  const limit = Number(req.query.limit ?? 5);

  const found = await findPokemonByNameLike(name, 1); //Search pokemon in blazegraph that matches 'name' -> returns 1 name
  const pokemon = found.results.bindings[0]; //the result from the query

  const target = {
    id: Number(pokemon.id.value),
    name: pokemon.name.value
  };

  const [best, worst] = await Promise.all([ //waits until both queries are done
    sparql(recommendQuery({ targetId: target.id, relation: "weakTo", limit })),  //query for best 
    sparql(recommendQuery({ targetId: target.id, relation: "resistantTo", limit })) //query for worst 
  ]);

 //takes the SPARQL result data and convert each row to a simple JS object for frontend
  const format = data =>
    mapRows(data, b => ({
      id: Number(b.candId.value),
      name: b.candName.value,
      score: Number(b.score.value)
    })); 
 //send json response back to frontend 
  res.json({
    target,
    best: format(best),
    worst: format(worst)
  });
});

//used for testing
app.listen(3001, () => {
  console.log("API running on http://localhost:3001");
  console.log("Try: http://localhost:3001/api/recommend?name=charizard&limit=5");
});
