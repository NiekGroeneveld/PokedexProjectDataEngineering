import './EvolutionCard.css';

interface EvolutionCardProps {
  label: string;        // "Previous", "Current", or "Next"
  name: string;         // Pokemon name
  imageUrl: string;     // Image URL
  typeColor: string;    // Background color from PokemonType
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

export default function EvolutionCard({ label, name, imageUrl, typeColor }: EvolutionCardProps) {
  // Use white background for image area
  const imageBackgroundColor = 'rgba(255, 255, 255, 0.9)';

  return (
    <div 
      className="evolution-card"
      style={{ backgroundColor: typeColor }}
    >
      <p className="evolution-card-label">{label}</p>
      
      <div 
        className="evolution-card-image"
        style={{ backgroundColor: imageBackgroundColor }}
      >
        <img src={imageUrl} alt={name} />
      </div>
      
      <p className="evolution-card-name">{name}</p>
    </div>
  );
}