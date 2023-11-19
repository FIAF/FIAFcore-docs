
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
# app.secret_key = 'your_secret_key'

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
        "nodes": [
            {
                "handle": "work",
                "label": "Work/Variant",
                "url": "WorkVariant",
                "x": 100,
                "y": 50
            },
            {
                "handle": "manifestation",
                "label": "Manifestation",
                "url": "Manifestation",
                "x": 100,
                "y": 150
            },
            {
                "handle": "item",
                "label": "Item",
                "url": "Item",
                "x": 100,
                "y": 250
            },
            {
                "handle": "carrier",
                "label": "Carrier",
                "url": "Carrier",
                "x": 100,
                "y": 350
            },
            {
                "handle": "event",
                "label": "Event",
                "url": "Event",
                "x": 350,
                "y": 200
            },
            {
                "handle": "activity",
                "label": "Activity",
                "url": "Activity",
                "x": 550,
                "y": 200
            },
            {
                "handle": "agent",
                "label": "Agent",
                "url": "Agent",
                "x": 750,
                "y": 200
            }
        ],
        "links": [
            {
                "source": "work",
                "target": "manifestation",
                "label": "Has Manfestation"
            },
            {
                "source": "manifestation",
                "target": "item",
                "label": "Has Item"
            },
            {
                "source": "item",
                "target": "carrier",
                "label": "Has Carrier"
            },
            {
                "source": "work",
                "target": "event",
                "label": "Has Event"
            },
            {
                "source": "manifestation",
                "target": "event",
                "label": "Has Event"
            },
            {
                "source": "item",
                "target": "event",
                "label": "Has Event"
            },
            {
                "source": "carrier",
                "target": "event",
                "label": "Has Event"
            },
            {
                "source": "event",
                "target": "activity",
                "label": "Has Activity"
            },
            {
                "source": "activity",
                "target": "agent",
                "label": "Has Agent"
            }
        ]
    },
    "es": {
        "nodes": [
            {
                "handle": "work",
                "label": "Obra/Variante",
                "url": "WorkVariant",
                "x": 100,
                "y": 50
            },
            {
                "handle": "manifestation",
                "label": "Manifestación",
                "url": "Manifestation",
                "x": 100,
                "y": 150
            },
            {
                "handle": "item",
                "label": "Ítem",
                "url": "Item",
                "x": 100,
                "y": 250
            },
            {
                "handle": "carrier",
                "label": "Portador",
                "url": "Carrier",
                "x": 100,
                "y": 350
            },
            {
                "handle": "event",
                "label": "Evento",
                "url": "Event",
                "x": 350,
                "y": 200
            },
            {
                "handle": "activity",
                "label": "Actividad",
                "url": "Activity",
                "x": 550,
                "y": 200
            },
            {
                "handle": "agent",
                "label": "Agente",
                "url": "Agent",
                "x": 750,
                "y": 200
            }
        ],
        "links": [
            {
                "source": "work",
                "target": "manifestation",
                "label": "Tiene una Manifestación"
            },
            {
                "source": "manifestation",
                "target": "item",
                "label": "Tiene un Item"
            },
            {
                "source": "item",
                "target": "carrier",
                "label": "Tiene Portador"
            },
            {
                "source": "work",
                "target": "event",
                "label": "Tiene un Evento"
            },
            {
                "source": "manifestation",
                "target": "event",
                "label": "Tiene un Evento"
            },
            {
                "source": "item",
                "target": "event",
                "label": "Tiene un Evento"
            },
            {
                "source": "carrier",
                "target": "event",
                "label": "Tiene un Evento"
            },
            {
                "source": "event",
                "target": "activity",
                "label": "Tiene Actividad"
            },
            {
                "source": "activity",
                "target": "agent",
                "label": "Tiene un Agente"
            }
        ]
    },
    "fr": {
        "nodes": [
            {
                "handle": "work",
                "label": "l'Œuvre/la Variante",
                "url": "WorkVariant",
                "x": 100,
                "y": 50
            },
            {
                "handle": "manifestation",
                "label": "Manifestation",
                "url": "Manifestation",
                "x": 100,
                "y": 150
            },
            {
                "handle": "item",
                "label": "Item",
                "url": "Item",
                "x": 100,
                "y": 250
            },
            {
                "handle": "carrier",
                "label": "Article",
                "url": "Carrier",
                "x": 100,
                "y": 350
            },
            {
                "handle": "event",
                "label": "Événement",
                "url": "Event",
                "x": 350,
                "y": 200
            },
            {
                "handle": "activity",
                "label": "Activité",
                "url": "Activity",
                "x": 550,
                "y": 200
            },
            {
                "handle": "agent",
                "label": "Agent",
                "url": "Agent",
                "x": 750,
                "y": 200
            }
        ],
        "links": [
            {
                "source": "work",
                "target": "manifestation",
                "label": "A une Manifestation"
            },
            {
                "source": "manifestation",
                "target": "item",
                "label": "A un Item"
            },
            {
                "source": "item",
                "target": "carrier",
                "label": "A un Article"
            },
            {
                "source": "work",
                "target": "event",
                "label": "A un Évènement"
            },
            {
                "source": "manifestation",
                "target": "event",
                "label": "A un Évènement"
            },
            {
                "source": "item",
                "target": "event",
                "label": "A un Évènement"
            },
            {
                "source": "carrier",
                "target": "event",
                "label": "A un Évènement"
            },
            {
                "source": "event",
                "target": "activity",
                "label": "A une Activité"
            },
            {
                "source": "activity",
                "target": "agent",
                "label": "A un Agent"
            }
        ]
    }
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

# legal entities

entities = []
for entity_type in [rdflib.OWL.Class, rdflib.OWL.DatatypeProperty, rdflib.OWL.ObjectProperty]:
    for s,p,o in graph.triples((None, rdflib.RDF.type, entity_type)):
        entities.append(pathlib.Path(s).name)
        
# render markdown

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

    search_entities = [rdflib.URIRef(f'https://fiafcore.org/ontology/{x}') for x in entities]
    search_options = [{'uri':x, 'label':pull_label(x, current_language)} for x in search_entities]
    entity_dict['search_term'] = translations[current_language]['search'] 
    
    search_options = sorted(search_options, key=lambda k: k['label']) 
    entity_dict['search_options'] = search_options

    return render_template('homepage.html', 
        intro=translations[current_language], 
        graph=primary_manual_translation[current_language],
        data=entity_dict, 
        lang=current_language)

@app.route('/ontology/<entity>', methods=['GET', 'POST'])
def entity_page(entity):

    if entity in entities:
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


        search_entities = [rdflib.URIRef(f'https://fiafcore.org/ontology/{x}') for x in entities]
        search_options = [{'uri':x, 'label':pull_label(x, current_language)} for x in search_entities]
        render_data['search_term'] = translations[current_language]['search'] 
        
        search_options = sorted(search_options, key=lambda k: k['label']) 
        render_data['search_options'] = search_options


        print('%%%', render_data)
        return render_template('entity_template.html', 
            lang=current_language, 
            data=render_data,
            page_type=page_type)
    else:
        return render_template('404.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
