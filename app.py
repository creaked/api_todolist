import os

from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import expression

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# Todo Class/Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False)
    completed = db.Column(
        db.Boolean, server_default=expression.false(), nullable=False)

    def __init__(self, title, completed):
        self.title = title
        self.completed = completed

# Todo Schema
class TodoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'completed')

# Init Schema
todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)

# Create Todo
@app.route('/todo', methods=['POST'])
def add_todo():
    title = request.json['title']
    completed = request.json['completed']

    new_todo = Todo(title, completed)
    db.session.add(new_todo)
    db.session.commit()

    return todo_schema.jsonify(new_todo)

# Get All Todos
@app.route('/todo', methods=['GET'])
def get_todos():
    all_todos = Todo.query.all()
    result = todos_schema.dump(all_todos)
    return jsonify(result)

# Get Todo
@app.route('/todo/<id>', methods=['GET'])
def get_todo(id):
    todo = Todo.query.get(id)
    return todo_schema.jsonify(todo)

# Update Todo
@app.route('/todo/<id>', methods=['PUT'])
def update_todo(id):
    todo = Todo.query.get(id)
    title = request.json['title']
    completed = request.json['completed']

    todo.title = title
    todo.completed = completed

    db.session.commit()

    return todo_schema.jsonify(todo)


# Delete Todo
@app.route('/todo/<id>', methods=['DELETE'])
def delete_todo(id):
    todo = Todo.query.get(id)
    db.session.delete(todo)
    db.session.commit()
    return todo_schema.jsonify(todo)


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
    return response


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
