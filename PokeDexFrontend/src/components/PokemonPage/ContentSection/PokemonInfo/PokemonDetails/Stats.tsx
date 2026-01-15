import { PokemonStats } from "../../../../../Types/Pokemon";
import "./Stats.css";

interface StatsProps {
  stats: PokemonStats;
  primaryTypeColor: string; // Hex color from the primary type
}

export default function Stats({ stats, primaryTypeColor }: StatsProps) {
  // Max stat value for calculating bar width (typical max is around 150-200)
  const MAX_STAT = 255;

  const statsData = [
    { label: "HP", value: stats.hp },
    { label: "Attack", value: stats.attack },
    { label: "Defense", value: stats.defense },
    { label: "Special Attack", value: stats.specialAttack },
    { label: "Special Defense", value: stats.specialDefense },
    { label: "Speed", value: stats.speed },
  ];

  return (
    <div className="stats-container" key={JSON.stringify(stats)}>
      <div className="stats-content">
        <div className="stats-labels">
          {statsData.map((stat) => (
            <p key={stat.label} className="stat-label">
              {stat.label}
            </p>
          ))}
        </div>
        <div className="stats-bars-container">
          {statsData.map((stat, index) => {
            const percentage = (stat.value / MAX_STAT) * 100;
            return (
              <div key={stat.label} className="stat-bar-row">
                <p className="stat-value">{stat.value}</p>
                <div className="stat-bar-track">
                  <div
                    className="stat-bar"
                    style={{
                      width: `${percentage}%`,
                      backgroundColor: primaryTypeColor,
                      animationDelay: `${index * 0.1}s`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
