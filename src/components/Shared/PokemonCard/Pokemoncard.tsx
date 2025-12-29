import type { KeyboardEvent } from 'react';
import './Pokemoncard.css';

interface PokemonCardProps {
  label: string;        // "Previous", "Current", or "Next"
  name: string;         // Pokemon name
  imageUrl: string;     // Image URL
  typeColor: string;    // Background color from PokemonType
  onSelect?: () => void;
}

// Helper function to convert hex to rgba with opacity
function hexToRgba(hex: string, opacity: number): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (result) {
    const r = parseInt(result[1], 16);
    const g = parseInt(result[2], 16);
    const b = parseInt(result[3], 16);
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
  }
  return hex;
}

export default function PokemonCard({ label, name, imageUrl, typeColor, onSelect }: PokemonCardProps) {
  // Use white background for image area
  const imageBackgroundColor = 'rgba(255, 255, 255, 0.9)';

  const className = onSelect
    ? 'pokemon-card pokemon-card-clickable'
    : 'pokemon-card';

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (!onSelect) {
      return;
    }

    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onSelect();
    }
  };

  return (
    <div 
      className={className}
      style={{ backgroundColor: typeColor }}
      onClick={onSelect}
      onKeyDown={handleKeyDown}
      role={onSelect ? 'button' : undefined}
      tabIndex={onSelect ? 0 : undefined}
    >
      <p className="pokemon-card-label">{label}</p>
      
      <div 
        className="pokemon-card-image"
        style={{ backgroundColor: imageBackgroundColor }}
      >
        <img src={imageUrl} alt={name} />
      </div>
      
      <p className="pokemon-card-name">{name}</p>
    </div>
  );
}