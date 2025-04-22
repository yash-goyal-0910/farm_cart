import sqlite3
from werkzeug.security import generate_password_hash
from random import choice, randint
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect('farmers_market.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS farmer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        phone TEXT,
        address TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        farmer_id INTEGER NOT NULL,
        shipping_option TEXT NOT NULL,
        FOREIGN KEY (farmer_id) REFERENCES farmer (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS "order" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_name TEXT NOT NULL,
        buyer_email TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT DEFAULT 'Pending',
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES product (id)
    )
''')

# Sample data lists for generating realistic entries
farmer_names = [
    'John Doe', 'Jane Smith', 'Michael Brown', 'Emily Davis', 'William Johnson',
    'Sarah Wilson', 'David Martinez', 'Laura Garcia', 'James Taylor', 'Anna Lee'
]
domains = ['example.com', 'mail.com', 'farmmail.com']
product_names = [
    'Organic Apples', 'Free-range Eggs', 'Tomatoes', 'Carrots', 'Potatoes',
    'Strawberries', 'Blueberries', 'Lettuce', 'Cucumbers', 'Bell Peppers',
    'Zucchini', 'Spinach', 'Kale', 'Broccoli', 'Cauliflower',
    'Honey', 'Maple Syrup', 'Fresh Milk', 'Artisanal Cheese', 'Beef Jerky'
]
descriptions = [
    'Freshly picked from our orchard', 'Organic and locally grown',
    'Juicy and ripe', 'Grown without pesticides', 'Perfect for cooking',
    'Sweet and delicious', 'Farm-fresh quality', 'Hand-harvested daily',
    'Rich in flavor', 'Sustainably produced'
]
shipping_options = ['Self Ship', 'Shiprocket']
statuses = ['Pending', 'Completed', 'Cancelled']

# Insert farmers
farmers = []
for i, name in enumerate(farmer_names, 1):
    email = f"{name.lower().replace(' ', '.')}@{choice(domains)}"
    phone = f"{randint(100, 999)}-{randint(100, 999)}-{randint(1000, 9999)}"
    address = f"{randint(100, 999)} {choice(['Farm', 'Orchard', 'Ranch'])} {choice(['Road', 'Lane', 'Way'])}"
    cursor.execute('''
        INSERT OR IGNORE INTO farmer (name, email, password_hash, phone, address)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        name,
        email,
        generate_password_hash('default123'),
        phone,
        address
    ))
    farmers.append((i, name, email))

# Commit farmers to get their IDs
conn.commit()

# Retrieve farmer IDs
farmer_ids = []
for _, name, email in farmers:
    cursor.execute('SELECT id FROM farmer WHERE email = ?', (email,))
    farmer_id = cursor.fetchone()
    if farmer_id:
        farmer_ids.append(farmer_id[0])

# Insert products
products = []
for i in range(50):
    farmer_id = choice(farmer_ids)
    name = choice(product_names)
    cursor.execute('''
        INSERT OR IGNORE INTO product (name, description, price, quantity, farmer_id, shipping_option)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        name,
        choice(descriptions),
        round(randint(100, 1000) / 100.0, 2),  # Prices between $1.00 and $10.00
        randint(10, 200),  # Quantities between 10 and 200
        farmer_id,
        choice(shipping_options)
    ))
    cursor.execute('SELECT id FROM product WHERE name = ? AND farmer_id = ?', (name, farmer_id))
    product_id = cursor.fetchone()
    if product_id:
        products.append(product_id[0])

# Commit products
conn.commit()

# Insert orders
for i in range(100):
    product_id = choice(products)
    buyer = choice(farmers)  # Buyers are farmers for simplicity
    quantity = randint(1, 10)
    status = choice(statuses)
    # Random order date within the last 30 days
    order_date = datetime.now() - timedelta(days=randint(0, 30))
    cursor.execute('''
        INSERT OR IGNORE INTO "order" (buyer_name, buyer_email, product_id, quantity, status, order_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        buyer[1],  # buyer_name
        buyer[2],  # buyer_email
        product_id,
        quantity,
        status,
        order_date.strftime('%Y-%m-%d %H:%M:%S')
    ))

# Commit and close
conn.commit()
conn.close()

print("Database initialized with a large amount of sample data.")