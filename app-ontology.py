from flask import Flask, render_template
import json
import pandas
import pathlib
import pydash
import rdflib
import requests

def value_extract(row, column):

    ''' Extract dictionary values. '''

    return pydash.get(row[column], 'value')

def sparql_query(query, service):

    ''' Send sparql request, and formulate results into a dataframe. '''

    headers = {
        'Content-Type': 'application/x-turtle',
        'Accept': 'application/json'
    }

    response = requests.get(service, params={'query': query}, timeout=120, headers=headers)

    results = pydash.get(response.json(), 'results.bindings')
    data_frame = pandas.DataFrame.from_dict(results)
    for column in data_frame.columns:
        data_frame[column] = data_frame.apply(value_extract, column=column, axis=1)

    return data_frame

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
                        extract_values('reference', entity, rdflib.URIRef('http://purl.org/dc/elements/1.1/source'), 'right'),  
                extract_values('description', entity, rdflib.URIRef('http://purl.org/dc/elements/1.1/description'), 'right'),
            extract_values('type', entity, rdflib.RDF.type, 'right'),
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

        # attributes = pandas.concat([
        #         attributes,
        #         extract_values('reference', entity, rdflib.URIRef('http://purl.org/dc/elements/1.1/source'), 'right'),  
        #         extract_values('description', entity, rdflib.URIRef('http://purl.org/dc/elements/1.1/description'), 'right')
        #     ])

        label = extract_values('label', entity, rdflib.RDFS.label, 'right').iloc[0]['value']

        # see if you can pull an instance of a work and all attached 

        select_query = '''
            prefix fiaf: <https://ontology.fiafcore.org/>
            select distinct ?workvariant where {
                ?workvariant rdf:type fiaf:WorkVariant
            }
        '''

        endpoint = 'https://query.fiafcore.org/repositories/fiaf-kg'
        graphdb = sparql_query(select_query, endpoint).drop_duplicates()

        # in the future your uuid should be hardcoded.

        example = [x['workvariant'] for x in graphdb.to_dict('records')][0]

        print(example)


        select_query = '''
            prefix fiaf: <https://ontology.fiafcore.org/>
            select distinct ?a ?b ?c where {
                values ?a {<'''+example+'''>}
                ?a ?b ?c
            }
        '''

        endpoint = 'https://query.fiafcore.org/repositories/fiaf-kg'
        graphdb = sparql_query(select_query, endpoint).drop_duplicates()
        rebuilt = rdflib.Graph()
        print(len(graphdb))
        print(type(graphdb))
        for index, row in graphdb.iterrows():
            print(row)
            print(len(row))
        # for x in graphdb:
        #     print(type(x), x)
            if 'genid' in row['c']:
                rebuilt.add((rdflib.URIRef(row['a']), rdflib.URIRef(row['b']), rdflib.BNode()))

            elif 'http' in row['c']:
                rebuilt.add((rdflib.URIRef(row['a']), rdflib.URIRef(row['b']), rdflib.URIRef(row['c'])))
            else:
                rebuilt.add((rdflib.URIRef(row['a']), rdflib.URIRef(row['b']), rdflib.Literal(row['c'])))

        turtle = rebuilt.serialize(format='ttl')[:-2]
        jsonld = rebuilt.serialize(format='json-ld')

        print(turtle)
        print(jsonld)


        print(list(turtle))

        # for x in graphdb.to_dict('records'):
        #     print(x)
            # print(f"{x['activity_label']} ({x['activity']}) // {x['agent_label']} ({x['agent']})")
            # print('\n')




        # example = 

        data = {'label': label, 'attributes': attributes.to_dict('records'), 'turtle':turtle, 'json':jsonld}




        return render_template('page.html', data=data, colour='mediumaquamarine')

    else:
        return render_template('404.html', colour='mediumaquamarine')

if __name__ == "__main__":
    app.run(debug=True, port=5028)