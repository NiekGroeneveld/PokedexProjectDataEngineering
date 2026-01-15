import { usePokemon } from "../../../../contexts/PokemonContext";
import { getTypeColor } from "../../../../Types/PokemonType";
import InfoBlock from "./PokemonDetails/InfoBlock";
import Abilities from "./PokemonDetails/Abilities";
import Stats from "./PokemonDetails/Stats";
import "./PokemonInfo.css";

export default function PokemonInfo() {
    const { selectedPokemon } = usePokemon();

    if (!selectedPokemon) {
        return (
            <div className="pokemon-info-container">
                <p className="no-pokemon-message">Select a Pokemon to view details</p>
            </div>
        );
    }

    // Get primary type color for abilities and stats
    const primaryTypeColor = getTypeColor(selectedPokemon.types[0]);

    return (
        <div className="pokemon-info-container">
            <div className="info-row-top">
                <InfoBlock
                    height={selectedPokemon.height}
                    weight={selectedPokemon.weight}
                    category={selectedPokemon.category}
                />
                <Abilities
                    abilities={selectedPokemon.abilities}
                    primaryTypeColor={primaryTypeColor}
                />
            </div>
            <Stats
                stats={selectedPokemon.stats}
                primaryTypeColor={primaryTypeColor}
            />
        </div>
    );
}   