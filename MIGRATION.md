# Frontend Migration Guide

## Overview
This guide explains how to update your React components to use the new `PokemonApiService` instead of the hardcoded `PokemonDatabase`.

## Key Changes

### 1. Import Change
**Old:**
```typescript
import { getAllPokemon, searchPokemonById } from '../data/PokemonDatabase';
```

**New:**
```typescript
import { getAllPokemon, searchPokemonById } from '../services/PokemonApiService';
```

### 2. Async/Await Pattern
All functions are now **async** and return Promises.

**Old (Synchronous):**
```typescript
const pokemon = searchPokemonById(25);
```

**New (Asynchronous):**
```typescript
const pokemon = await searchPokemonById(25);
// or
searchPokemonById(25).then(pokemon => {
  // use pokemon
});
```

### 3. Component Updates with Loading States

You'll need to add loading and error states to your components:

```typescript
import { useState, useEffect } from 'react';
import { getAllPokemon } from '../services/PokemonApiService';
import { Pokemon } from '../Types/Pokemon';

function PokemonList() {
  const [pokemon, setPokemon] = useState<Pokemon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPokemon() {
      try {
        setLoading(true);
        const data = await getAllPokemon();
        setPokemon(data);
      } catch (err) {
        setError('Failed to load Pokemon');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchPokemon();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      {pokemon.map(p => <div key={p.id}>{p.name}</div>)}
    </div>
  );
}
```

## Function-by-Function Migration

### getAllPokemon()
```typescript
// OLD
const allPokemon = getAllPokemon();

// NEW
const allPokemon = await getAllPokemon(151, 0); // limit, offset
```

### searchPokemonById()
```typescript
// OLD
const pikachu = searchPokemonById(25);

// NEW
const pikachu = await searchPokemonById(25);
// Returns undefined if not found
```

### searchPokemonByName()
```typescript
// OLD
const results = searchPokemonByName("pika");

// NEW
const results = await searchPokemonByName("pika");
// Returns empty array if no matches
```

### searchPokemonByType()
```typescript
// OLD
const electricPokemon = searchPokemonByType(PokemonType.ELECTRIC);

// NEW
const electricPokemon = await searchPokemonByType(PokemonType.ELECTRIC);
```

### getPokemonByEvolutionChain()
```typescript
// OLD
const evolutionLine = getPokemonByEvolutionChain([172, 25, 26]);

// NEW
const evolutionLine = await getPokemonByEvolutionChain([172, 25, 26]);
```

### getPokemonCount()
```typescript
// OLD
const count = getPokemonCount();

// NEW
const count = await getPokemonCount();
```

## New Functions Available

### getRecommendations()
Get type-based Pokemon recommendations:

```typescript
const recommendations = await getRecommendations(25, 5); // Pikachu, limit 5

// Returns:
// {
//   target: { id: 25, name: "Pikachu" },
//   best: [{ id: 27, name: "Sandshrew", score: 2 }, ...],
//   worst: [{ id: 7, name: "Squirtle", score: 1 }, ...]
// }
```

## Files to Update

Based on your project structure, update these files:

1. **Components using Pokemon data:**
   - `src/components/PokemonPage/PokemonPage.tsx`
   - `src/components/PokemonPage/ContentSection/PokemonInfo/PokemonInfo.tsx`
   - `src/components/PokemonPage/EvolutionChain/EvolutionChain.tsx`
   - `src/components/PokemonPage/RecommenderBox/RecommenderBox.tsx`
   - `src/components/NavBar/SearchBar/SearchBar.tsx`

2. **Context (if applicable):**
   - `src/contexts/PokemonContext.tsx`

## Example: Complete Component Migration

**Before:**
```typescript
import { searchPokemonById } from '../data/PokemonDatabase';

function PokemonDetail({ id }: { id: number }) {
  const pokemon = searchPokemonById(id);
  
  if (!pokemon) return <div>Not found</div>;
  
  return <div>{pokemon.name}</div>;
}
```

**After:**
```typescript
import { useState, useEffect } from 'react';
import { searchPokemonById } from '../services/PokemonApiService';
import { Pokemon } from '../Types/Pokemon';

function PokemonDetail({ id }: { id: number }) {
  const [pokemon, setPokemon] = useState<Pokemon | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadPokemon() {
      setLoading(true);
      const data = await searchPokemonById(id);
      setPokemon(data || null);
      setLoading(false);
    }
    
    loadPokemon();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!pokemon) return <div>Not found</div>;
  
  return <div>{pokemon.name}</div>;
}
```

## Testing

1. **Start the backend:**
   ```bash
   docker-compose up blazegraph backend
   ```

2. **Load data:**
   ```bash
   ./load-data.ps1
   ```

3. **Test API manually:**
   ```bash
   curl http://localhost:5000/api/pokemon/25
   ```

4. **Run frontend in dev mode:**
   ```bash
   cd PokeDexFrontend
   npm run dev
   ```

## Common Issues

### CORS Errors
- Backend has CORS enabled for all origins
- In production, update `allow_origins` in `Backend/app.py`

### API Not Available
- Check nginx.conf has correct proxy configuration
- Verify backend is running: `docker-compose ps`

### Empty Results
- Ensure Blazegraph data is loaded
- Check backend logs: `docker-compose logs backend`

### Type Mismatches
- The API returns the same structure as before
- Stats object structure is maintained
- Type enum values are preserved

## Rollback Plan

If you need to rollback, keep the old `PokemonDatabase.ts` file and simply change imports back. The API service maintains the same function signatures for compatibility.
