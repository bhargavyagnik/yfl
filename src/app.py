from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
db = SQLAlchemy(app)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    youtube_link = db.Column(db.String(200))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_recipes', methods=['POST'])
def find_recipes():
    ingredients = request.json['ingredients']
    matching_recipes = []

    for ingredient in ingredients:
        recipes = Recipe.query.filter(Recipe.ingredients.like(f'%{ingredient}%')).all()
        for recipe in recipes:
            if recipe not in matching_recipes:
                matching_recipes.append(recipe)

    results = [
        {
            'name': recipe.name,
            'ingredients': recipe.ingredients,
            'youtube_link': recipe.youtube_link
        }
        for recipe in matching_recipes
    ]

    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)