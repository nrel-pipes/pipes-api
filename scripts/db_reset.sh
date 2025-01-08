#!/bin/bash


# Step 1: Drop all vertices and edges in Amazon Neptune using Gremlin API
echo "Dropping all data in Amazon Neptune database..."
curl -X POST "https://${PIPES_NEPTUNE_HOST}:${PIPES_NEPTUNE_PORT}/gremlin" \
     -H 'Content-Type: application/json' \
     --data '{"gremlin": "g.V().drop()"}'
