import "./Abilities.css";

interface AbilitiesProps {
  abilities: string[];
  primaryTypeColor: string; // Hex color from the primary type
}

export default function Abilities({ abilities, primaryTypeColor }: AbilitiesProps) {
  return (
    <div 
      className="abilities-container" 
      style={{ backgroundColor: primaryTypeColor }}
    >
      <p className="abilities-title">Abilities</p>
      <div className="abilities-list">
        {abilities.map((ability, index) => (
          <p key={index} className="ability-item">{ability}</p>
        ))}
      </div>
    </div>
  );
}
