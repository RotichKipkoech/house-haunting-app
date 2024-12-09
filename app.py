import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///houses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key' 
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

# Model for users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Model for houses
class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(15), nullable=False)
    additional_images = db.Column(db.Text, nullable=True)

    def get_additional_images(self):
        if self.additional_images:
            return self.additional_images.split(',')
        return []

# Check allowed image extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def index():
    houses = House.query.all()
    return render_template('index.html', houses=houses)

# Route to add a new house (Admin only)
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_house():
    if not current_user.is_admin:
        return "Access Denied", 403

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        location = request.form['location']
        contact_name = request.form['contact_name']
        contact_phone = request.form['contact_phone']

        image_file = request.files['image_file']
        additional_images = request.files.getlist('additional_images')
        image_filename = None
        additional_image_filenames = []

        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        for img in additional_images:
            if img and allowed_file(img.filename):
                img_filename = secure_filename(img.filename)
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
                additional_image_filenames.append(img_filename)

        additional_images_str = ','.join(additional_image_filenames)

        new_house = House(
            title=title,
            description=description,
            price=price,
            location=location,
            image_file=image_filename,
            contact_name=contact_name,
            contact_phone=contact_phone,
            additional_images=additional_images_str
        )
        db.session.add(new_house)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_house.html')

# Route to edit an existing house (Admin only)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_house(id):
    if not current_user.is_admin:
        return "Access Denied", 403

    house = House.query.get_or_404(id)
    if request.method == 'POST':
        house.title = request.form['title']
        house.description = request.form['description']
        house.price = request.form['price']
        house.location = request.form['location']
        house.contact_name = request.form['contact_name']
        house.contact_phone = request.form['contact_phone']

        image_file = request.files['image_file']
        additional_images = request.files.getlist('additional_images')

        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            house.image_file = image_filename

        additional_image_filenames = house.get_additional_images()
        for img in additional_images:
            if img and allowed_file(img.filename):
                img_filename = secure_filename(img.filename)
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
                additional_image_filenames.append(img_filename)

        house.additional_images = ','.join(additional_image_filenames)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_house.html', house=house)

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        is_admin = 'is_admin' in request.form  # Checkbox for admin
        new_user = User(username=username, password=password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your credentials and try again.', 'danger')
    return render_template('login.html')

# User logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route to view house details
@app.route('/house/<int:house_id>')
def house_detail(house_id):
    house = House.query.get_or_404(house_id)
    return render_template('house_detail.html', house=house)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
