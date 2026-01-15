import "./TopInfoBar.css";
import TypeCard from "../../Shared/TypeCard/TypeCard";
import { usePokemon } from "../../../contexts/PokemonContext";

export default function TopInfoBar() {
    const { selectedPokemon } = usePokemon();

    if (!selectedPokemon) {
        return null; // Or a placeholder if no Pokémon is selected
    }
    
    return (
        <div className="top-info-bar-container">
            <div className ="pokemon-id">
                <p>#{selectedPokemon.id.toString().padStart(3, '0')}</p>
            </div>

            <div className="pokemon-name">
                <p>{selectedPokemon.name}</p>
            </div>

            <div className="pokemon-types">
                {selectedPokemon.types.map((type) => (
                    <TypeCard key={type} type={type} />
                ))}
            </div>
        </div>
    )
}
