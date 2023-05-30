
from flask import Flask, render_template, url_for, jsonify, request, session
from flask_language import Language, current_language
import json
import rdflib

# language updates.
# read default and changing working as expected, 
# now mission is to be able to toggle using gui element
# and also route different data based on lang variable.

intro = {
    "en": {
        "link1": "FIAFcore",
        "text1": " is an ontology for film archives, based primarily on the",
        "link2": "FIAF Cataloguing Manual",
        "text2": ". It is intended to facilitate data harmonisation and exchange between institutions."
    },
    "es": {
        "link1": "FIAFcore",
        "text1": " es una ontología para archivos fílmicos, basada principalmente en el",
        "link2": "Manual FIAF de Catalogación",
        "text2": ". Su objetivo es facilitar la armonización y el intercambio de datos entre instituciones."
    },
    "fr": {
        "link1": "FIAFcore",
        "text1": " est une ontologie pour les archives cinématographiques, basée principalement sur",
        "link2": "Le Manuel de catalogage de la FIAF",
        "text2": ". Elle est destinée à faciliter l'harmonisation et l'échange de données entre les institutions."
    }
}

elements = {
    "primary": {
        "en": "primary classes",
        "es": "clases primarias",
        "fr": "classes primaires"
    },
    "resources": {
        "en": "resources",
        "es": "recursos",
        "fr": "ressources"
    },
    "contact": {
        "en": "contact",
        "es": "contacto",
        "fr": "contact"
    },
    "type": {
        "en": "type",
        "es": "tipo",
        "fr": "type"
    },
    "reference": {
        "en": "reference",
        "es": "referencia",
        "fr": "référence"
    },
    "superclass": {
        "en": "superclass",
        "es": "superclase",
        "fr": "super-classe"
    },
    "subclass": {
        "en": "subclass",
        "es": "subclase",
        "fr": "sous-classe"
    },
    "properties": {
        "en": "properties",
        "es": "propiedades",
        "fr": "propriétés"
    },
    "description": {
        "en": "description",
        "es": "descripción",
        "fr": "description"
    },
    "domains": {
        "en": "domain",
        "es": "dominio",
        "fr": "domaine"
    },
    "ranges": {
        "en": "range",
        "es": "rango",
        "fr": "étendue"
    },
    "none": {
        "en": "None",
        "es": "Ninguno",
        "fr": "Aucun"
    }
}

def pull_label(entity):

    ''' Pull first available label for entity. '''

    label = [o for s,p,o in graph.triples((entity, rdflib.RDFS.label, None)) if o.language == 'en'] # this is where we tweak language for labels
    if not len(label):
        return "Label required."
    else:
        return str(label[0])

def pull_label_multi(entity, language):

    ''' Pull first available label for entity. '''

    label = [o for s,p,o in graph.triples((entity, rdflib.RDFS.label, None)) if o.language == language] # this is where we tweak language for labels
    if not len(label):
        return "Label required."
    else:
        return str(label[0])

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

graph = rdflib.Graph()
graph.parse('https://raw.githubusercontent.com/FIAF/FIAFcore/main/FIAFcore.ttl', format='ttl')

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
    primary = [{'uri':x, 'label':pull_label_multi(x, current_language)} for x in primary_classes]
    entity_dict['primary'] = {'label':elements['primary'][current_language], 'data': primary} 
    entity_dict['resources'] = {'label':elements['resources'][current_language]}
    entity_dict['contact'] = {'label':elements['contact'][current_language]}

    return render_template('homepage.html', intro=intro[current_language], data=entity_dict, lang=current_language)

