

from flask import Flask, render_template
import pandas
import pathlib
import rdflib

# load resource parquet files

df = pandas.read_parquet(pathlib.Path.cwd() / 'static' / 'bundesarchiv_resources.parquet')
df['resource_id'] = df['entity'].str.split('/').str[-1]

app = Flask(__name__)

@app.route('/<resource>', methods=['GET', 'POST'])
def home_page(resource):

    if resource in list(df.resource_id.unique()):

        entity_data = df.loc[df.resource_id.isin([resource])]
        data = {
            'resource_label': entity_data.iloc[0]['entityLabel'],
            'resource_type': entity_data.iloc[0]['type_label'],
            'identifiers': [{'id':f"{x['id_value']} ({x['auth_label']})", 'pos':n} for n,x in enumerate(entity_data.to_dict('records'))]
            }

        return render_template('resource.html', data=data)

    else:
        return render_template('404.html')

if __name__ == "__main__":
    app.run(debug=True, port=5001)