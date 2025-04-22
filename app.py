from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging
from sqlalchemy.exc import OperationalError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Set database URI using absolute path for reliability
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get('DB_PATH', os.path.join(BASE_DIR, 'farmers_market.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    products = db.relationship('Product', backref='farmer', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_name = db.Column(db.String(100), nullable=False)
    buyer_email = db.Column(db.String(120), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='orders')

# Create database tables if they don't exist
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
        products = Product.query.all()
        logger.info(f"Retrieved {len(products)} products from database")
        return render_template('index.html', products=products)
    except OperationalError as e:
        logger.error(f"Error querying products: {e}")
        return jsonify({'error': 'Database error, please try again later'}), 500

@app.route('/profile/<int:farmer_id>')
def profile(farmer_id):
    try:
        farmer = Farmer.query.get_or_404(farmer_id)
        products = Product.query.filter_by(farmer_id=farmer_id).all()
        orders = Order.query.join(Product).filter(Product.farmer_id == farmer_id).all()
        logger.info(f"Retrieved profile for farmer ID: {farmer_id}")
        return render_template('profile.html', farmer=farmer, products=products, orders=orders)
    except OperationalError as e:
        logger.error(f"Error retrieving profile for farmer {farmer_id}: {e}")
        return jsonify({'error': 'Database error, please try again later'}), 500

@app.route('/api/farmers/register', methods=['POST'])
def register_farmer():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'name' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if Farmer.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        farmer = Farmer(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address')
        )
        db.session.add(farmer)
        db.session.commit()
        logger.info(f"Registered farmer: {data['email']}")
        return jsonify({'message': 'Farmer registered successfully', 'id': farmer.id}), 201
    except Exception as e:
        logger.error(f"Error registering farmer: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to register farmer'}), 500

@app.route('/api/farmers/<int:farmer_id>', methods=['PUT'])
def update_farmer(farmer_id):
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
def add_product():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['name', 'price', 'quantity', 'farmer_id']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            quantity=data['quantity'],
            farmer_id=data['farmer_id']
        )
        db.session.add(product)
        db.session.commit()
        logger.info(f"Added product: {data['name']}")
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
            'farmer': p.farmer.name if p.farmer else 'Unknown'
        } for p in products])
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        return jsonify({'error': 'Failed to retrieve products'}), 500

@app.route('/api/orders', methods=['POST'])
def place_order():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['buyer_name', 'buyer_email', 'product_id', 'quantity']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        product = Product.query.get_or_404(data['product_id'])
        
        if product.quantity < data['quantity']:
            return jsonify({'error': 'Insufficient quantity'}), 400
        
        order = Order(
            buyer_name=data['buyer_name'],
            buyer_email=data['buyer_email'],
            product_id=data['product_id'],
            quantity=data['quantity']
        )
        product.quantity -= data['quantity']
        db.session.add(order)
        db.session.commit()
        logger.info(f"Placed order for product ID: {data['product_id']}")
        return jsonify({'message': 'Order placed successfully', 'id': order.id}), 201
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to place order'}), 500

@app.route('/api/farmers/<int:farmer_id>/orders', methods=['GET'])
def get_farmer_orders(farmer_id):
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

if __name__ == '__main__':
    logger.info(f"Starting Flask app with database: {DB_PATH}")
    app.run(debug=True)