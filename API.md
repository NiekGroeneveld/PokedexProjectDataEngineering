# Pokemon API Documentation

Base URL: `http://localhost:5000`

## Endpoints

### Health Check

#### GET `/`
Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "message": "Pokemon API is running"
}
```

---

### Pokemon Endpoints

#### GET `/api/pokemon`
Get all Pokemon with pagination.

**Query Parameters:**
- `limit` (optional, default: 151, max: 1000) - Number of Pokemon to return
- `offset` (optional, default: 0) - Number of Pokemon to skip

**Example:**
```bash
curl "http://localhost:5000/api/pokemon?limit=10&offset=0"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Bulbasaur",
    "types": ["Grass", "Poison"],
    "imageUrl": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png",
    "height": 7,
    "weight": 69,
    "abilities": ["Overgrow", "Chlorophyll"],
    "category": "Seed",
    "evolutionChain": [1, 2, 3],
    "stats": {
      "hp": 45,
      "attack": 49,
      "defense": 49,
      "specialAttack": 65,
      "specialDefense": 65,
      "speed": 45
    }
  }
]
```

---

#### GET `/api/pokemon/{id}`
Get a specific Pokemon by ID with full details including stats.

**Path Parameters:**
- `id` (required) - Pokemon ID (1-1000+)

**Example:**
```bash
curl "http://localhost:5000/api/pokemon/25"
```

**Response:**
```json
{
  "id": 25,
  "name": "Pikachu",
  "types": ["Electric"],
  "imageUrl": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
  "height": 4,
  "weight": 60,
  "abilities": ["Static", "Lightning Rod"],
  "category": "Mouse",
  "evolutionChain": [172, 25, 26],
  "stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "specialAttack": 50,
    "specialDefense": 50,
    "speed": 90
  }
}
```

**Error Response (404):**
```json
{
  "detail": "Pokemon with ID 9999 not found"
}
```

---

#### GET `/api/pokemon/search`
Search for Pokemon by name (partial match, case-insensitive).

**Query Parameters:**
- `name` (required) - Name to search for

**Example:**
```bash
curl "http://localhost:5000/api/pokemon/search?name=char"
```

**Response:**
```json
[
  {
    "id": 4,
    "name": "Charmander",
    "types": ["Fire"],
    "imageUrl": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png",
    ...
  },
  {
    "id": 5,
    "name": "Charmeleon",
    "types": ["Fire"],
    ...
  },
  {
    "id": 6,
    "name": "Charizard",
    "types": ["Fire", "Flying"],
    ...
  }
]
```

---

#### GET `/api/pokemon/type/{type}`
Get all Pokemon of a specific type.

**Path Parameters:**
- `type` (required) - Pokemon type (e.g., "Fire", "Water", "Electric")

**Valid Types:**
- Normal, Fire, Water, Electric, Grass, Ice, Fighting, Poison
- Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy

**Example:**
```bash
curl "http://localhost:5000/api/pokemon/type/Electric"
```

**Response:**
```json
[
  {
    "id": 25,
    "name": "Pikachu",
    "types": ["Electric"],
    ...
  },
  {
    "id": 26,
    "name": "Raichu",
    "types": ["Electric"],
    ...
  }
]
```

---

#### GET `/api/pokemon/evolution-chain/{id}`
Get the complete evolution chain for a Pokemon.

**Path Parameters:**
- `id` (required) - Pokemon ID

**Example:**
```bash
curl "http://localhost:5000/api/pokemon/evolution-chain/25"
```

**Response:**
```json
[
  {
    "id": 172,
    "name": "Pichu",
    "types": ["Electric"],
    ...
  },
  {
    "id": 25,
    "name": "Pikachu",
    "types": ["Electric"],
    ...
  },
  {
    "id": 26,
    "name": "Raichu",
    "types": ["Electric"],
    ...
  }
]
```

---

### Recommendation Endpoints

#### GET `/api/recommendations`
Get Pokemon recommendations based on type effectiveness.

**Query Parameters:**
- `pokemon_id` (optional) - Pokemon ID to get recommendations for
- `name` (optional) - Pokemon name (used if pokemon_id not provided)
- `limit` (optional, default: 5, max: 20) - Number of recommendations

**Note:** Either `pokemon_id` or `name` must be provided.

**Example:**
```bash
curl "http://localhost:5000/api/recommendations?pokemon_id=25&limit=5"
# or
curl "http://localhost:5000/api/recommendations?name=pikachu&limit=5"
```

**Response:**
```json
{
  "target": {
    "id": 25,
    "name": "Pikachu"
  },
  "best": [
    {
      "id": 27,
      "name": "Sandshrew",
      "score": 2
    },
    {
      "id": 50,
      "name": "Diglett",
      "score": 2
    }
  ],
  "worst": [
    {
      "id": 1,
      "name": "Bulbasaur",
      "score": 1
    },
    {
      "id": 7,
      "name": "Squirtle",
      "score": 1
    }
  ]
}
```

**Explanation:**
- `best` - Pokemon that are strong against the target (target is weak to these)
- `worst` - Pokemon that the target is strong against (these are weak to the target)
- `score` - Number of type matchups (higher = stronger advantage)

---

### Statistics Endpoints

#### GET `/api/stats`
Get database statistics.

**Example:**
```bash
curl "http://localhost:5000/api/stats"
```

**Response:**
```json
{
  "totalPokemon": 1008
}
```

---

## Data Models

### Pokemon Object
```typescript
{
  id: number;              // Pokemon ID (1-1000+)
  name: string;            // Pokemon name
  types: string[];         // Array of type names
  imageUrl: string;        // URL to official artwork from PokeAPI
  height: number;          // Height in decimeters
  weight: number;          // Weight in hectograms
  abilities: string[];     // Array of ability names
  category: string;        // Pokemon category/species
  evolutionChain: number[]; // Array of Pokemon IDs in evolution chain
  stats?: {                // Stats (optional, included in detail views)
    hp: number;
    attack: number;
    defense: number;
    specialAttack: number;
    specialDefense: number;
    speed: number;
  }
}
```

### Recommendation Object
```typescript
{
  target: {
    id: number;
    name: string;
  };
  best: Array<{           // Pokemon strong against target
    id: number;
    name: string;
    score: number;
  }>;
  worst: Array<{          // Pokemon target is strong against
    id: number;
    name: string;
    score: number;
  }>;
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Either pokemon_id or name must be provided"
}
```

### 404 Not Found
```json
{
  "detail": "Pokemon with ID 9999 not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Database query failed: connection timeout"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider adding rate limiting middleware.

---

## CORS

CORS is enabled for all origins (`*`). In production, update the `allow_origins` list in `Backend/app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

These interfaces allow you to:
- Browse all endpoints
- See request/response schemas
- Test endpoints directly in the browser
- Download OpenAPI specification

---

## Examples

### TypeScript/React Usage

```typescript
import { Pokemon } from './types';

// Get all Pokemon
async function fetchAllPokemon(): Promise<Pokemon[]> {
  const response = await fetch('/api/pokemon?limit=151');
  return response.json();
}

// Search by name
async function searchPokemon(query: string): Promise<Pokemon[]> {
  const response = await fetch(`/api/pokemon/search?name=${encodeURIComponent(query)}`);
  return response.json();
}

// Get specific Pokemon
async function getPokemon(id: number): Promise<Pokemon> {
  const response = await fetch(`/api/pokemon/${id}`);
  if (!response.ok) {
    throw new Error('Pokemon not found');
  }
  return response.json();
}

// Get recommendations
async function getRecommendations(pokemonId: number) {
  const response = await fetch(`/api/recommendations?pokemon_id=${pokemonId}&limit=5`);
  return response.json();
}
```

### Python Usage

```python
import requests

BASE_URL = "http://localhost:5000"

# Get all Pokemon
response = requests.get(f"{BASE_URL}/api/pokemon", params={"limit": 151})
pokemon_list = response.json()

# Search by name
response = requests.get(f"{BASE_URL}/api/pokemon/search", params={"name": "pika"})
results = response.json()

# Get specific Pokemon
response = requests.get(f"{BASE_URL}/api/pokemon/25")
pikachu = response.json()

# Get recommendations
response = requests.get(
    f"{BASE_URL}/api/recommendations",
    params={"pokemon_id": 25, "limit": 5}
)
recommendations = response.json()
```
