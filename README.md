# FIAFcore-docs
Documentation application for the [FIAFcore ontology](https://raw.githubusercontent.com/FIAF/FIAFcore/main/FIAFcore.ttl).

### Index

To build and run index application, cd to `index` directory and run

```
docker build -t fiafcore-docs-index -f Dockerfile . 
```

Once image has been built it can be deployed as a standalone instance

```
docker run -d --restart=always -p 5001:5000 fiafcore-docs-index
```

Service should then be visible at localhost:5001
