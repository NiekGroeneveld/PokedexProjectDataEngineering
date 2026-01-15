import { Pokemon, PokemonStats } from '../Types/Pokemon';
import { PokemonType } from '../Types/PokemonType';
import PikachuImg from '../assets/Pikachu.png';
import RaichuImg from '../assets/Raichu.png';
import PichuImg from '../assets/Pichu.png';

// Pokemon Database - All available Pokemon
const POKEMON_DATABASE: Pokemon[] = [
  new Pokemon(
    172,
    'Pichu',
    [PokemonType.ELECTRIC],
    PichuImg,
    3,
    20,
    ['Static', 'Lightning Rod'],
    "Tiny Mouse",
    [172, 25, 26],
    new PokemonStats(20, 40, 15, 35, 35, 60)
  ),
  new Pokemon(
    25,
    'Pikachu',
    [PokemonType.ELECTRIC],
    PikachuImg,
    4,
    60,
    ['Static', 'Lightning Rod'],
    "Mouse",
    [172, 25, 26],
    new PokemonStats(35, 55, 40, 50, 50, 90)
  ),
  new Pokemon(
    26,
    'Raichu',
    [PokemonType.POISON],
    RaichuImg,
    8,
    300,
    ['Static', 'Lightning Rod'],
    "Mouse",
    [172, 25, 26],
    new PokemonStats(60, 90, 55, 90, 80, 110)
  ),
];

// Database Query Functions

/**
 * Get all Pokemon from the database
 */
export function getAllPokemon(): Pokemon[] {
  return POKEMON_DATABASE;
}

/**
 * Search for a Pokemon by ID
 * @param id - The Pokemon ID to search for
 * @returns The Pokemon if found, undefined otherwise
 */
export function searchPokemonById(id: number): Pokemon | undefined {
  return POKEMON_DATABASE.find(pokemon => pokemon.id === id);
}

/**
 * Search for Pokemon by name (case-insensitive, partial match)
 * @param name - The name to search for
 * @returns Array of matching Pokemon
 */
export function searchPokemonByName(name: string): Pokemon[] {
  const searchTerm = name.toLowerCase();
  return POKEMON_DATABASE.filter(pokemon => 
    pokemon.name.toLowerCase().includes(searchTerm)
  );
}

/**
 * Search for Pokemon by type
 * @param type - The PokemonType to search for
 * @returns Array of Pokemon with that type
 */
export function searchPokemonByType(type: PokemonType): Pokemon[] {
  return POKEMON_DATABASE.filter(pokemon => 
    pokemon.types.includes(type)
  );
}

/**
 * Get Pokemon by evolution chain
 * @param chainIds - Array of Pokemon IDs in the evolution chain
 * @returns Array of Pokemon in the evolution chain
 */
export function getPokemonByEvolutionChain(chainIds: number[]): Pokemon[] {
  return POKEMON_DATABASE.filter(pokemon => 
    chainIds.includes(pokemon.id)
  );
}

/**
 * Get the total count of Pokemon in the database
 */
export function getPokemonCount(): number {
  return POKEMON_DATABASE.length;
}

// Export individual Pokemon for backward compatibility
export const PICHU = POKEMON_DATABASE[0];
export const PIKACHU = POKEMON_DATABASE[1];
export const RAICHU = POKEMON_DATABASE[2];
