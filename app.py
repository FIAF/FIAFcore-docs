
from flask import Flask, render_template, url_for, jsonify, request, session
from flask_language import Language, current_language
import json
import numpy
import pathlib
import pydash
import rdflib

def pull_label(entity, language):

    ''' Pull first available label for entity. '''

    label = [o for s,p,o in graph.triples((entity, rdflib.RDFS.label, None)) if o.language == language]
    if not len(label):
        return "Label required."
    else:
        return str(label[0])
    
def pull_attributes(ee, key, lang):

    ''' Pull information about the entity from the graph. '''

    query = '''
        select distinct ?class ?label ?superclass ?subclass ?properties ?domain ?union_domain ?range ?reference 
        where {
            values ?subject {<https://fiafcore.org/ontology/'''+ee+'''>}
            values ?language {"'''+lang+'''"}
            ?subject rdf:type ?class .
            optional { 
                ?subject rdfs:label ?label . 
                filter (lang (?label) = ?language) . }
            optional { ?subject rdfs:subClassOf ?superclass . }
            optional { ?subclass rdfs:subClassOf ?subject . }
            optional { ?properties rdfs:domain ?subject . }
            optional { ?subject rdfs:domain ?domain . }
            optional {
                ?subject rdfs:domain ?domain .
                ?domain owl:unionOf ?a . 
                ?a rdf:rest*/rdf:first ?union_domain . }
            optional { ?subject rdfs:range ?range . }
            optional { 
                ?subject <http://purl.org/dc/elements/1.1/source> ?reference . 
                filter (lang (?reference) = ?language) . } 
            } '''

    result = pydash.uniq([r[key] for r in graph.query(query)])
    result = [x for x in result if not isinstance(x, type(None))]
    result = [x for x in result if not isinstance(x, type(rdflib.BNode('')))]
    result = sorted(result)

    if len(result) < 1:
        return []
    elif isinstance(result[0], type(rdflib.Literal(''))):
        return [str(x) for x in result]
    elif type(result[0]) == type(rdflib.URIRef('')):
        entity_list = [{'link':x, 'label':pull_label(x, lang)} for x in result]
        return sorted(entity_list, key=lambda x: x['label'])
    else:
        raise Exception('Unexpected result.')

app = Flask(__name__)
lang = Language(app)
app.secret_key = 'your_secret_key'

@lang.allowed_languages
def get_allowed_languages():
    return ['en', 'es', 'fr']

@lang.default_language
def get_default_language():
    return 'en'

@app.route('/api/language')
def get_language():
    print(str(current_language))
    return jsonify({
        'language': str(current_language),
    })

primary_manual_translation = {
    "en": {
        "work": "Work/Variant",
        "manifestation": "Manifestation",
        "item": "Item",
        "carrier": "Carrier",
        "event": "Event",
        "activity": "Activity",
        "agent": "Agent",
    },
    "es": {
        "work": "Obra/Variante", 
        "manifestation": "Manifestación",
        "item": "Ítem",
        "carrier": "Portador",
        "event": "Evento",
        "activity": "Actividad",
        "agent": "Agente",
    },
    "fr": {
        "work": "l'Œuvre/la Variante",
        "manifestation": "Manifestation",
        "item": "Item",
        "carrier": "Article",
        "event": "Événement",
        "activity": "Activité",
        "agent": "Agent"
    },
}

graph = rdflib.Graph()
graph.parse('https://raw.githubusercontent.com/FIAF/FIAFcore/main/FIAFcore.ttl', format='ttl')

# parsing work to remove all unionOf nodes
# while these are required in the ontology, they would be confusing in the documentation

query = ''' 
    select ?subject ?union_domain where {
        ?subject rdfs:domain ?domain .
        ?domain owl:unionOf ?a .
        ?a rdf:rest*/rdf:first ?union_domain .
    } '''

# add direct domain statements

for a, b in graph.query(query):
    graph.add((a, rdflib.RDFS.domain, b))

