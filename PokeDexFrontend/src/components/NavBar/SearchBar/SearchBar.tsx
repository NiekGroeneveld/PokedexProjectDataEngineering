import {useState, useEffect, useRef} from 'react';
import {usePokemon} from '../../../contexts/PokemonContext';
import { getSearchList, getPokemonByName } from '../../../services/PokemonApiService';
import type {Pokemon} from '../../../Types/Pokemon';
import TypeCard from '../../Shared/TypeCard/TypeCard';
import './SearchBar.css';


function SearchBar() {
    const {setSelectedPokemon} = usePokemon();
    const [searchText, setSearchText] = useState('');
    const [showDropdown, setShowDropdown] = useState(false);
    const [allPokemon, setAllPokemon] = useState<Pokemon[]>([]);
    const [loading, setLoading] = useState(true);
    const searchRef = useRef<HTMLDivElement>(null);

    // Load Pokemon search list on component mount (lightweight)
    useEffect(() => {
        async function loadPokemon() {
            try {
                const pokemon = await getSearchList(1000);
                console.log('Loaded search list count:', pokemon.length);
                setAllPokemon(pokemon);
            } catch (error) {
                console.error('Failed to load search list:', error);
            } finally {
                setLoading(false);
            }
        }
        loadPokemon();
    }, []);

    const filteredPokemon = searchText.trim() 
        ? allPokemon
            .filter(pokemon => pokemon.name.toLowerCase().includes(searchText.toLowerCase()))
            .slice(0, 20) // Limit to 20 results for performance
        : [];

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

    const handlePokemonSelect = async (pokemon: Pokemon) => {
        // Fetch full Pokemon data by name to get the exact form selected from the search
        const fullPokemon = await getPokemonByName(pokemon.name);
        if (fullPokemon) {
            setSelectedPokemon(fullPokemon);
        }
        setSearchText('');
        setShowDropdown(false);
    }

    // Debug logging
    console.log('searchText:', searchText);
    console.log('filteredPokemon count:', filteredPokemon.length);
    if (filteredPokemon.length > 0 && filteredPokemon.length <= 5) {
        console.log('filteredPokemon:', filteredPokemon.map(p => p.name));
    }

    return(
        <div className="search-bar-container" ref={searchRef}>
            <input
                type="text"
                className="search-bar-input"
                placeholder="Search Pokémon..."
                value={searchText}
                onChange={(e) => {
                    setSearchText(e.target.value);
                    setShowDropdown(e.target.value.trim().length > 0);
                }}
                onFocus={() => {
                    if (searchText.trim().length > 0) {
                        setShowDropdown(true);
                    }
                }}
            />

            {showDropdown && (
                <div className="search-bar-dropdown" data-filtered-count={filteredPokemon.length} key={searchText}>
                    {loading ? (
                        <div className="search-item-empty">Loading...</div>
                    ) : filteredPokemon.length > 0 ? (
                        filteredPokemon.map((pokemon, index) => (
                            <div 
                                key={`${pokemon.id}-${pokemon.name}-${index}`}
                                className="search-item"
                                onClick={() => handlePokemonSelect(pokemon)}
                                data-pokemon-name={pokemon.name}
                                data-index={index}
                            >
                                <div className="search-item-id">
                                    #{pokemon.id.toString().padStart(3, '0')}
                                </div>
                                <div className="search-item-name">
                                    {pokemon.name}
                                </div>
                                <div className="search-item-types">
                                    {pokemon.types.map((type, typeIndex) => (
                                        <TypeCard key={`${type}-${typeIndex}`} type={type} small={true} />
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