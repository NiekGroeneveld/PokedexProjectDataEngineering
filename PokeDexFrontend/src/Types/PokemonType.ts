export const PokemonType = {
    NORMAL: "Normal",
    FIRE: "Fire",
    WATER: "Water",
    ELECTRIC: "Electric",
    GRASS: "Grass",
    ICE: "Ice",
    FIGHTING: "Fighting",
    POISON: "Poison",
    GROUND: "Ground",
    FLYING: "Flying",
    PSYCHIC: "Psychic",
    BUG: "Bug",
    ROCK: "Rock",
    GHOST: "Ghost",
    DRAGON: "Dragon",
    DARK: "Dark",
    STEEL: "Steel",
    FAIRY: "Fairy"
} as const;

export type PokemonType = typeof PokemonType[keyof typeof PokemonType];

export const TYPE_COLORS: Record<PokemonType, string> = {
    [PokemonType.NORMAL]: "#a8a878",
    [PokemonType.FIRE]: "#f08030",
    [PokemonType.WATER]: "#6890f0",
    [PokemonType.ELECTRIC]: "#e8d13b",
    [PokemonType.GRASS]: "#78c850",
    [PokemonType.ICE]: "#98d8d8",
    [PokemonType.FIGHTING]: "#c03028",
    [PokemonType.POISON]: "#a040a0",
    [PokemonType.GROUND]: "#e0c068",
    [PokemonType.FLYING]: "#a890f0",
    [PokemonType.PSYCHIC]: "#f85888",
    [PokemonType.BUG]: "#a8b820",
    [PokemonType.ROCK]: "#b8a038",
    [PokemonType.GHOST]: "#705898",
    [PokemonType.DRAGON]: "#7038f8",
    [PokemonType.DARK]: "#705848",
    [PokemonType.STEEL]: "#b8b8d0",
    [PokemonType.FAIRY]: "#ee99ac"
};

export function getTypeColor(type: PokemonType | string): string {
    // If type is already a PokemonType value, use it directly
    // Otherwise, find the matching PokemonType key
    const typeValue = Object.values(PokemonType).includes(type as any) 
        ? type as PokemonType
        : type as PokemonType;
    return TYPE_COLORS[typeValue] || TYPE_COLORS[PokemonType.NORMAL];
}