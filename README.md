# FIAFcore-docs
Documentation application for the [FIAFcore ontology](https://raw.githubusercontent.com/FIAF/FIAFcore/main/FIAFcore.ttl).

### Local

A local instance of the documentation can be run using the following command

>python3 app.py

### Production

The Docker image of the Flask app can be built using the following command

>docker build -t fiafcore-docs -f Dockerfile .

The instance can be deployed using Docker Compose via the following command

> docker compose up -d