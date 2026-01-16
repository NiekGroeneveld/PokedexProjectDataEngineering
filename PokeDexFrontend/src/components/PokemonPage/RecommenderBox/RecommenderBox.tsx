import "./RecommenderBox.css";
import PokemonCard from "../../Shared/PokemonCard/Pokemoncard";
import { useState, useEffect } from "react";

import { usePokemon } from "../../../contexts/PokemonContext";
import { getRecommendations, getPokemonCardById, searchPokemonById } from "../../../services/PokemonApiService";
import { getTypeColor } from "../../../Types/PokemonType";

const MAX_RECOMMENDATIONS = 5;

export default function RecommenderBox() {
    const { selectedPokemon, setSelectedPokemon } = usePokemon();
    const [bestMatches, setBestMatches] = useState<Array<{id: number; name: string; types: string[]; imageUrl: string}>>([]);
    const [worstMatches, setWorstMatches] = useState<Array<{id: number; name: string; types: string[]; imageUrl: string}>>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!selectedPokemon) return;

        async function loadRecommendations() {
            if (!selectedPokemon?.id) return;
            
            setLoading(true);
            try {
                const recommendations = await getRecommendations(selectedPokemon.id, MAX_RECOMMENDATIONS);
                
                // Load card data for each recommendation
                const bestCards = await Promise.all(
                    recommendations.best.map(async (rec) => {
                        const card = await getPokemonCardById(rec.id);
                        return card || { id: rec.id, name: rec.name, types: [], imageUrl: '' };
                    })
                );
                
                const worstCards = await Promise.all(
                    recommendations.worst.map(async (rec) => {
                        const card = await getPokemonCardById(rec.id);
                        return card || { id: rec.id, name: rec.name, types: [], imageUrl: '' };
                    })
                );
                
                setBestMatches(bestCards);
                setWorstMatches(worstCards);
            } catch (error) {
                console.error('Failed to load recommendations:', error);
                setBestMatches([]);
                setWorstMatches([]);
            } finally {
                setLoading(false);
            }
        }

        loadRecommendations();
    }, [selectedPokemon?.id]);

    if (!selectedPokemon) {
        return null;
    }

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
                            <h3 className="recommendation-title">Losing Matches</h3>
                            <div className="recommendation-list">
                                {loading ? (
                                    <div style={{padding: '20px', textAlign: 'center'}}>Loading...</div>
                                ) : bestMatches.length > 0 ? (
                                    bestMatches.map((pokemon, index) => (
                                        <PokemonCard
                                            key={`best-${pokemon.id}-${index}`}
                                            label={`Losing Match ${index + 1}`}
                                            name={pokemon.name}
                                            imageUrl={pokemon.imageUrl}
                                            typeColor={pokemon.types.length > 0 ? getTypeColor(pokemon.types[0]) : "#777"}
                                            onSelect={async () => {
                                                const fullPokemon = await searchPokemonById(pokemon.id);
                                                if (fullPokemon) setSelectedPokemon(fullPokemon);
                                            }}
                                        />
                                    ))
                                ) : (
                                    <div style={{padding: '20px', textAlign: 'center'}}>No recommendations</div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="recommendation-column">
                        <div className="recommendation-panel">
                            <h3 className="recommendation-title">Winning Matches</h3>
                            <div className="recommendation-list">
                                {loading ? (
                                    <div style={{padding: '20px', textAlign: 'center'}}>Loading...</div>
                                ) : worstMatches.length > 0 ? (
                                    worstMatches.map((pokemon, index) => (
                                        <PokemonCard
                                            key={`worst-${pokemon.id}-${index}`}
                                            label={`Winning Match ${index + 1}`}
                                            name={pokemon.name}
                                            imageUrl={pokemon.imageUrl}
                                            typeColor={pokemon.types.length > 0 ? getTypeColor(pokemon.types[0]) : "#777"}
                                            onSelect={async () => {
                                                const fullPokemon = await searchPokemonById(pokemon.id);
                                                if (fullPokemon) setSelectedPokemon(fullPokemon);
                                            }}
                                        />
                                    ))
                                ) : (
                                    <div style={{padding: '20px', textAlign: 'center'}}>No recommendations</div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}