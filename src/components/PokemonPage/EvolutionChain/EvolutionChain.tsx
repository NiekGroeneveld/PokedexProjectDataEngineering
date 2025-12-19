import "./EvolutionChain.css";
import EvolutionCard from "./EvolutionCard/Evolutioncard";
import { usePokemon } from "../../../contexts/PokemonContext";
import { searchPokemonById } from "../../../data/PokemonDatabase";
import { getTypeColor } from "../../../Types/PokemonType";

export default function EvolutionChain() {
  const { selectedPokemon } = usePokemon();

  if (!selectedPokemon || !selectedPokemon.evolutionChain) {
    return null;
  }

  // Get all Pokemon in the evolution chain
  const evolutionChain = selectedPokemon.evolutionChain
    .map(id => searchPokemonById(id))
    .filter(pokemon => pokemon !== undefined);

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

  // Get primary type color
  const typeColor = getTypeColor(currentPokemon.types[0]);

  return (
    <div className="evolution-chain-container">
      {/* Show First/Previous if not at the beginning */}
      {currentIndex === evolutionChain.length - 1 && currentIndex === 2 && evolutionChain[0] && (
        <>
          <EvolutionCard
            label="First"
            name={evolutionChain[0].name}
            imageUrl={evolutionChain[0].imageUrl}
            typeColor={typeColor}
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
            typeColor={typeColor}
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
            typeColor={typeColor}
          />
          <span className="evolution-arrow">&gt;</span>
        </>
      )}

      {/* Current Pokemon */}
      <EvolutionCard
        label="Current"
        name={currentPokemon.name}
        imageUrl={currentPokemon.imageUrl}
        typeColor={typeColor}
      />

      {/* Next Pokemon */}
      {nextPokemon && (
        <>
          <span className="evolution-arrow">&gt;</span>
          <EvolutionCard
            label={getLabel('next')}
            name={nextPokemon.name}
            imageUrl={nextPokemon.imageUrl}
            typeColor={typeColor}
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
            typeColor={typeColor}
          />
        </>
      )}
    </div>
  );
}