
from flask import Flask, render_template, request
import json
import pathlib
import rdflib

with open(pathlib.Path.cwd() / 'static' / 'summary.json') as data:
    data = json.load(data)

# searchable items are all classes, properties and named individuals.

graph = rdflib.Graph().parse('https://raw.githubusercontent.com/FIAF/FIAFcore/v1.1.0/FIAFcore.ttl', format='ttl')

searchable_items = list()
for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.OWL.Class)):

    label = ''
    for a,b,c in graph.triples((s, rdflib.RDFS.label, None)):
        if c.language == 'en':
            label = c

    description = 'No description.'
    for a,b,c in graph.triples((s, rdflib.URIRef('http://purl.org/dc/elements/1.1/description'), None)):
        if c.language == 'en':
            description = c

    searchable_items.append({'uri':s, 'label':label, 'description':description})

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home_page():

    accept_language_header = request.headers.get('Accept-Language')
    print('@@@', accept_language_header)

    # if en,es,fr in here translate, otherwise en as fallback?

    return render_template('index.html', data=data)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search']
        search_results = [i for i in searchable_items if search_term.lower() in i['label'].lower()]
        search_results = sorted(search_results, key=lambda d: d['label'])
       
        return render_template('search.html', search_term=search_term, search_results=search_results)
    return render_template('search.html')

if __name__ == "__main__":
    app.run(debug=True, port=5027)