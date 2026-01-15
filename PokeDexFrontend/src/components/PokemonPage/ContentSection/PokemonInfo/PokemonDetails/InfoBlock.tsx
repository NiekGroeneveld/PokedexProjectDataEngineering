import "./InfoBlock.css";

interface InfoBlockProps {
  height: number; // in decimetres
  weight: number; // in hectograms
  category: string;
}

export default function InfoBlock({ height, weight, category }: InfoBlockProps) {
  // Convert height from decimetres to feet and inches
  const heightInInches = height * 3.937;
  const feet = Math.floor(heightInInches / 12);
  const inches = Math.round(heightInInches % 12);
  
  // Convert weight from hectograms to pounds
  const weightInPounds = (weight * 0.2204623).toFixed(1);

  return (
    <div className="info-block">
      <p className="info-label">Height</p>
      <p className="info-value">{feet}' {inches.toString().padStart(2, '0')}"</p>
      
      <p className="info-label">Weight</p>
      <p className="info-value">{weightInPounds} lbs</p>
      
      <p className="info-label">Category</p>
      <p className="info-value">{category}</p>
    </div>
  );
}
