import TopInfoBar from './TopInfoBar/TopInfoBar';
import PokemonImage from './ContentSection/PokemonImage/PokemonImage';
import PokemonInfo from './ContentSection/PokemonInfo/PokemonInfo';
import EvolutionChain from './EvolutionChain/EvolutionChain';
import './PokemonPage.css';
import RecommenderBox from './RecommenderBox/RecommenderBox';

export default function PokemonPage() {
  return (
    <main className="pokemon-page">
      <TopInfoBar />
      
      <div className="content-grid">
        <PokemonImage />
        <PokemonInfo />
      </div>
      
      <EvolutionChain />
      <RecommenderBox />
    </main>
  );
}