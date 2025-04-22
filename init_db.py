import sqlite3
from werkzeug.security import generate_password_hash

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

# Insert sample data
# Farmers
cursor.execute('''
    INSERT OR IGNORE INTO farmer (name, email, password_hash, phone, address)
    VALUES (?, ?, ?, ?, ?)
''', (
    'John Doe',
    'john@example.com',
    generate_password_hash('default123'),
    '123-456-7890',
    '123 Farm Road'
))

cursor.execute('''
    INSERT OR IGNORE INTO farmer (name, email, password_hash, phone, address)
    VALUES (?, ?, ?, ?, ?)
''', (
    'Jane Smith',
    'jane@example.com',
    generate_password_hash('default123'),
    '098-765-4321',
    '456 Orchard Lane'
))

# Get farmer IDs
cursor.execute('SELECT id FROM farmer WHERE email = ?', ('john@example.com',))
john_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM farmer WHERE email = ?', ('jane@example.com',))
jane_id = cursor.fetchone()[0]

# Products with shipping options
cursor.execute('''
    INSERT OR IGNORE INTO product (name, description, price, quantity, farmer_id, shipping_option)
    VALUES (?, ?, ?, ?, ?, ?)
''', (
    'Organic Apples',
    'Fresh red apples from our orchard',
    2.5,
    100,
    john_id,
    'Self Ship'
))

cursor.execute('''
    INSERT OR IGNORE INTO product (name, description, price, quantity, farmer_id, shipping_option)
    VALUES (?, ?, ?, ?, ?, ?)
''', (
    'Free-range Eggs',
    'Dozen free-range chicken eggs',
    5.0,
    50,
    jane_id,
    'Shiprocket'
))

cursor.execute('''
    INSERT OR IGNORE INTO product (name, description, price, quantity, farmer_id, shipping_option)
    VALUES (?, ?, ?, ?, ?, ?)
''', (
    'Tomatoes',
    'Juicy organic tomatoes',
    3.0,
    80,
    john_id,
    'Self Ship'
))

# Orders
cursor.execute('SELECT id FROM product WHERE name = ?', ('Organic Apples',))
apple_id = cursor.fetchone()[0]

cursor.execute('''
    INSERT OR IGNORE INTO "order" (buyer_name, buyer_email, product_id, quantity, status)
    VALUES (?, ?, ?, ?, ?)
''', (
    'John Doe',
    'john@example.com',
    apple_id,
    10,
    'Pending'
))

# Commit and close
conn.commit()
conn.close()

print("Database initialized with sample data.")