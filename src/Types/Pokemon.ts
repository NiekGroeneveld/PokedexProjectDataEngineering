import { PokemonType } from "./PokemonType";

export class Pokemon {
    id: number;
    name: string;
    types: PokemonType[];
    imageUrl: string;
    height: number; // in decimetres
    weight: number; // in hectograms
    abilities: string[];
    category: string;
    evolutionChain: number[]; // array of Pokemon IDs in the evolution chain
    stats: PokemonStats;

    constructor(
        id: number,
        name: string,
        types: PokemonType[],
        imageUrl: string,
        height: number,
        weight: number,
        abilities: string[],
        category: string,
        evolutionChain: number[],
        stats: PokemonStats

    ) { 
        this.id = id;
        this.name = name;
        this.types = types;
        this.imageUrl = imageUrl;
        this.height = height;
        this.weight = weight;
        this.abilities = abilities;
        this.category = category;
        this.evolutionChain = evolutionChain;
        this.stats = stats;
    }
}
export class PokemonStats {
    hp: number;
    attack: number;
    defense: number;
    specialAttack: number;
    specialDefense: number;
    speed: number;

    constructor(
        hp: number,
        attack: number,
        defense: number,
        specialAttack: number,
        specialDefense: number,
        speed: number
    ){
        this.hp = hp;
        this.attack = attack;
        this.defense = defense;
        this.specialAttack = specialAttack;
        this.specialDefense = specialDefense;
        this.speed = speed;
    }
}   
    

