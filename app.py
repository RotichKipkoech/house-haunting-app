import os
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure the database and image upload folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///houses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# House model
class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    available = db.Column(db.Boolean, default=True)

# Helper function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home route
@app.route('/')
def index():
    houses = House.query.all()
    return render_template('index.html', houses=houses)

# Route to add a new house
@app.route('/add', methods=['GET', 'POST'])
def add_house():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        location = request.form['location']
        
        image_file = request.files['image_file']
        image_filename = None
        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        new_house = House(title=title, description=description, price=price, location=location, image_file=image_filename)
        db.session.add(new_house)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_house.html')

# Route to edit an existing house
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_house(id):
    house = House.query.get_or_404(id)
    if request.method == 'POST':
        house.title = request.form['title']
        house.description = request.form['description']
        house.price = request.form['price']
        house.location = request.form['location']
        house.available = True if 'available' in request.form else False

        image_file = request.files['image_file']
        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            house.image_file = image_filename

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_house.html', house=house)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
