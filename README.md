# FIAFcore-docs

#### Summary

This repository contains documentation for the [FIAFcore](https://github.com/FIAF/FIAFcore) ontology, built using [Docusaurus](https://github.com/facebook/docusaurus).

#### Transformation

Markdown docs are generated directly from the [ontology source file](https://raw.githubusercontent.com/FIAF/FIAFcore/main/FIAFcore.ttl), via a [Jupyter notebook](documentation.ipynb).

#### Deployment

Documentation can be deployed using the following commands on a Debian server (tested using Debian 11 x64).

```bash
# clone repo

sudo apt install git
git clone https://github.com/FIAF/FIAFcore-docs.git
cd FIAFcore-docs

# nginx config

sudo apt install nginx-full    
sudo apt install python3-certbot-nginx    
sudo apt install certbot    
sudo certbot certonly --nginx --noninteractive --agree-tos --email paulduchesne@tuta.io -d fiafcore.org    
sudo cp nginx.conf /etc/nginx/nginx.conf    
sudo systemctl restart nginx    

# install node and deploy

curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash    
sudo apt-get install -y nodejs    
screen npm run serve -- --build --port 8080 --host 0.0.0.0
```