# FIAFcore-docs
Documentation application for the [FIAFcore](https://raw.githubusercontent.com/FIAF/FIAFcore/main/FIAFcore.ttl) ontology.

**Build images.**

The documentation web app comprises three distinct docker containers which need to be built using the following commands.

```
docker build -t fiafcore-index -f dockerfile-index .

docker build -t fiafcore-ontology -f dockerfile-ontology .

docker build -t fiafcore-resource -f dockerfile-resource .
```

Resulting images can be seen by running `docker images -a`.

***Deploy images.**

The three images can be deployed by simply running

```
docker compose up -d
```

Resulting containers can be seen by running `docker ps`.
