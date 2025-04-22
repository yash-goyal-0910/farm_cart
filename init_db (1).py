import sqlite3
from datetime import datetime

# Connect to SQLite database (creates farmers_market.db if it doesn't exist)
conn = sqlite3.connect('farmers_market.db')
cursor = conn.cursor()

# Create Farmer table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS farmer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        address TEXT
    )
''')

# Create Product table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        farmer_id INTEGER NOT NULL,
        FOREIGN KEY (farmer_id) REFERENCES farmer (id)
    )
''')

# Create Order table (quote "order" to avoid reserved keyword issue)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS "order" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_name TEXT NOT NULL,
        buyer_email TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT DEFAULT 'Pending',
        order_date TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES product (id)
    )
''')

# Insert sample data
# Farmers
cursor.executemany('''
    INSERT OR IGNORE INTO farmer (name, email, phone, address) VALUES (?, ?, ?, ?)
''', [
    ('John Doe', 'john@example.com', '123-456-7890', '123 Farm Road, Ruralville'),
    ('Jane Smith', 'jane@example.com', '098-765-4321', '456 Orchard Lane, Agritown')
])

# Products
cursor.executemany('''
    INSERT OR IGNORE INTO product (name, description, price, quantity, farmer_id) VALUES (?, ?, ?, ?, ?)
''', [
    ('Organic Apples', 'Fresh red apples from our orchard', 2.5, 100, 1),
    ('Free-range Eggs', 'Dozen large brown eggs', 4.0, 50, 2),
    ('Tomatoes', 'Heirloom tomatoes, vine-ripened', 3.0, 80, 1)
])

# Orders
cursor.executemany('''
    INSERT OR IGNORE INTO "order" (buyer_name, buyer_email, product_id, quantity, status, order_date) VALUES (?, ?, ?, ?, ?, ?)
''', [
    ('Alice Brown', 'alice@example.com', 1, 5, 'Pending', datetime.utcnow().isoformat()),
    ('Bob Wilson', 'bob@example.com', 2, 2, 'Completed', datetime.utcnow().isoformat())
])

# Commit changes and close connection
conn.commit()
conn.close()

print("Database initialized successfully with sample data.")