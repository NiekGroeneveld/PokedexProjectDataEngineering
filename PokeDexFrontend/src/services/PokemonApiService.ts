import { Pokemon, PokemonStats } from '../Types/Pokemon';
import { PokemonType } from '../Types/PokemonType';

// API Configuration
const API_BASE_URL = '/api';

// Helper function to handle API errors
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }
  return response.json();
}

// Helper function to convert API response to Pokemon class instance
function toPokemon(data: any): Pokemon {
  const stats = new PokemonStats(
    data.stats?.hp || 0,
    data.stats?.attack || 0,
    data.stats?.defense || 0,
    data.stats?.specialAttack || 0,
    data.stats?.specialDefense || 0,
    data.stats?.speed || 0
  );

  // Convert type strings to PokemonType enum values
  const types = data.types.map((type: string) => {
    const typeKey = type.toUpperCase();
    return PokemonType[typeKey as keyof typeof PokemonType] || type;
  });

  return new Pokemon(
    data.id,
    data.name,
    types,
    data.imageUrl,
    data.height || 0,
    data.weight || 0,
    data.abilities || [],
    data.category || 'Unknown',
    data.evolutionChain || [data.id],
    stats
  );
}

/**
 * Get lightweight search list (id, name, types only)
 * @param limit - Maximum number of Pokemon to fetch (default: 1000)
 */
export async function getSearchList(limit: number = 1000): Promise<Pokemon[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/pokemon/search?limit=${limit}`);
    const data = await handleResponse<any[]>(response);
    return data.map(toPokemon);
  } catch (error) {
    console.error('Error fetching search list:', error);
    return [];
  }
}

/**
 * Get all Pokemon from the API
 * @param limit - Maximum number of Pokemon to fetch (default: 151)
 * @param offset - Number of Pokemon to skip (default: 0)
 */
export async function getAllPokemon(limit: number = 151, offset: number = 0): Promise<Pokemon[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/pokemon?limit=${limit}&offset=${offset}`);
    const data = await handleResponse<any[]>(response);
    return data.map(toPokemon);
  } catch (error) {
    console.error('Error fetching all Pokemon:', error);
    return [];
  }
}

/**
 * Search for a Pokemon by ID
 * @param id - The Pokemon ID to search for
 * @returns The Pokemon if found, undefined otherwise
 */
export async function searchPokemonById(id: number): Promise<Pokemon | undefined> {
  try {
    const response = await fetch(`${API_BASE_URL}/pokemon/${id}`);
    const data = await handleResponse<any>(response);
    return toPokemon(data);
  } catch (error) {
    console.error(`Error fetching Pokemon with ID ${id}:`, error);
    return undefined;
  }
}

/**
 * Get a Pokemon by exact name (for getting the correct form with full details)
 * @param name - The exact Pokemon name to get
 * @returns The Pokemon if found, undefined otherwise
 */
export async function getPokemonByName(name: string): Promise<Pokemon | undefined> {
  try {
    const encodedName = encodeURIComponent(name);
    const response = await fetch(`${API_BASE_URL}/pokemon/name/${encodedName}`);
    const data = await handleResponse<any>(response);
    return toPokemon(data);
  } catch (error) {
    console.error(`Error fetching Pokemon with name ${name}:`, error);
    return undefined;
  }
}

/**
 * Get all forms of a Pokemon by ID (base, Mega, Gigantamax, regional variants)
 * @param id - The Pokemon ID
 * @returns Array of all forms of the Pokemon
 */
