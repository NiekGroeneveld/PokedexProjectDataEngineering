import "./EvolutionChain.css";
import EvolutionCard from "../../Shared/PokemonCard/Pokemoncard";
import { usePokemon } from "../../../contexts/PokemonContext";
import { getPokemonCardById, searchPokemonById } from "../../../services/PokemonApiService";
import { getTypeColor } from "../../../Types/PokemonType";
import { useState, useEffect } from "react";

type PokemonCard = {
  id: number;
  name: string;
  types: string[];
  imageUrl: string;
};

export default function EvolutionChain() {
  const { selectedPokemon, setSelectedPokemon } = usePokemon();
  const [evolutionChain, setEvolutionChain] = useState<PokemonCard[]>([]);

  useEffect(() => {
    if (!selectedPokemon || !selectedPokemon.evolutionChain) {
      setEvolutionChain([]);
      return;
    }

    async function loadEvolutionChain() {
      if (!selectedPokemon?.evolutionChain) return;
      
      try {
        // Load card data for each Pokemon in the evolution chain
        const cards = await Promise.all(
          selectedPokemon.evolutionChain.map(async (id) => {
            const card = await getPokemonCardById(id);
            return card || { id, name: 'Unknown', types: [], imageUrl: '' };
          })
        );
        setEvolutionChain(cards);
      } catch (error) {
        console.error('Failed to load evolution chain:', error);
        setEvolutionChain([]);
      }
    }

    loadEvolutionChain();
  }, [selectedPokemon?.id]);

  if (!selectedPokemon || !selectedPokemon.evolutionChain || evolutionChain.length === 0) {
    return null;
  }

  // Find current Pokemon's index in the chain
  const currentIndex = evolutionChain.findIndex(
    pokemon => pokemon.id === selectedPokemon.id
  );

  if (currentIndex === -1) {
    return null;
  }

  // Determine which Pokemon to show based on current position
  const showPrevious = currentIndex > 0;
  const showNext = currentIndex < evolutionChain.length - 1;
  const showLast = currentIndex < evolutionChain.length - 2;

  // Get the Pokemon to display
  const previousPokemon = showPrevious ? evolutionChain[currentIndex - 1] : null;
  const currentPokemon = evolutionChain[currentIndex];
  const nextPokemon = showNext ? evolutionChain[currentIndex + 1] : null;
  const lastPokemon = showLast ? evolutionChain[currentIndex + 2] : null;

  // Determine labels based on position
  const getLabel = (position: 'previous' | 'current' | 'next' | 'last'): string => {
    if (currentIndex === 0) {
      // First in chain
      if (position === 'current') return 'Current';
      if (position === 'next') return 'Next';
      if (position === 'last') return 'Last';
    } else if (currentIndex === evolutionChain.length - 1) {
      // Last in chain
      if (position === 'previous' && currentIndex === 2) return 'First';
      if (position === 'previous' && currentIndex === 1) return 'Previous';
      if (position === 'next' && currentIndex > 1) return 'Previous';
      if (position === 'current') return 'Current';
    } else {
      // Middle of chain
      if (position === 'previous') return 'Previous';
      if (position === 'current') return 'Current';
      if (position === 'next') return 'Next';
    }
    return position.charAt(0).toUpperCase() + position.slice(1);
  };

  const fallbackTypeColor = currentPokemon.types.length > 0
    ? getTypeColor(currentPokemon.types[0])
    : "#f5f5f5";

  const getPrimaryTypeColor = (pokemon: PokemonCard | null | undefined): string => {
    if (!pokemon || pokemon.types.length === 0) {
      return fallbackTypeColor;
    }
    return getTypeColor(pokemon.types[0]);
  };

  const handleSelect = (pokemon: PokemonCard | null) => async () => {
    if (pokemon) {
      // Load full Pokemon data by ID (fast, gets base form)
      const fullPokemon = await searchPokemonById(pokemon.id);
      if (fullPokemon) {
        setSelectedPokemon(fullPokemon);
      }
    }
  };

  return (
    <div className="evolution-chain-section">
      <div className="evolution-chain-container">
        <div className="evolution-chain-header">
          <h2 className="evolution-chain-title">Evolution Chain</h2>
          <span className="evolution-chain-divider" aria-hidden="true"></span>
        </div>

        <div className="evolution-chain-cards">
          {/* Show First/Previous if not at the beginning */}
          {currentIndex === evolutionChain.length - 1 && currentIndex === 2 && evolutionChain[0] && (
            <>
              <EvolutionCard
                label="First"
                name={evolutionChain[0].name}
                imageUrl={evolutionChain[0].imageUrl}
                typeColor={getPrimaryTypeColor(evolutionChain[0])}
                onSelect={handleSelect(evolutionChain[0])}
              />
              <span className="evolution-arrow">&gt;</span>
            </>
          )}

          {previousPokemon && currentIndex !== evolutionChain.length - 1 && (
            <>
              <EvolutionCard
                label={getLabel('previous')}
                name={previousPokemon.name}
                imageUrl={previousPokemon.imageUrl}
                typeColor={getPrimaryTypeColor(previousPokemon)}
                onSelect={handleSelect(previousPokemon)}
              />
              <span className="evolution-arrow">&gt;</span>
            </>
          )}

          {currentIndex === evolutionChain.length - 1 && currentIndex > 0 && evolutionChain[currentIndex - 1] && (
            <>
              <EvolutionCard
                label="Previous"
                name={evolutionChain[currentIndex - 1].name}
                imageUrl={evolutionChain[currentIndex - 1].imageUrl}
                typeColor={getPrimaryTypeColor(evolutionChain[currentIndex - 1])}
                onSelect={handleSelect(evolutionChain[currentIndex - 1])}
              />
              <span className="evolution-arrow">&gt;</span>
            </>
          )}

          {/* Current Pokemon */}
          <EvolutionCard
            label="Current"
            name={currentPokemon.name}
            imageUrl={currentPokemon.imageUrl}
            typeColor={getPrimaryTypeColor(currentPokemon)}
            onSelect={handleSelect(currentPokemon)}
          />

          {/* Next Pokemon */}
          {nextPokemon && (
            <>
              <span className="evolution-arrow">&gt;</span>
              <EvolutionCard
                label={getLabel('next')}
                name={nextPokemon.name}
                imageUrl={nextPokemon.imageUrl}
                typeColor={getPrimaryTypeColor(nextPokemon)}
                onSelect={handleSelect(nextPokemon)}
              />
            </>
          )}

          {/* Last Pokemon (if current is first) */}
          {lastPokemon && (
            <>
              <span className="evolution-arrow">&gt;</span>
              <EvolutionCard
                label="Last"
                name={lastPokemon.name}
                imageUrl={lastPokemon.imageUrl}
                typeColor={getPrimaryTypeColor(lastPokemon)}
                onSelect={handleSelect(lastPokemon)}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}