@app.route('/ontology/<entity>', methods=['GET', 'POST'])
def entity_page(entity):

    if request.method == 'POST':

        print('hello', request.form['lang'])
        lang.change_language(request.form['lang'])
 
    entity_uri = rdflib.URIRef(f'https://fiafcore.org/ontology/{entity}')
    entity_dict = {'entity':entity_uri, 'label':pull_label_multi(entity_uri, current_language)} 
    class_triples = [s for s,p,o in graph.triples((entity_uri, rdflib.RDF.type, rdflib.OWL.Class))]
    object_property_triples = [s for s,p,o in graph.triples((entity_uri, rdflib.RDF.type, rdflib.OWL.ObjectProperty))]

    if len(class_triples):

        entity_type = [{'uri':str(o), 'label':str(o)} for s,p,o in graph.triples((entity_uri, rdflib.RDF.type, None))]
        entity_dict['entity_type'] = {'label':elements['type'][current_language], 'data':sorted(entity_type, key=lambda d: d['label'])} 

        superclasses = [{'uri':o, 'label':pull_label_multi(o, current_language)} for s,p,o in graph.triples((entity_uri, rdflib.RDFS.subClassOf, None))]
        entity_dict['superclasses'] = {'label':elements['superclass'][current_language], 'data': sorted(superclasses, key=lambda d: d['label'])} 

        # following two calls are the same and could be a function.

        subclasses = [{'uri':s, 'label':pull_label_multi(s, current_language)} for s,p,o in graph.triples((None, rdflib.RDFS.subClassOf, entity_uri))]
        entity_dict['subclasses'] = {'label':elements['subclass'][current_language], 'data': sorted(subclasses, key=lambda d: d['label'])} 

        properties = [{'uri':s, 'label':pull_label_multi(s, current_language), 'short':str(s).replace('https://fiafcore.org/ontology/', 'fiaf:')} for s,p,o in graph.triples((None, rdflib.RDFS.domain, entity_uri))]
        entity_dict['properties'] = {'label':elements['properties'][current_language], 'data': properties}
        
        reference = [str(o) for s,p,o in graph.triples((entity_uri, rdflib.URIRef('http://purl.org/dc/elements/1.1/source'), None))]
        entity_dict['reference'] = {'label':elements['reference'][current_language], 'data': reference}

        entity_dict['description'] = {'label':elements['description'][current_language], 'data': ''}

        entity_dict['none'] = {'label':elements['none'][current_language]}


        # search_options = [pull_label_multi(s, current_language) for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.OWL.Class))]
        # print('search options', search_options )
        # entity_dict['search_options'] = sorted(search_options)
        
        return render_template('class_template.html', data=entity_dict, lang=current_language)

    elif len(object_property_triples):

        entity_type = [{'uri':str(o), 'label':str(o)} for s,p,o in graph.triples((entity_uri, rdflib.RDF.type, None))]
        entity_dict['entity_type'] = {'label':elements['type'][current_language], 'data':sorted(entity_type, key=lambda d: d['label'])} 

        domains = [{'uri':o, 'label':pull_label_multi(o, current_language)} for s,p,o in graph.triples((entity_uri, rdflib.RDFS.domain, None))]
        entity_dict['domains'] = {'label':elements['domains'][current_language], 'data': sorted(domains, key=lambda d: d['label'])} 

        ranges = [{'uri':o, 'label':pull_label_multi(o, current_language)} for s,p,o in graph.triples((entity_uri, rdflib.RDFS.range, None))]
        entity_dict['ranges'] = {'label':elements['ranges'][current_language], 'data': sorted(ranges, key=lambda d: d['label'])} 

        reference = [str(o) for s,p,o in graph.triples((entity_uri, rdflib.URIRef('http://purl.org/dc/elements/1.1/source'), None))]
        entity_dict['reference'] = {'label':elements['reference'][current_language], 'data': reference}



        entity_dict['description'] = {'label':elements['description'][current_language], 'data': ''}


        entity_dict['none'] = {'label':elements['none'][current_language]}


        return render_template('property_template.html', data=entity_dict, lang=current_language)

    else:
        
        return render_template('404.html') 
        
if __name__ == "__main__":
    app.run(debug=True, port=5000)
