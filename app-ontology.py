from flask import Flask, render_template
import json
import pandas
import pathlib
import pydash
import rdflib

def extract_values(key, entity, predicate, direction):

    current_language = 'en'
    entity_id = rdflib.URIRef(f'https://ontology.fiafcore.org/{entity}')

    if direction == 'right':
        property_matches = [o for s,p,o in graph.triples((entity_id, predicate, None))]
    elif direction == 'left':
        property_matches = [s for s,p,o in graph.triples((None, predicate, entity_id))]
    else:
        raise Exception('this shouldnt happen.')

    recollect = list()

    for x in property_matches:
        if type(x) == type(rdflib.Literal('')):
            if x.language == current_language:
                recollect.append({'key':key, 'value':str(x), 'link':''})
        elif type(x) == type(rdflib.URIRef('')):
            labels = [c for a,b,c in graph.triples((x, rdflib.RDFS.label, None)) if c.language == current_language]
            if not len(labels):
                lab = 'No label available.'
            else:
                lab = str(labels[0])

            recollect.append({'key':key, 'value':lab, 'link':str(x)})

        else:
            pass # blank nodes seem to still be here??? why

    if not len(recollect):
        recollect.append({'key': key, 'value':'None', 'link':''})

    recollect = sorted(recollect, key=lambda x: x['value'])
    recollect = pandas.DataFrame(recollect)
    recollect['pos'] = [x for x in range(len(recollect))]

    return recollect

def pull_label(entity, language):

    ''' Pull first available label for entity. '''

    label = [o for s,p,o in graph.triples((entity, rdflib.RDFS.label, None)) if o.language == language]
    if not len(label):
        return "Label required."
    else:
        return str(label[0])

graph = rdflib.Graph()
graph.parse(pathlib.Path.cwd() / 'static' / 'ontology.ttl', format='ttl')

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
        
for l in ['en', 'es', 'fr']:
    graph.add((rdflib.URIRef('http://www.w3.org/2002/07/owl#Class'), rdflib.RDFS.label, rdflib.Literal('Class', lang=l)))
    graph.add((rdflib.URIRef('http://www.w3.org/2002/07/owl#ObjectProperty'), rdflib.RDFS.label, rdflib.Literal('Object Property', lang=l)))
    graph.add((rdflib.URIRef('http://www.w3.org/2002/07/owl#DatatypeProperty'), rdflib.RDFS.label, rdflib.Literal('Datatype Property', lang=l)))

app = Flask(__name__)

@app.route('/<entity>', methods=['GET', 'POST'])
def home_page(entity):

    if entity in entities:

        current_language = 'en'
        type_state = extract_values('type', entity, rdflib.RDF.type, 'right').iloc[0]['value']

        attributes = pandas.concat([
            extract_values('type', entity, rdflib.RDF.type, 'right'),
            extract_values('reference', entity, rdflib.URIRef('http://purl.org/dc/elements/1.1/source'), 'right')  
        ])
        
        if type_state == 'Class':

            attributes = pandas.concat([
                attributes,
                extract_values('parent classes', entity, rdflib.RDFS.subClassOf, 'right'),
                extract_values('child classes', entity, rdflib.RDFS.subClassOf, 'left'),
                extract_values('properties', entity, rdflib.RDFS.domain, 'left')
            ])

        if type_state != 'Class':

            attributes = pandas.concat([
                attributes,
                extract_values('domain', entity, rdflib.RDFS.domain, 'right'),
                extract_values('range', entity, rdflib.RDFS.range, 'right')
            ])

        attributes = pandas.concat([
                attributes,
                extract_values('description', entity, rdflib.URIRef('http://purl.org/dc/elements/1.1/description'), 'right')
            ])

        label = extract_values('label', entity, rdflib.RDFS.label, 'right').iloc[0]['value']
        data = {'label': label, 'attributes': attributes.to_dict('records')}

        return render_template('page.html', data=data, colour='mediumaquamarine')

    else:
        return render_template('404.html', colour='mediumaquamarine')

if __name__ == "__main__":
    app.run(debug=True, port=5028)