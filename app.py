import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zoo.db'
db = SQLAlchemy(app)

# Set the path for the upload folder to be 'media'
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'media')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    filename = db.Column(db.String(255), nullable=False)

@app.route('/upload', methods=['POST'])
def add_animal():
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({'error': 'No file or name part in the request'}), 400
    
    file = request.files['file']
    name = request.form['name']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    new_animal = Animal(name=name, filename=filename)
    db.session.add(new_animal)
    db.session.commit()

    return jsonify({'message': 'Animal added successfully', 'name': name, 'filename': filename}), 201

@app.route('/media/<filename>')
def media(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/getImages', methods=['GET'])
def get_images():
    animals = Animal.query.all()
    animal_list = [{'id': animal.id, 'name': animal.name, 'filename': animal.filename} for animal in animals]
    return jsonify(animal_list)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
