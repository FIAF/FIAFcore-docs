# FIAFcore-docs
Documentation application for the [FIAFcore ontology](https://raw.githubusercontent.com/FIAF/FIAFcore/main/FIAFcore.ttl).

## Dev deployment

A local instance of the application can be run using the following command

>python3 app.py

## Docker deployment

The Docker image of the Flask app can be built using the following command

>docker build -t fiafcore-docs -f Dockerfile .

The instance can then be deployed using Docker Compose via the following command

> docker compose up -d
