# build fiafcore-index image
docker build -t fiafcore-index -f dockerfile-index .

# build fiafcore-ontology image
docker build -t fiafcore-ontology -f dockerfile-ontology .

# build fiafcore-resource image
docker build -t fiafcore-resource -f dockerfile-resource .