export async function getPokemonForms(id: number): Promise<Pokemon[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/pokemon/${id}/forms`);
    const data = await handleResponse<any[]>(response);
    return data.map(toPokemon);
  } catch (error) {
    console.error(`Error fetching Pokemon forms for ID ${id}:`, error);
    return [];
  }
}

/**
 * Get minimal Pokemon card data by ID (lightweight, for displaying cards)
 * @param id - The Pokemon ID
 * @returns Basic Pokemon data (id, name, types, imageUrl) or undefined if not found
 */
export async function getPokemonCardById(id: number): Promise<{ id: number; name: string; types: string[]; imageUrl: string } | undefined> {
  try {
    const response = await fetch(`${API_BASE_URL}/pokemon/${id}/card`);
    const data = await handleResponse<any>(response);
    return {
      id: data.id,
      name: data.name,
      types: data.types,
      imageUrl: data.imageUrl
    };
  } catch (error) {
    console.error(`Error fetching Pokemon card with ID ${id}:`, error);
    return undefined;
  }
}

/**
 * Search for Pokemon by name (case-insensitive, partial match)
 * @param name - The name to search for
 * @returns Array of matching Pokemon
 */
export async function searchPokemonByName(name: string): Promise<Pokemon[]> {
  if (!name || name.trim().length === 0) {
    return [];
  }

  try {
    const response = await fetch(`${API_BASE_URL}/pokemon/search?name=${encodeURIComponent(name)}`);
    const data = await handleResponse<any[]>(response);
    return data.map(toPokemon);
  } catch (error) {
    console.error(`Error searching Pokemon by name "${name}":`, error);
    return [];
  }
}

/**
 * Search for Pokemon by type
 * @param type - The PokemonType to search for
 * @returns Array of Pokemon with that type
 */
export async function searchPokemonByType(type: PokemonType): Promise<Pokemon[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/pokemon/type/${encodeURIComponent(type)}`);
    const data = await handleResponse<any[]>(response);
    return data.map(toPokemon);
  } catch (error) {
    console.error(`Error searching Pokemon by type "${type}":`, error);
    return [];
  }
}

/**
 * Get Pokemon by evolution chain
 * @param chainIds - Array of Pokemon IDs in the evolution chain
 * @returns Array of Pokemon in the evolution chain
 */
export async function getPokemonByEvolutionChain(chainIds: number[]): Promise<Pokemon[]> {
  if (!chainIds || chainIds.length === 0) {
    return [];
  }

  try {
    // If we have a primary ID, use the evolution chain endpoint
    if (chainIds.length > 0) {
      const response = await fetch(`${API_BASE_URL}/pokemon/evolution-chain/${chainIds[0]}`);
      const data = await handleResponse<any[]>(response);
      return data.map(toPokemon);
    }
    return [];
  } catch (error) {
    console.error('Error fetching evolution chain:', error);
    return [];
  }
}

/**
 * Get the total count of Pokemon in the database
 */
export async function getPokemonCount(): Promise<number> {
  try {
    const response = await fetch(`${API_BASE_URL}/stats`);
    const data = await handleResponse<{ totalPokemon: number }>(response);
    return data.totalPokemon;
  } catch (error) {
    console.error('Error fetching Pokemon count:', error);
    return 0;
  }
}

/**
 * Get Pokemon recommendations based on type effectiveness
 * @param pokemonId - ID of the Pokemon to get recommendations for
 * @param limit - Maximum number of recommendations (default: 5)
 */
export async function getRecommendations(
  pokemonId: number,
  limit: number = 5
): Promise<{
  target: { id: number; name: string };
  best: Array<{ id: number; name: string; score: number }>;
  worst: Array<{ id: number; name: string; score: number }>;
}> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/recommendations?pokemon_id=${pokemonId}&limit=${limit}`
    );
    return await handleResponse(response);
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    return {
      target: { id: pokemonId, name: 'Unknown' },
      best: [],
      worst: []
    };
  }
}

// Export for backward compatibility (will be undefined until loaded)
export let PICHU: Pokemon | undefined;
export let PIKACHU: Pokemon | undefined;
export let RAICHU: Pokemon | undefined;

// Load the classic Pokemon on module initialization
(async () => {
  try {
    PICHU = await searchPokemonById(172);
    PIKACHU = await searchPokemonById(25);
    RAICHU = await searchPokemonById(26);
  } catch (error) {
    console.error('Error loading classic Pokemon:', error);
  }
})();
