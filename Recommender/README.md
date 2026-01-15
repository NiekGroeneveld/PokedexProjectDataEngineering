How to run??

1) Install Node dependencies
    cd api
    npm install

2) Run docker in main folder 
    docker compose up -d  

3) Load in data 
    run the load_data.sh file in your terminal
     (if it is not working try this first: hmod +x load_data.sh)
        ./load_data.sh


4)  Start the API
    cd api
    node server.js

Example: 
http://localhost:3001/api/recommend?name=charizard&limit=5

If it works you should see: 
{"target":{"id":6,"name":"Charizard"},"best":[{"id":479,"name":"Rotom","score":7},{"id":479,"name":"RotomFan Rotom","score":7},{"id":479,"name":"RotomFrost Rotom","score":7},{"id":479,"name":"RotomHeat Rotom","score":7},{"id":479,"name":"RotomMow Rotom","score":7}],"worst":[{"id":413,"name":"WormadamPlant Cloak","score":6},{"id":413,"name":"WormadamSandy Cloak","score":6},{"id":413,"name":"WormadamTrash Cloak","score":6},{"id":46,"name":"Paras","score":2},{"id":47,"name":"Parasect","score":2}]}