# remove blank node statements

for a,b,c in graph.triples((None, None, None)):
    if type(a) == type(rdflib.BNode('')) or type(b) == type(rdflib.BNode('')):
        graph.remove(( a, b, c))

# manually add some labelling here, for classes eg
# ideally these should also be translated

for l in ['en', 'es', 'fr']:
    graph.add((rdflib.URIRef('http://www.w3.org/2002/07/owl#Class'), rdflib.RDFS.label, rdflib.Literal('Class', lang=l)))
    graph.add((rdflib.URIRef('http://www.w3.org/2002/07/owl#ObjectProperty'), rdflib.RDFS.label, rdflib.Literal('Object Property', lang=l)))
    graph.add((rdflib.URIRef('http://www.w3.org/2002/07/owl#DatatypeProperty'), rdflib.RDFS.label, rdflib.Literal('Datatype Property', lang=l)))

with open(pathlib.Path.cwd() / 'static' / 'translations.json') as translations:
    translations = json.load(translations)

@app.route('/', methods=['GET', 'POST'])
@app.route('/ontology/', methods=['GET', 'POST'])
def home_page():

    if request.method == 'POST':

        print('hello', request.form['lang'])
        lang.change_language(request.form['lang'])

    entity_dict = dict()

    primary_classes = [
        'WorkVariant',
        'Manifestation',
        'Item',
        'Carrier',
        'Event',
        'Activity',
        'Agent'
    ]
    
    primary_classes = [rdflib.URIRef(f'https://fiafcore.org/ontology/{x}') for x in primary_classes]
    primary = [{'uri':x, 'label':pull_label(x, current_language)} for x in primary_classes]
    entity_dict['primary'] = {'label':translations[current_language]['primary'], 'data': primary} 
    entity_dict['resources'] = {'label':translations[current_language]['resources']}
    entity_dict['contact'] = {'label':translations[current_language]['contact']}

    return render_template('homepage.html', 
        intro=translations[current_language], 
        graph=primary_manual_translation[current_language],
        data=entity_dict, 
        lang=current_language)

@app.route('/ontology/<entity>', methods=['GET', 'POST'])
def entity_page(entity):

    if request.method == 'POST':
       lang.change_language(request.form['lang'])
 
    combined_domains = pull_attributes(entity, 'domain', current_language)
    combined_domains += pull_attributes(entity, 'union_domain', current_language)
    type_state = pull_attributes(entity, 'class', current_language)[0]['link']

    if str(type_state) == 'http://www.w3.org/2002/07/owl#Class':
        page_type = 'class'
    else:
        page_type = 'property'
        
    render_data = {'label': pull_attributes(entity, 'label', current_language)[0]}
    render_data['type_gate'] = str(pull_attributes(entity, 'class', current_language)[0]['link'])
    render_data['entity_type'] = {'label': translations[current_language]['type'], 'instances': pull_attributes(entity, 'class', current_language)}
    render_data['reference'] = {'label': translations[current_language]['reference'], 'instances': pull_attributes(entity, 'reference', current_language)}
    render_data['superclass'] = {'label': translations[current_language]['superclass'], 'instances': pull_attributes(entity, 'superclass', current_language)}
    render_data['subclass'] = {'label': translations[current_language]['subclass'], 'instances': pull_attributes(entity, 'subclass', current_language)}
    render_data['properties'] = {'label': translations[current_language]['properties'], 'instances': pull_attributes(entity, 'properties', current_language)}
    render_data['domain'] = {'label': translations[current_language]['domain'], 'instances': combined_domains}
    render_data['range'] = {'label': translations[current_language]['range'], 'instances': pull_attributes(entity, 'range', current_language)}
    render_data['description'] = {'label': translations[current_language]['description'], 'instances': []}
    render_data['none'] = translations[current_language]['none']

    return render_template('entity_template.html', 
        lang=current_language, 
        data=render_data,
        page_type=page_type)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
