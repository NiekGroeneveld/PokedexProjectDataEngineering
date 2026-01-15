import "./PokemonImage.css";
import { usePokemon } from "../../../../contexts/PokemonContext";

export default function PokemonImage() {
    const { selectedPokemon } = usePokemon();

    if (!selectedPokemon) {
        return null; // Or a placeholder if no Pokémon is selected
    }
    
    return( 
        <div className="pokemon-image-container">
            <div className = "pokemon-image">
                <img src = {selectedPokemon.imageUrl} alt = {selectedPokemon.name} />
            </div>        
        </div>
    )
}