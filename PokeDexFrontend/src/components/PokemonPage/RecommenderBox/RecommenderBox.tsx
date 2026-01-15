import "./RecommenderBox.css";
import PokemonCard from "../../Shared/PokemonCard/Pokemoncard";

import { usePokemon } from "../../../contexts/PokemonContext";
import { getAllPokemon } from "../../../data/PokemonDatabase";
import { getTypeColor } from "../../../Types/PokemonType";
import type { Pokemon } from "../../../Types/Pokemon";

const MAX_RECOMMENDATIONS = 5;

const hasSharedType = (a: Pokemon, b: Pokemon): boolean => {
    return a.types.some(type => b.types.includes(type));
};

const padRecommendations = (entries: Pokemon[], fallback: Pokemon): Pokemon[] => {
    const padded = [...entries];
    while (padded.length < MAX_RECOMMENDATIONS) {
        padded.push(fallback);
    }
    return padded.slice(0, MAX_RECOMMENDATIONS);
};

export default function RecommenderBox() {
    const { selectedPokemon, setSelectedPokemon } = usePokemon();

    if (!selectedPokemon) {
        return null;
    }

    const allPokemon = getAllPokemon().filter(pokemon => pokemon.id !== selectedPokemon.id);

    const bestMatches = padRecommendations(
        allPokemon.filter(pokemon => hasSharedType(pokemon, selectedPokemon)),
        selectedPokemon
    );

    const worstMatches = padRecommendations(
        allPokemon.filter(pokemon => !hasSharedType(pokemon, selectedPokemon)),
        selectedPokemon
    );

    return (
        <section className="recommender-section">
            <div className="recommender-container">
                <header className="recommender-header">
                    <h2 className="recommender-title">Recommendations</h2>
                    <span className="recommender-divider" aria-hidden="true"></span>
                </header>

                <div className="recommender-box">
                    <div className="recommendation-column">
                        <div className="recommendation-panel">
                            <h3 className="recommendation-title">Best Matches</h3>
                            <div className="recommendation-list">
                                {bestMatches.map((pokemon, index) => (
                                    <PokemonCard
                                        key={`best-${pokemon.id}-${index}`}
                                        label={`Best Match ${index + 1}`}
                                        name={pokemon.name}
                                        imageUrl={pokemon.imageUrl}
                                        typeColor={pokemon.types.length > 0 ? getTypeColor(pokemon.types[0]) : "#777"}
                                        onSelect={() => setSelectedPokemon(pokemon)}
                                    />
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="recommendation-column">
                        <div className="recommendation-panel">
                            <h3 className="recommendation-title">Worst Matches</h3>
                            <div className="recommendation-list">
                                {worstMatches.map((pokemon, index) => (
                                    <PokemonCard
                                        key={`worst-${pokemon.id}-${index}`}
                                        label={`Worst Match ${index + 1}`}
                                        name={pokemon.name}
                                        imageUrl={pokemon.imageUrl}
                                        typeColor={pokemon.types.length > 0 ? getTypeColor(pokemon.types[0]) : "#777"}
                                        onSelect={() => setSelectedPokemon(pokemon)}
                                    />
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}