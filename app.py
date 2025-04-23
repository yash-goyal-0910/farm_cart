from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import logging
from sqlalchemy.exc import OperationalError
from sqlalchemy import or_

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Set database URI and secret key
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get('DB_PATH', os.path.join(BASE_DIR, 'farmers_market.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')  # Change in production
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class Farmer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    products = db.relationship('Product', backref='farmer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    shipping_option = db.Column(db.String(50), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_name = db.Column(db.String(100), nullable=False)
    buyer_email = db.Column(db.String(120), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='orders')

@login_manager.user_loader
def load_user(user_id):
    return Farmer.query.get(int(user_id))

# Create database tables
try:
    with app.app_context():
        db.create_all()
        logger.info("Database tables verified/created successfully")
except OperationalError as e:
    logger.error(f"Database error: {e}")
    raise

# Routes
@app.route('/')
def index():
    try:
        search_query = request.args.get('search', '').strip()
        farmer_filter = request.args.get('farmer', '').strip()
        query = Product.query
        if search_query:
            search_term = f'%{search_query}%'
            query = query.filter(or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            ))
        if farmer_filter:
            query = query.join(Farmer).filter(Farmer.name.ilike(f'%{farmer_filter}%'))
        products = query.all()
        farmers = Farmer.query.all()
        logger.info(f"Retrieved {len(products)} products with search: '{search_query}', farmer: '{farmer_filter}'")
        return render_template('index.html', products=products, farmers=farmers, search_query=search_query, farmer_filter=farmer_filter)
    except OperationalError as e:
        logger.error(f"Error querying products: {e}")
        return jsonify({'error': 'Database error, please try again later'}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        logger.info(f"Retrieved dashboard for farmer ID: {current_user.id}")
        return render_template('dashboard.html')
    except OperationalError as e:
        logger.error(f"Error retrieving dashboard: {e}")
        return jsonify({'error': 'Database error, please try again later'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            data = request.form
            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                flash('Email and password are required', 'error')
                return render_template('login.html')
            farmer = Farmer.query.filter_by(email=email).first()
            if farmer and farmer.check_password(password):
                login_user(farmer)
                logger.info(f"Farmer logged in: {email}")
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'error')
                return render_template('login.html')
        except Exception as e:
            logger.error(f"Error during login: {e}")
            flash('An error occurred, please try again', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            data = request.form
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            phone = data.get('phone')
            address = data.get('address')
            if not all([name, email, password]):
                flash('Name, email, and password are required', 'error')
                return render_template('signup.html')
            if Farmer.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('signup.html')
            farmer = Farmer(name=name, email=email, phone=phone, address=address)
            farmer.set_password(password)
            db.session.add(farmer)
            db.session.commit()
            logger.info(f"Registered farmer via signup: {email}")
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Error during signup: {e}")
            db.session.rollback()
            flash('An error occurred, please try again', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/order/<int:product_id>', methods=['GET', 'POST'])
@login_required
def order(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        if request.method == 'POST':
            data = request.form
            quantity = data.get('quantity')
            if not quantity:
                flash('Quantity is required', 'error')
                return render_template('order.html', product=product)
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    flash('Quantity must be greater than zero', 'error')
                    return render_template('order.html', product=product)
            except ValueError:
                flash('Quantity must be a valid number', 'error')
                return render_template('order.html', product=product)
            if product.quantity < quantity:
                flash('Insufficient quantity available', 'error')
                return render_template('order.html', product=product)
            order = Order(
                buyer_name=current_user.name,
                buyer_email=current_user.email,
                product_id=product_id,
                quantity=quantity
            )
            product.quantity -= quantity
            db.session.add(order)
            db.session.commit()
            logger.info(f"Order placed for product ID: {product_id} by {current_user.email}")
            flash('Order placed successfully!', 'success')
            return redirect(url_for('profile', farmer_id=current_user.id))
        return render_template('order.html', product=product)
    except Exception as e:
        logger.error(f"Error processing order for product {product_id}: {e}")
        flash('An error occurred, please try again', 'error')
        return render_template('order.html', product=product)

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        if product.farmer_id != current_user.id:
            flash('You can only edit your own products', 'error')
            return redirect(url_for('profile', farmer_id=current_user.id))
        if request.method == 'POST':
            data = request.form
            name = data.get('name')
            description = data.get('description')
            price = data.get('price')
            quantity = data.get('quantity')
            shipping_option = data.get('shipping_option')
            if not all([name, price, quantity, shipping_option]):
                flash('Name, price, quantity, and shipping option are required', 'error')
                return render_template('product.html', product=product)
            if shipping_option not in ['Self Ship', 'Shiprocket']:
                flash('Invalid shipping option', 'error')
                return render_template('product.html', product=product)
            try:
                price = float(price)
                quantity = int(quantity)
                if price <= 0 or quantity < 0:
                    flash('Price must be greater than zero and quantity cannot be negative', 'error')
                    return render_template('product.html', product=product)
            except ValueError:
                flash('Price and quantity must be valid numbers', 'error')
                return render_template('product.html', product=product)
            product.name = name
            product.description = description
            product.price = price
            product.quantity = quantity
            product.shipping_option = shipping_option
            db.session.commit()
            logger.info(f"Updated product ID: {product_id} by farmer ID: {current_user.id}")
            flash('Product updated successfully!', 'success')
            return redirect(url_for('profile', farmer_id=current_user.id))
        return render_template('product.html', product=product)
    except Exception as e:
        logger.error(f"Error processing product {product_id}: {e}")
        db.session.rollback()
        flash('An error occurred, please try again', 'error')
        return render_template('product.html', product=product)

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    try:
        data = request.form
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        quantity = data.get('quantity')
        shipping_option = data.get('shipping_option')
        if not all([name, price, quantity, shipping_option]):
            flash('Name, price, quantity, and shipping option are required', 'error')
            return redirect(url_for('profile', farmer_id=current_user.id))
        if shipping_option not in ['Self Ship', 'Shiprocket']:
            flash('Invalid shipping option', 'error')
            return redirect(url_for('profile', farmer_id=current_user.id))
        try:
            price = float(price)
            quantity = int(quantity)
            if price <= 0 or quantity <= 0:
                flash('Price and quantity must be greater than zero', 'error')
                return redirect(url_for('profile', farmer_id=current_user.id))
        except ValueError:
            flash('Price and quantity must be valid numbers', 'error')
            return redirect(url_for('profile', farmer_id=current_user.id))
        product = Product(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            farmer_id=current_user.id,
            shipping_option=shipping_option
        )
        db.session.add(product)
        db.session.commit()
        logger.info(f"Added product: {name} by farmer ID: {current_user.id} with shipping: {shipping_option}")
        flash('Product added successfully!', 'success')
        return redirect(url_for('profile', farmer_id=current_user.id))
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        db.session.rollback()
        flash('An error occurred, please try again', 'error')
        return redirect(url_for('profile', farmer_id=current_user.id))

@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        product = Product.query.get_or_404(order.product_id)
        if product.farmer_id != current_user.id:
            flash('Unauthorized to update this order', 'error')
            return redirect(url_for('profile', farmer_id=current_user.id))
        if order.status == 'Completed':
            flash('Cannot change status of a completed order', 'error')
            return redirect(url_for('profile', farmer_id=current_user.id))
        data = request.form
        new_status = data.get('status')
        if not new_status:
            flash('Status is required', 'error')
            return redirect(url_for('profile', farmer_id=current_user.id))
        if new_status not in ['Pending', 'Completed', 'Cancelled']:
            flash('Invalid status', 'error')
            return redirect(url_for('profile', farmer_id=current_user.id))
        order.status = new_status
        db.session.commit()
        logger.info(f"Updated order ID: {order_id} to status: {new_status} by farmer ID: {current_user.id}")
        flash('Order status updated successfully!', 'success')
        return redirect(url_for('profile', farmer_id=current_user.id))
    except Exception as e:
        logger.error(f"Error updating order status for order {order_id}: {e}")
        db.session.rollback()
        flash('An error occurred, please try again', 'error')
        return redirect(url_for('profile', farmer_id=current_user.id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    logger.info("Farmer logged out")
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/profile/<int:farmer_id>')
@login_required
def profile(farmer_id):
    if current_user.id != farmer_id:
        flash('You can only access your own profile', 'error')
        return redirect(url_for('profile', farmer_id=current_user.id))
    
    try:
        farmer = Farmer.query.get_or_404(farmer_id)
        products = Product.query.filter_by(farmer_id=farmer_id).all()
        # Orders where farmer is the seller (products they own)
        seller_orders = Order.query.join(Product).filter(Product.farmer_id == farmer_id).all()
        # Orders where farmer is the buyer
        buyer_orders = Order.query.filter_by(buyer_email=farmer.email).all()
        logger.info(f"Retrieved profile for farmer ID: {farmer_id}")
        return render_template('profile.html', farmer=farmer, products=products, seller_orders=seller_orders, buyer_orders=buyer_orders)
    except OperationalError as e:
        logger.error(f"Error retrieving profile for farmer {farmer_id}: {e}")
        return jsonify({'error': 'Database error, please try again later'}), 500

@app.route('/api/farmers/register', methods=['POST'])
def register_farmer():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['email', 'name', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        if Farmer.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        farmer = Farmer(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address')
        )
        farmer.set_password(data['password'])
        db.session.add(farmer)
        db.session.commit()
        logger.info(f"Registered farmer via API: {data['email']}")
        return jsonify({'message': 'Farmer registered successfully', 'id': farmer.id}), 201
    except Exception as e:
        logger.error(f"Error registering farmer: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to register farmer'}), 500

@app.route('/api/farmers/<int:farmer_id>', methods=['PUT'])
@login_required
def update_farmer(farmer_id):
    if current_user.id != farmer_id:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        data = request.get_json()
        farmer = Farmer.query.get_or_404(farmer_id)
        if 'phone' in data:
            farmer.phone = data['phone']
        if 'address' in data:
            farmer.address = data['address']
        db.session.commit()
        logger.info(f"Updated profile for farmer ID: {farmer_id}")
        return jsonify({'message': 'Farmer profile updated successfully'}), 200
    except Exception as e:
        logger.error(f"Error updating farmer {farmer_id}: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

@app.route('/api/products', methods=['POST'])
@login_required
def api_add_product():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['name', 'price', 'quantity', 'shipping_option']):
            return jsonify({'error': 'Missing required fields'}), 400
        if data['shipping_option'] not in ['Self Ship', 'Shiprocket']:
            return jsonify({'error': 'Invalid shipping option'}), 400
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            quantity=data['quantity'],
            farmer_id=current_user.id,
            shipping_option=data['shipping_option']
        )
        db.session.add(product)
        db.session.commit()
        logger.info(f"Added product via API: {data['name']} with shipping: {data['shipping_option']}")
        return jsonify({'message': 'Product added successfully', 'id': product.id}), 201
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to add product'}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        logger.info(f"Retrieved {len(products)} products for API")
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'quantity': p.quantity,
            'farmer': p.farmer.name if p.farmer else 'Unknown',
            'shipping_option': p.shipping_option
        } for p in products])
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        return jsonify({'error': 'Failed to retrieve products'}), 500

@app.route('/api/orders', methods=['POST'])
@login_required
def place_order():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['product_id', 'quantity']):
            return jsonify({'error': 'Missing required fields'}), 400
        product = Product.query.get_or_404(data['product_id'])
        if product.quantity < data['quantity']:
            return jsonify({'error': 'Insufficient quantity'}), 400
        order = Order(
            buyer_name=current_user.name,
            buyer_email=current_user.email,
            product_id=data['product_id'],
            quantity=data['quantity']
        )
        product.quantity -= data['quantity']
        db.session.add(order)
        db.session.commit()
        logger.info(f"Placed order for product ID: {data['product_id']} by {current_user.email}")
        return jsonify({'message': 'Order placed successfully', 'id': order.id}), 201
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to place order'}), 500

@app.route('/api/farmers/<int:farmer_id>/orders', methods=['GET'])
@login_required
def get_farmer_orders(farmer_id):
    if current_user.id != farmer_id:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        orders = Order.query.join(Product).filter(Product.farmer_id == farmer_id).all()
        logger.info(f"Retrieved {len(orders)} orders for farmer ID: {farmer_id}")
        return jsonify([{
            'id': o.id,
            'buyer_name': o.buyer_name,
            'product_name': o.product.name,
            'quantity': o.quantity,
            'status': o.status,
            'order_date': o.order_date.isoformat()
        } for o in orders])
    except Exception as e:
        logger.error(f"Error retrieving orders for farmer {farmer_id}: {e}")
        return jsonify({'error': 'Failed to retrieve orders'}), 500

@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def api_update_order_status(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        product = Product.query.get_or_404(order.product_id)
        if product.farmer_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        if order.status == 'Completed':
            return jsonify({'error': 'Cannot change status of a completed order'}), 400
        data = request.get_json()
        new_status = data.get('status')
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        if new_status not in ['Pending', 'Completed', 'Cancelled']:
            return jsonify({'error': 'Invalid status'}), 400
        order.status = new_status
        db.session.commit()
        logger.info(f"Updated order ID: {order_id} to status: {new_status} via API")
        return jsonify({'message': 'Order status updated successfully'}), 200
    except Exception as e:
        logger.error(f"Error updating order status via API for order {order_id}: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update order status'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Flask app with database: {DB_PATH}")
    app.run(debug=True)