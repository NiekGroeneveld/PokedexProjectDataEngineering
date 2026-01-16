# Pokémon Application

A full-stack Pokémon application with a React/TypeScript frontend, Python FastAPI backend, and GraphDB (Blazegraph) database using RDF ontologies.

## Architecture

- **Frontend**: React + TypeScript + Vite, served by Nginx
- **Backend**: Python FastAPI with SPARQL queries
- **Database**: Blazegraph (RDF triple store) with Pokémon ontology
- **Containerization**: Docker Compose for orchestration

## Prerequisites

- Docker Desktop (for Windows)
- Docker Compose
- At least 4GB RAM available for containers
- Ports 80, 5000, and 9999 available

## Project Structure

```
PokedexProject/
├── Backend/               # Python FastAPI backend
│   ├── app.py            # Main API application
│   ├── Dockerfile        # Backend container config
│   └── requirements.txt  # Python dependencies
├── PokeDexFrontend/      # React TypeScript frontend
│   ├── src/
│   │   └── services/
│   │       └── PokemonApiService.ts  # API client
│   ├── nginx.conf        # Nginx proxy configuration
│   └── Dockerfile        # Frontend container config
├── Recommender/          # Recommendation system data
│   └── data/             # RDF ontology files (.ttl)
├── ontol_kde/            # Ontology & knowledge data
│   └── global_turtle_data/  # Pokemon RDF data
└── docker-compose.yml    # Container orchestration
```

## Quick Start

### 1. Load Data into Blazegraph

Before starting the application, you need to load the Pokémon RDF data into Blazegraph.

```powershell
# Start only Blazegraph first
docker-compose up -d blazegraph

# Wait for Blazegraph to be ready (about 30 seconds)
Start-Sleep -Seconds 30

# Load the RDF data files
$files = @(
    "Recommender\data\pokemon_simple.ttl",
    "Recommender\data\pokemon_abilities_aligned.ttl",
    "Recommender\data\pokemon_evolution_links.ttl",
    "Recommender\data\pokemon_type_effectiveness_aligned.ttl"
)

foreach ($file in $files) {
    Write-Host "Loading $file..."
    curl.exe -X POST `
        -H "Content-Type: application/x-turtle" `
        --data-binary "@$file" `
        "http://localhost:9999/bigdata/namespace/kb/sparql"
}

Write-Host "Data loading complete!"
```

### 2. Start All Services

```powershell
# Build and start all containers
docker-compose up --build
```

### 3. Access the Application

- **Frontend**: http://localhost (or http://localhost:80)
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs
- **Blazegraph Admin**: http://localhost:9999/bigdata

## API Endpoints

The backend exposes the following endpoints:

### Pokémon Data
- `GET /api/pokemon` - Get all Pokémon (supports pagination)
- `GET /api/pokemon/{id}` - Get specific Pokémon by ID
- `GET /api/pokemon/search?name={name}` - Search Pokémon by name
- `GET /api/pokemon/type/{type}` - Filter Pokémon by type
- `GET /api/pokemon/evolution-chain/{id}` - Get evolution chain

### Recommendations
- `GET /api/recommendations?pokemon_id={id}&limit={n}` - Get type-based recommendations

### Statistics
- `GET /api/stats` - Get database statistics

## Development

### Frontend Development

```powershell
cd PokeDexFrontend
npm install
npm run dev
```

Access at http://localhost:5173

### Backend Development

```powershell
cd Backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 5000
```

Access at http://localhost:5000

## Stopping the Application

```powershell
# Stop all containers
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

## Troubleshooting

### Containers won't start
```powershell
# Check container logs
docker-compose logs backend
docker-compose logs blazegraph
docker-compose logs frontend

# Restart specific service
docker-compose restart backend
```

### Database connection errors
```powershell
# Verify Blazegraph is running
curl http://localhost:9999/bigdata/

# Check if data is loaded
curl "http://localhost:9999/bigdata/namespace/kb/sparql?query=SELECT%20(COUNT(*)%20AS%20?count)%20WHERE%20{%20?s%20?p%20?o%20}"
```

### Frontend can't connect to backend
1. Check nginx.conf has correct proxy settings
2. Verify backend is accessible: `curl http://localhost:5000/`
3. Check browser console for CORS errors

### Port conflicts
If ports 80, 5000, or 9999 are already in use:

1. Edit docker-compose.yml
2. Change port mappings (e.g., `"8080:80"` instead of `"80:80"`)
3. Restart containers

## Data Sources

- **Pokémon Images**: PokeAPI (https://pokeapi.co/)
- **RDF Ontology**: Custom ontology in `Recommender/data/` and `ontol_kde/`
- **Type Effectiveness**: Stored in RDF triple store

## Technologies Used

- **Frontend**: React 18, TypeScript, Vite, CSS
- **Backend**: FastAPI, Python 3.11, Uvicorn
- **Database**: Blazegraph 2.1.5 (RDF triple store)
- **Query Language**: SPARQL
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx 1.27

## Notes

- The application uses RDF ontologies for semantic data representation
- Pokémon images are fetched from PokeAPI on-demand
- The recommendation system uses type effectiveness relationships
- All data queries use SPARQL for flexible semantic queries

## Contributing

When adding new features:
1. Update the ontology files if adding new data types
2. Add corresponding API endpoints in `Backend/app.py`
3. Update the frontend service in `PokemonApiService.ts`
4. Test with Docker Compose before committing

## License

This project is for educational purposes.
