from flask import Flask, render_template, request
import json
import pandas
import pathlib
import pydash
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

def extract_values(key, entity, predicate, direction, lang):

    none_dict = {'en':'None', 'es':'Ninguno', 'fr':'Aucun'}

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
            if x.language == lang:
                recollect.append({'key':key, 'value':str(x), 'link':''})
        elif type(x) == type(rdflib.URIRef('')):
            labels = [c for a,b,c in graph.triples((x, rdflib.RDFS.label, None)) if c.language == lang]
            if not len(labels):
                lab = 'No label available.'
            else:
                lab = str(labels[0])

            recollect.append({'key':key, 'value':lab, 'link':str(x)})

        else:
            pass # blank nodes seem to still be here??? why

    if not len(recollect):
        recollect.append({'key': key, 'value':none_dict[lang], 'link':''})

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

graph = rdflib.Graph().parse('https://raw.githubusercontent.com/FIAF/FIAFcore/main/FIAFcore.ttl', format='ttl')

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


        lang = language()
        
        type_dict = {'en':'type', 'es':'tipo', 'fr':'type'}
        domain_dict = {'en':'domain', 'es':'dominio', 'fr':'domaine'}
        range_dict = {'en':'range', 'es':'rango', 'fr':'étendue'}
        descript_dict = {'en':'description', 'es':'descripción', 'fr':'description'}
        prop_dict = {'en':'properties', 'es':'propiedades', 'fr':'propriétés'}
        ref_dict = {'en':'reference', 'es':'referencia', 'fr':'référence'}
        parent_dict = {'en':'parent classes', 'es':'clases parentales', 'fr':'classes parentes'}
        child_dict = {'en':'child classes', 'es':'clases infantiles', 'fr':"classes d'enfants"}

        type_state = extract_values(type_dict[lang], entity, rdflib.RDF.type, 'right', lang).iloc[0]['value']

        attributes = pandas.concat([
            extract_values(type_dict[lang], entity, rdflib.RDF.type, 'right', lang),
        ])
        
        if type_state != 'Class':

            attributes = pandas.concat([
                attributes,
                extract_values(domain_dict[lang], entity, rdflib.RDFS.domain, 'right', lang),
                extract_values(range_dict[lang], entity, rdflib.RDFS.range, 'right', lang)
            ])

        attributes = pandas.concat([
                attributes,
                extract_values(ref_dict[lang], entity, rdflib.URIRef('http://purl.org/dc/elements/1.1/source'), 'right', lang),  
                extract_values(descript_dict[lang], entity, rdflib.URIRef('http://purl.org/dc/elements/1.1/description'), 'right', lang)
            ])
        
        if type_state == 'Class':

            attributes = pandas.concat([
                attributes,
                extract_values(parent_dict[lang], entity, rdflib.RDFS.subClassOf, 'right', lang),
                extract_values(child_dict[lang], entity, rdflib.RDFS.subClassOf, 'left', lang),
                extract_values(prop_dict[lang], entity, rdflib.RDFS.domain, 'left', lang)
            ])

        label = extract_values('label', entity, rdflib.RDFS.label, 'right', lang).iloc[0]['value']

        # if your entity is one of the primaries, then pull an example.
        # Event should be in there, but there are currently none in the triplestore.

        if entity in ['WorkVariant', 'Manifestation', 'Item', 'Carrier', 'Activity', 'Agent']:

            select_query = '''
                prefix fiaf: <https://ontology.fiafcore.org/>
                select distinct ?element where {
                    ?element rdf:type fiaf:'''+entity+'''
                }
            '''

            endpoint = 'https://query.fiafcore.org/repositories/fiaf-kg'
            graphdb = sparql_query(select_query, endpoint).drop_duplicates()

            # in the future your uuids should be hardcoded for each example.

            example = [x['element'] for x in graphdb.to_dict('records')][0]
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
            for index, row in graphdb.iterrows():
                if 'genid' in row['c']:
                    rebuilt.add((rdflib.URIRef(row['a']), rdflib.URIRef(row['b']), rdflib.BNode()))
                # elif 'genid' in row['a']:
                #     rebuilt.add((rdflib.BNode(), rdflib.URIRef(row['b']), rdflib.URIRef(row['c'])))                    
                elif 'http' in row['c']:
                    rebuilt.add((rdflib.URIRef(row['a']), rdflib.URIRef(row['b']), rdflib.URIRef(row['c'])))
                else:
                    rebuilt.add((rdflib.URIRef(row['a']), rdflib.URIRef(row['b']), rdflib.Literal(row['c'])))

            turtle = rebuilt.serialize(format='ttl')[:-2]

            data = {'label': label, 'attributes': attributes.to_dict('records'), 'turtle':turtle, 'mode':'example'}
        else:
            data = {'label': label, 'attributes': attributes.to_dict('records'), 'mode':'secondary'}

        return render_template('page.html', data=data, colour='mediumaquamarine')

    else:
        return render_template('404.html', colour='mediumaquamarine')

if __name__ == "__main__":
    app.run(debug=True, port=5028)