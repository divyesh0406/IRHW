echo '{
  "query": "{
    Get{
      SimSearch (
        limit: 3
        nearText: {
          concepts: [\"indian songs\"],
        }
      ){
        musicGenre
        songTitle
        artist
      }
    }
  }"
}'  | curl -s \
    -X POST \
    -H 'Content-Type: application/json' \
    -d @- \
    localhost:8080/v1/graphql
