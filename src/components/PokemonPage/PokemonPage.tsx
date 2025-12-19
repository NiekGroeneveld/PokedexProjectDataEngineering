import TopInfoBar from './TopInfoBar/TopInfoBar';
import PokemonImage from './ContentSection/PokemonImage/PokemonImage';
import PokemonInfo from './ContentSection/PokemonInfo/PokemonInfo';
import EvolutionChain from './EvolutionChain/EvolutionChain';
import './PokemonPage.css';

export default function PokemonPage() {
  return (
    <main className="pokemon-page">
      <TopInfoBar />
      
      <div className="content-grid">
        <PokemonImage />
        <PokemonInfo />
      </div>
      
      <EvolutionChain />
    </main>
  );
}