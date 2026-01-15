import './Navbar.css';
import PokemonLogo from '../../assets/Pokedexlogo.png';
import SearchBar from './SearchBar/SearchBar';

export default function Navbar() {
    return(
        <nav className = "navbar">
            <div className = "navbar-logo">
                <img
                    src = {PokemonLogo}
                    alt = "Pokemon Logo"
                />
            </div>

            <SearchBar />

            <div className = "navbar-right">
                {/* Future right-aligned navbar items can be added here */}
            </div>
        </nav>
    )
}