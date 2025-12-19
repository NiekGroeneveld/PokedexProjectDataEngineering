import Navbar from './components/NavBar/Navbar';
import PokemonPage from './components/PokemonPage/PokemonPage';
import { PokemonProvider } from './contexts/PokemonContext';
import './App.css';

function App() {
  return (
    <PokemonProvider>
      <Navbar />
      <PokemonPage />
    </PokemonProvider>
  );
}

export default App;