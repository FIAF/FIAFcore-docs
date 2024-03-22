# FIAFcore-docs
Documentation for the [FIAFcore](https://github.com/FIAF/FIAFcore) ontology.

**Build**

The documentation web app comprises three distinct docker containers which can be built using the following script.

```
./build.sh
```

Resulting images can be seen by running `docker images -a`.

**Deploy**

The three images can then be deployed by simply running

```
docker compose up -d
```

Resulting containers can be seen by running `docker ps`.
