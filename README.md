# Pokemon Pokedex Application

## Quick Start

Run the entire application with Docker Compose:

```bash
docker-compose up -d --build
```

The application will be available at:
- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:5000
- **Recommender Service**: http://localhost:3001
- **Blazegraph Database**: http://localhost:9999

To stop the application:

```bash
docker-compose down
```

## Features

### Pokemon Database
Browse and search through a comprehensive Pokemon database stored in an RDF/SPARQL knowledge graph (Blazegraph).

### Detailed Pokemon Information
- View stats (HP, Attack, Defense, Speed, etc.)
- See types and abilities
- Check height, weight, and category
- Display accurate images for all forms (base, Mega, regional variants)

### Evolution Chains
Navigate through Pokemon evolution paths with visual cards showing previous, current, and next evolutions.

### Type-Based Recommendations
Get strategic recommendations showing:
- **Losing Matches**: Pokemon that counter your selected Pokemon (strong against it)
- **Winning Matches**: Pokemon that your selected Pokemon counters (weak to it)

## Architecture

- **Frontend**: React + TypeScript with Vite
- **Backend**: FastAPI (Python) with modular architecture
- **Database**: Blazegraph RDF triple store with SPARQL queries
- **Recommender**: Node.js Express service for type effectiveness analysis
- **Data Source**: Pokemon.com for images, PokeAPI for supplementary data
