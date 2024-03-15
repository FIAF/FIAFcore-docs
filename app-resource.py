

from flask import Flask, render_template
import pandas
import pathlib
import rdflib

# load resource parquet files

df = pandas.read_csv(pathlib.Path.cwd() / 'static' / 'bundesarchiv_resources.csv')
df['resource_id'] = df['entity'].str.split('/').str[-1]

app = Flask(__name__)

@app.route('/<resource>', methods=['GET', 'POST'])
def home_page(resource):

    if resource in list(df.resource_id.unique()):

        entity_data = df.loc[df.resource_id.isin([resource])].copy()
        entity_data['id_concat'] = entity_data['id_value']+' ('+entity_data['auth_label']+')'

        ident = entity_data[['id_concat']].rename(columns={'id_concat':'value'})
        ident['key'] = 'identifiers'
        ident['link'] = ''
        ident['pos'] = [x for x in range(len(ident))]

        attributes = pandas.concat([
            pandas.DataFrame([{
                'key':'type', 
                'value':entity_data.iloc[0]['type_label'],
                'link':entity_data.iloc[0]['type'],
                'pos':0
                }]),
            ident 
            ])

        data = {'label': entity_data.iloc[0]['entityLabel'], 
            'attributes': attributes.to_dict('records')}

        return render_template('resource.html', data=data)

    else:
        return render_template('404.html', colour='tomato')

if __name__ == "__main__":
    app.run(debug=True, port=5029)