import type { PokemonType } from "../../../Types/PokemonType";
import { getTypeColor } from "../../../Types/PokemonType";
import "./TypeCard.css";

interface TypeCardProps {
  type: PokemonType;
  small?: boolean;
}

export default function TypeCard({ type, small = false }: TypeCardProps) {
  const color = getTypeColor(type);
  
    return (
    <div 
      className={`type-card ${small ? 'type-card-small' : ''}`}
      style={{ backgroundColor: color }}
    >
      <p>{type}</p>
    </div>
  );
}