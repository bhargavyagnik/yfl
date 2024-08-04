from flask import Flask, request, jsonify
import pandas as pd
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch(hosts=[{'host': 'elasticsearch', 'port': 9200}])
#ToDo : Elasticsearch docker container should be running before running this script
# Load CSV data into Elasticsearch
df = pd.read_csv('data/recipes.csv')
for index, row in df.iterrows():
    doc = {
        'recipe_name': row['recipe_name'],
        'ingredients': row['ingredients'],
        'preparation_time': row['preparation_time'],
        'cooking_time': row['cooking_time']
    }
    es.index(index='recipes', body=doc)

# Search by name
@app.route('/search/name', methods=['GET'])
def search_by_name():
    query = request.args.get('q')
    response = es.search(index='recipes', body={
        'query': {
            'match': {
                'recipe_name': query
            }
        }
    })
    return jsonify(response['hits']['hits'])

# Search by ingredients
@app.route('/search/ingredients', methods=['GET'])
def search_by_ingredients():
    query = request.args.get('q')
    response = es.search(index='recipes', body={
        'query': {
            'match': {
                'ingredients': query
            }
        }
    })
    return jsonify(response['hits']['hits'])

if __name__ == '__main__':
    app.run(debug=True)