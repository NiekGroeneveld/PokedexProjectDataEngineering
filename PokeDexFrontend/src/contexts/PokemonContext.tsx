import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import { Pokemon } from '../Types/Pokemon';

// Define the shape of the context
interface PokemonContextType {
  selectedPokemon: Pokemon | null;
  setSelectedPokemon: (pokemon: Pokemon | null) => void;
}

// Create the context with a default value
const PokemonContext = createContext<PokemonContextType | undefined>(undefined);

// Provider component
interface PokemonProviderProps {
  children: ReactNode;
}

export const PokemonProvider = ({ children }: PokemonProviderProps) => {
  const [selectedPokemon, setSelectedPokemon] = useState<Pokemon | null>(null);

  return (
    <PokemonContext.Provider value={{ selectedPokemon, setSelectedPokemon }}>
      {children}
    </PokemonContext.Provider>
  );
};

// Custom hook to use the Pokemon context
export const usePokemon = () => {
  const context = useContext(PokemonContext);
  
  if (context === undefined) {
    throw new Error('usePokemon must be used within a PokemonProvider');
  }
  
  return context;
};
