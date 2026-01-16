# Troubleshooting Guide

## Common Issues and Solutions

### 1. Blazegraph Won't Start

**Symptoms:**
- `docker-compose up` shows Blazegraph container exiting
- Error: "Address already in use"

**Solutions:**
```powershell
# Check if port 9999 is in use
netstat -ano | findstr :9999

# Kill the process if needed (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change the port in docker-compose.yml
# Change "9999:8080" to "9998:8080" or another available port
```

### 2. Backend Can't Connect to Blazegraph

**Symptoms:**
- Backend logs show connection errors
- API returns 500 errors

**Solutions:**
```powershell
# Check if Blazegraph is accessible
curl http://localhost:9999/bigdata/

# Check Docker network
docker network inspect pokedexproject_pokemon-network

# Restart backend
docker-compose restart backend

# Check backend logs
docker-compose logs -f backend
```

### 3. Frontend Shows Empty Page

**Symptoms:**
- Browser shows blank page
- Console shows network errors

**Solutions:**
```powershell
# Check if frontend is running
curl http://localhost/

# Check nginx logs
docker-compose logs frontend

# Verify nginx.conf is correctly configured
docker exec -it pokemon-frontend cat /etc/nginx/conf.d/default.conf

# Rebuild frontend
docker-compose up -d --build frontend
```

### 4. API Returns Empty Results

**Symptoms:**
- `/api/pokemon` returns empty array
- No Pokemon data available

**Solutions:**
```powershell
# Check if data is loaded in Blazegraph
curl "http://localhost:9999/bigdata/namespace/kb/sparql?query=SELECT%20(COUNT(*)%20AS%20?count)%20WHERE%20{%20?s%20?p%20?o%20}"

# If count is 0, reload data
.\load-data.ps1

# Check RDF file paths exist
ls Recommender\data\*.ttl
```

### 5. CORS Errors in Browser

**Symptoms:**
- Browser console: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solutions:**
1. Verify backend CORS settings in `Backend/app.py`
2. Use nginx proxy instead of direct backend access
3. Access frontend via `http://localhost` not `http://localhost:5173`

### 6. Images Not Loading

**Symptoms:**
- Pokemon cards show broken images

**Solutions:**
```powershell
# Verify PokeAPI is accessible
curl https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png

# Check if backend is generating correct URLs
curl http://localhost:5000/api/pokemon/25

# Verify imageUrl field in response
```

### 7. Port Already in Use

**Symptoms:**
- Error: "port is already allocated"

**Solutions:**
```powershell
# Find what's using the port (e.g., port 80)
netstat -ano | findstr :80

# Stop the process or change docker-compose.yml ports
# Edit docker-compose.yml:
# frontend:
#   ports:
#     - "8080:80"  # Use 8080 instead of 80
```

### 8. Docker Build Fails

**Symptoms:**
- `docker-compose build` fails
- Error during npm install or pip install

**Solutions:**
```powershell
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check for network issues
# Try using a different network/VPN

# Verify Dockerfile syntax
docker build -t test ./Backend
```

### 9. TypeScript Errors in Frontend

**Symptoms:**
- Frontend won't compile
- Type errors related to Pokemon

**Solutions:**
```powershell
cd PokeDexFrontend

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check TypeScript version
npm ls typescript

# Verify types are correct
npm run build
```

### 10. Data Loading Fails

**Symptoms:**
- load-data.ps1 shows errors
- curl returns error when posting TTL files

**Solutions:**
```powershell
# Verify file encoding (should be UTF-8)
# Check file exists
Test-Path Recommender\data\pokemon_simple.ttl

# Try loading manually
curl -X POST `
  -H "Content-Type: application/x-turtle" `
  --data-binary "@Recommender\data\pokemon_simple.ttl" `
  "http://localhost:9999/bigdata/namespace/kb/sparql"

# Check Blazegraph UI
# Visit http://localhost:9999/bigdata
# Go to "UPDATE" tab and manually upload TTL files
```

## Diagnostic Commands

### Check All Services Status
```powershell
docker-compose ps
```

### View All Logs
```powershell
docker-compose logs -f
```

### View Specific Service Logs
```powershell
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f blazegraph
```

### Test Backend API
```powershell
# Health check
curl http://localhost:5000/

# Get Pokemon
curl http://localhost:5000/api/pokemon/25

# Search
curl "http://localhost:5000/api/pokemon/search?name=pika"

# Stats
curl http://localhost:5000/api/stats
```

### Test Blazegraph SPARQL
```powershell
# Count triples
$query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
$encoded = [System.Uri]::EscapeDataString($query)
curl "http://localhost:9999/bigdata/namespace/kb/sparql?query=$encoded"

# List Pokemon
$query = "PREFIX ex: <http://example.org/> SELECT ?name WHERE { ?p a ex:Pokemon ; ex:name ?name } LIMIT 10"
$encoded = [System.Uri]::EscapeDataString($query)
curl "http://localhost:9999/bigdata/namespace/kb/sparql?query=$encoded"
```

### Check Network Connectivity
```powershell
# From host to containers
curl http://localhost:5000/
curl http://localhost:9999/bigdata/
curl http://localhost/

# Between containers
docker exec pokemon-backend curl http://blazegraph:8080/bigdata/
```

### Clean Restart
```powershell
# Stop everything
docker-compose down

# Remove volumes (WARNING: deletes database)
docker-compose down -v

# Remove all containers and images
docker-compose down --rmi all

# Start fresh
.\start.ps1
```

## Performance Issues

### Slow API Responses

1. Check SPARQL query complexity
2. Add indexes in Blazegraph
3. Limit result sets with LIMIT clause
4. Use caching in frontend

### High Memory Usage

1. Reduce `JAVA_XMX` in docker-compose.yml
2. Limit concurrent requests
3. Restart containers periodically

### Docker Using Too Much Disk

```powershell
# Clean up unused resources
docker system prune -a --volumes

# Check disk usage
docker system df
```

## Getting Help

If none of these solutions work:

1. **Check logs thoroughly:**
   ```powershell
   docker-compose logs --tail=100
   ```

2. **Verify file structure:**
   ```powershell
   tree /F
   ```

3. **Check Docker resources:**
   - Open Docker Desktop
   - Ensure enough RAM allocated (minimum 4GB)
   - Ensure enough disk space

4. **Test components individually:**
   ```powershell
   # Test only Blazegraph
   docker-compose up blazegraph
   
   # Test backend alone
   cd Backend
   pip install -r requirements.txt
   python app.py
   ```

5. **Check versions:**
   ```powershell
   docker --version
   docker-compose --version
   node --version
   python --version
   ```
