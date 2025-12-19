import {useState, useEffect, useRef} from 'react';
import {usePokemon} from '../../../contexts/PokemonContext';
import { getAllPokemon } from '../../../data/PokemonDatabase';
import type {Pokemon} from '../../../Types/Pokemon';
import TypeCard from '../../Shared/TypeCard/TypeCard';
import './SearchBar.css';

const SEARCHABLE_POKEMON: Pokemon[] = getAllPokemon();


function SearchBar() {
    const {setSelectedPokemon} = usePokemon();
    const [searchText, setSearchText] = useState('');
    const [showDropdown, setShowDropdown] = useState(false);
    const searchRef = useRef<HTMLDivElement>(null);


    const filteredPokemon = SEARCHABLE_POKEMON.filter(pokemon => pokemon.name.toLowerCase().includes(searchText.toLowerCase()));

    // Handle click outside to close dropdown
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if(searchRef.current && !searchRef.current.contains(event.target as Node)) {
                setShowDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [])

    const handlePokemonSelect = (pokemon: Pokemon) => {
        setSelectedPokemon(pokemon);
        setSearchText('');
        setShowDropdown(false);
    }

    // Debug logging
    console.log('showDropdown:', showDropdown);
    console.log('filteredPokemon:', filteredPokemon);



    return(
        <div className="search-bar-container" ref={searchRef}>
            <input
                type="text"
                className="search-bar-input"
                placeholder="Search Pokémon..."
                value={searchText}
                onChange={(e) => {
                    setSearchText(e.target.value);
                    setShowDropdown(true);
                }}
                onFocus={() => {
                    console.log('Input focused!');
                    setShowDropdown(true);
                }}
            />

            {showDropdown && (
                <div className="search-bar-dropdown">
                    {filteredPokemon.length > 0 ? (
                        filteredPokemon.map((pokemon) => (
                            <div 
                                key={pokemon.id}
                                className="search-item"
                                onClick={() => handlePokemonSelect(pokemon)}
                            >
                                <div className="search-item-id">
                                    #{pokemon.id.toString().padStart(3, '0')}
                                </div>
                                <div className="search-item-name">
                                    {pokemon.name}
                                </div>
                                <div className="search-item-types">
                                    {pokemon.types.map((type) => (
                                        <TypeCard key={type} type={type} small={true} />
                                    ))}
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="search-item-empty">No Pokémon found</div>
                    )}
                </div>
            )}
        </div> 
    );
}

export default SearchBar;