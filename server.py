from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from werkzeug.utils import secure_filename
import os


app = Flask('__name__')
app.config['SECRET_KEY'] = 'newapp'
app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///joylistic.db" 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'C://Users//hp//Documents//Files//Python//Pro Projects//Restaurant site//static//food_images'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app=app)


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(30), nullable=False, unique=False)
    lname = db.Column(db.String(30), nullable=False, unique=False)
    phone_number = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(1000), nullable=False, unique=False)


class Food(db.Model):
    __tablename__ = 'food'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), nullable=False, unique=False)
    food_name = db.Column(db.String(30), nullable=False, unique=False)
    price = db.Column(db.Integer, nullable=False, unique=False)
    in_stock = db.Column(db.Boolean, default=True, nullable=False)
    times_ordered = db.Column(db.Integer, nullable=True, unique=False)
    image = db.Column(db.String(1000), nullable=False)



with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def home():
    meal_1 = Food.query.filter_by(in_stock=True).limit(limit=2)
    
    return render_template('index.html', meals=meal_1)

@app.route('/menu')
def menu():
    
    return render_template('menu.html')

@app.route('/product')
def product():
    meal_id = request.args.get('ll')
    meal = Food.query.filter_by(id=meal_id).first()
    extras = Food.query.filter_by(category='Extras', in_stock=True).all()
    drinks = Food.query.filter_by(category='Drinks', in_stock=True).all()
    proteins = Food.query.filter_by(category='Proteins', in_stock=True).all()
    drinks_len = len(drinks)
    extras_len = len(extras)
    proteins_len = len(proteins)

    return render_template('product.html', meal=meal, extras=extras, drinks=drinks,
                            proteins=proteins, drinks_len=drinks_len,
                            extras_len=extras_len, proteins_len=proteins_len)

@app.route('/search')
def search():
    pass

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/meals')
def meals():
    cat = request.args.get('cat')
    item = Food.query.filter_by(category=cat).all()
    return render_template('meal.html', items=item, cat=cat)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/add', methods=['POST', 'GET'])
def add_meal():
    if request.method == 'POST':
        food_name = request.form.get('food-name')
        category = request.form.get('category')
        price = request.form.get('price')
        uploaded_file = request.files['image']

        if uploaded_file.filename != '':
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            new_food = Food(
                category=category,
                food_name=food_name.title(),
                price=price,
                image=filename

            )

            db.session.add(new_food)
            db.session.flush()
            db.session.commit()
            flash('Form submitted successfully!', 'success')
            return redirect(url_for('add_meal'))
        else:
            return 'No file selected!'
        
    return render_template('add_food.html')

@app.route('/view')
def view_meals():
    meals = Food.query.all()
    return render_template('view_foods.html', meals=meals)

@app.route('/del')
def delete_meal():
    meal_id = request.args.get('ll')
    meal = Food.query.filter_by(id=meal_id).first()
    db.session.delete(meal)
    db.session.commit()
    return redirect(url_for('view_meals'))


@app.route('/edit', methods=['POST', 'GET'])
def edit_meal():
    meal_id = request.args.get('ll')
    meal = Food.query.filter_by(id=meal_id).first()
    if request.method == 'POST':
        food_name = request.form.get('food-name')
        category = request.form.get('category')
        price = request.form.get('price')
        uploaded_file = request.files['image']
        in_stock = request.form.get('availability')

        avail = None
        if in_stock == 'available':
            avail = True
            meal.in_stock = avail
        else:
            avail = False
            meal.in_stock = avail
        
        meal.food_name = food_name.title()
        meal.category = category.title()
        meal.price = price
        

        if uploaded_file.filename != '':
            file = secure_filename(uploaded_file.filename)
            fz = os.path.join(app.config['UPLOAD_FOLDER'], file)
            uploaded_file.save(fz)

            meal.image = file
        else:
            meal.image = meal.image
        
        db.session.commit()

        return redirect(url_for('view_meals'))

    return render_template('edit_food.html', meal=meal)

if __name__ == '__main__':
    app.run(debug=True)