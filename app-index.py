
from flask import Flask, render_template, request
import rdflib


# searchable items are all classes, properties and named individuals.

graph = rdflib.Graph().parse('https://raw.githubusercontent.com/FIAF/FIAFcore/v1.1.0/FIAFcore.ttl', format='ttl')

def candidates(lang):
    searchable_items = list()
    for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.OWL.Class)):

        label = ''
        for a,b,c in graph.triples((s, rdflib.RDFS.label, None)):
            if c.language == lang:
                label = c

        description = 'No description.'
        for a,b,c in graph.triples((s, rdflib.URIRef('http://purl.org/dc/elements/1.1/description'), None)):
            if c.language == lang:
                description = c

        searchable_items.append({'uri':s, 'label':label, 'description':description})

    return searchable_items

candidates_en = candidates('en')
candidates_es = candidates('es')
candidates_fr = candidates('fr')

app = Flask(__name__)

def language():

    ''' Query request for language. '''

    request_lang = request.headers.get('Accept-Language').split(',')
    request_lang = [x for x in request_lang if x in ['en', 'es', 'fr']]
    if len(request_lang):
        return request_lang[0]
    else:
        return 'en'

@app.route('/', methods=['GET', 'POST'])
def home_page():

    lang = language()

    if lang == 'en':
        return render_template('index_en.html', lang=lang)

    elif lang == 'es':
        return render_template('index_es.html', lang=lang)

    elif lang == 'fr':
        return render_template('index_fr.html', lang=lang)

    else:
        raise Exception('This should not happen.')

@app.route('/search', methods=['GET', 'POST'])
def search():

    lang = language()

    if lang == 'en':
        candid = candidates_en
    elif lang == 'es':
        candid = candidates_es
    elif lang == 'fr':
        candid = candidates_fr        
    else:
        raise Exception('This should not happen.')

    if request.method == 'POST':
        search_term = request.form['search']
        search_results = [i for i in candid if search_term.lower() in i['label'].lower()]
        search_results = sorted(search_results, key=lambda d: d['label'])
       
        return render_template('search.html', search_term=search_term, search_results=search_results)
    return render_template('search.html')

if __name__ == "__main__":
    app.run(debug=True, port=5027)