from flask import Flask, render_template, request
import rdflib
import requests

def language():

    ''' Query request for language. '''

    request_lang = request.headers.get('Accept-Language').split(',')
    request_lang = [x for x in request_lang if x in ['en', 'es', 'fr']]
    if len(request_lang):
        return request_lang[0]
    else:
        return 'en'

app = Flask(__name__)

@app.route('/<resource>', methods=['GET', 'POST'])
def home_page(resource):

    query = '''
        prefix fiaf: <https://ontology.fiafcore.org/>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        construct where {
            values ?entity {<https://resource.fiafcore.org/'''+resource+'''>}
            ?entity rdfs:label ?entity_label .
            ?entity rdf:type ?type .
            ?type rdfs:label ?type_label .
            ?entity fiaf:hasIdentifier ?id .
            ?id fiaf:hasIdentifierValue ?id_value .
            ?id fiaf:hasIdentifierAuthority ?auth .
            ?auth rdfs:label ?auth_label .
            }
    '''

    # this would work better if you actually had authority labels

    lang = language()
    type_dict = {'en':'type', 'es':'tipo', 'fr':'type'}
    ident_dict = {'en':'identifiers', 'es':'identificadores', 'fr':'identifiants'}

    endpoint = 'https://query.fiafcore.org/repositories/fiaf-kg'
    response = requests.get(endpoint, params={'query': query}, timeout=120)
    graph = rdflib.Graph().parse(data=response.text)

    if not len(response.text):
        return render_template('404.html', colour='tomato')
    
    else:
        attributes = list()
        for s,p,o in graph.triples((rdflib.URIRef(f'https://resource.fiafcore.org/{resource}'), rdflib.RDFS.label, None)):
            label = str(o)

        for s,p,o in graph.triples((None, rdflib.RDF.type, None)):
            for a,b,c in graph.triples((o, rdflib.RDFS.label, None)):
                if c.language == lang:
                    attributes.append({'key':type_dict[lang], 'value':c, 'link':o, 'pos':0})

        for i, x in enumerate(graph.triples((None, rdflib.URIRef(f'https://ontology.fiafcore.org/hasIdentifier'), None))):
            id_value = ''
            for a,b,c in graph.triples((x[2], rdflib.URIRef(f'https://ontology.fiafcore.org/hasIdentifierValue'), None)):
                id_value += c
            for a,b,c in graph.triples((x[2], rdflib.URIRef(f'https://ontology.fiafcore.org/hasIdentifierAuthority'), None)):
                for d,e,f in graph.triples((c, rdflib.RDFS.label, None)):        
                    id_value += f' ({f})'
            attributes.append({'key':ident_dict[lang], 'value':id_value, 'link':'', 'pos': i})

        data = {'label':label, 'attributes':attributes, 'mode':'resource'}
        return render_template('page.html', data=data, colour='tomato')

if __name__ == "__main__":
    app.run(debug=True, port=5029)