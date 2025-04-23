import sqlite3
import hashlib

# Connect to the database
conn = sqlite3.connect('farmers_market.db')
cursor = conn.cursor()

# Create farmer table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS farmer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        phone TEXT,
        address TEXT
    )
''')

# Create product table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        shipping_option TEXT NOT NULL,
        FOREIGN KEY (farmer_id) REFERENCES farmer(id)
    )
''')

# Create orders table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER,
        product_id INTEGER,
        buyer_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES farmer(id),
        FOREIGN KEY (product_id) REFERENCES product(id)
    )
''')

# Create crop_suggestions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS crop_suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT NOT NULL,
        district TEXT,
        state TEXT NOT NULL,
        soil_type TEXT NOT NULL,
        popular_crop TEXT NOT NULL,
        recommended_seeds TEXT,
        best_fertilizers TEXT,
        irrigation_technique TEXT,
        yield_estimate REAL,
        suitability_score INTEGER
    )
''')

# Insert crop_suggestions data
crop_data = [
    # Madhya Pradesh
    ('Central India', 'Bhopal', 'Madhya Pradesh', 'Black', 'Soybean', 'HYV Soybean JS 335', 'NPK, Gypsum', 'Drip Irrigation', 2.5, 85),
    ('Central India', 'Indore', 'Madhya Pradesh', 'Black', 'Wheat', 'Durum Wheat HD 2967', 'NPK, Organic Manure', 'Flood Irrigation', 3.0, 88),
    ('Central India', 'Jabalpur', 'Madhya Pradesh', 'Alluvial', 'Rice', 'HYV IR 64', 'NPK, Urea', 'Flood Irrigation', 2.8, 82),
    ('Central India', 'Ujjain', 'Madhya Pradesh', 'Black', 'Chickpea', 'HYV JG 11', 'NPK, Micronutrients', 'Drip Irrigation', 1.2, 80),
    ('Central India', 'Gwalior', 'Madhya Pradesh', 'Alluvial', 'Maize', 'HYV DMH 11', 'NPK, Compost', 'Sprinkler Irrigation', 2.0, 78),
    ('Central India', 'Sagar', 'Madhya Pradesh', 'Black', 'Cotton', 'Bt Cotton', 'NPK, Gypsum', 'Drip Irrigation', 1.8, 75),
    # Uttar Pradesh
    ('Northern India', 'Lucknow', 'Uttar Pradesh', 'Alluvial', 'Rice', 'HYV Pusa Basmati 1121', 'NPK, Zinc', 'Drip Irrigation', 3.2, 90),
    ('Northern India', 'Kanpur', 'Uttar Pradesh', 'Alluvial', 'Wheat', 'HYV PBW 550', 'NPK, Sulphur', 'Flood Irrigation', 3.5, 92),
    ('Northern India', 'Varanasi', 'Uttar Pradesh', 'Alluvial', 'Sugarcane', 'CO 0238', 'NPK, Organic Matter', 'Drip Irrigation', 70.0, 85),
    # Punjab
    ('Northern India', 'Ludhiana', 'Punjab', 'Alluvial', 'Wheat', 'HYV PBW 343', 'NPK, Zinc', 'Drip Irrigation', 4.0, 95),
    ('Northern India', 'Amritsar', 'Punjab', 'Alluvial', 'Rice', 'HYV PR 114', 'NPK, Potash', 'Flood Irrigation', 3.8, 93),
    # Karnataka
    ('Southern India', 'Bengaluru', 'Karnataka', 'Red', 'Coffee', 'Arabica Selection 9', 'Organic Matter', 'Rainwater Harvesting', 1.0, 80),
    ('Southern India', 'Mysuru', 'Karnataka', 'Laterite', 'Maize', 'HYV NK 6240', 'NPK, Compost', 'Sprinkler Irrigation', 2.2, 78),
    # Rajasthan
    ('Western India', 'Jaipur', 'Rajasthan', 'Sandy', 'Millet', 'HYV RHB 173', 'NPK, Farmyard Manure', 'Drip Irrigation', 1.5, 75),
    ('Western India', 'Jodhpur', 'Rajasthan', 'Sandy', 'Mustard', 'HYV NRCHB 101', 'NPK, Sulphur', 'Drip Irrigation', 1.2, 72),
    # Gujarat
    ('Western India', 'Ahmedabad', 'Gujarat', 'Alluvial', 'Cotton', 'Bt Cotton BG II', 'NPK, Gypsum', 'Drip Irrigation', 2.0, 80),
    ('Western India', 'Surat', 'Gujarat', 'Black', 'Groundnut', 'HYV GG 20', 'NPK, Micronutrients', 'Drip Irrigation', 1.8, 78),
    # Tamil Nadu
    ('Southern India', 'Chennai', 'Tamil Nadu', 'Red', 'Rice', 'HYV ADT 43', 'NPK, Urea', 'Flood Irrigation', 2.9, 85),
    ('Southern India', 'Coimbatore', 'Tamil Nadu', 'Laterite', 'Banana', 'Grand Naine', 'NPK, Organic Matter', 'Drip Irrigation', 40.0, 82),
    # Maharashtra
    ('Western India', 'Pune', 'Maharashtra', 'Black', 'Sugarcane', 'CO 86032', 'NPK, Compost', 'Drip Irrigation', 65.0, 88),
    ('Western India', 'Nagpur', 'Maharashtra', 'Alluvial', 'Orange', 'Mosambi', 'NPK, Micronutrients', 'Drip Irrigation', 15.0, 85),
    # Andhra Pradesh
    ('Southern India', 'Vijayawada', 'Andhra Pradesh', 'Alluvial', 'Rice', 'HYV MTU 1010', 'NPK, Zinc', 'Flood Irrigation', 3.0, 87),
    ('Southern India', 'Visakhapatnam', 'Andhra Pradesh', 'Red', 'Cashew', 'HYV VRI 3', 'Organic Matter', 'Rainwater Harvesting', 0.8, 75),
    # Haryana
    ('Northern India', 'Chandigarh', 'Haryana', 'Alluvial', 'Wheat', 'HYV HD 3086', 'NPK, Sulphur', 'Drip Irrigation', 3.7, 94),
    ('Northern India', 'Faridabad', 'Haryana', 'Alluvial', 'Mustard', 'HYV RH 749', 'NPK, Micronutrients', 'Drip Irrigation', 1.3, 80),
    # Bihar
    ('Eastern India', 'Patna', 'Bihar', 'Alluvial', 'Rice', 'HYV Rajendra Mahsuri', 'NPK, Urea', 'Flood Irrigation', 2.7, 83),
    ('Eastern India', 'Bhagalpur', 'Bihar', 'Alluvial', 'Maize', 'HYV DKC 9144', 'NPK, Compost', 'Sprinkler Irrigation', 2.1, 79),
    # West Bengal
    ('Eastern India', 'Kolkata', 'West Bengal', 'Alluvial', 'Rice', 'HYV Swarna Sub1', 'NPK, Zinc', 'Flood Irrigation', 2.9, 86),
    ('Eastern India', 'Darjeeling', 'West Bengal', 'Laterite', 'Tea', 'Assam Hybrid', 'Organic Matter', 'Rainwater Harvesting', 1.5, 80),
    # Odisha
    ('Eastern India', 'Bhubaneswar', 'Odisha', 'Red', 'Rice', 'HYV Pooja', 'NPK, Urea', 'Flood Irrigation', 2.6, 84),
    ('Eastern India', 'Cuttack', 'Odisha', 'Alluvial', 'Pulses', 'HYV Pusa 256', 'NPK, Micronutrients', 'Drip Irrigation', 1.0, 76),
    # Assam
    ('Northeastern India', 'Guwahati', 'Assam', 'Alluvial', 'Rice', 'HYV Ranjit', 'NPK, Organic Matter', 'Flood Irrigation', 2.8, 85),
    ('Northeastern India', 'Dibrugarh', 'Assam', 'Laterite', 'Tea', 'Darjeeling Clone', 'Organic Matter', 'Rainwater Harvesting', 1.4, 79),
    # Jammu & Kashmir
    ('Northern India', 'Srinagar', 'Jammu & Kashmir', 'Alluvial', 'Apple', 'Golden Delicious', 'NPK, Compost', 'Drip Irrigation', 12.0, 90),
    ('Northern India', 'Jammu', 'Jammu & Kashmir', 'Alluvial', 'Walnut', 'Chakri Variety', 'Organic Matter', 'Rainwater Harvesting', 0.9, 75),
    # Kerala
    ('Southern India', 'Thiruvananthapuram', 'Kerala', 'Laterite', 'Rubber', 'RRII 105', 'NPK, Organic Matter', 'Drip Irrigation', 1.2, 80),
    ('Southern India', 'Kochi', 'Kerala', 'Alluvial', 'Coconut', 'Chowghat Orange Dwarf', 'NPK, Micronutrients', 'Drip Irrigation', 8.0, 83),
]

cursor.executemany('INSERT OR IGNORE INTO crop_suggestions (region, district, state, soil_type, popular_crop, recommended_seeds, best_fertilizers, irrigation_technique, yield_estimate, suitability_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', crop_data)

# Helper function to hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Insert large sample of farmers with default password 'default123'
default_password_hash = hash_password('default123')
farmers_data = [
    ('Ramesh Sharma', 'ramesh.sharma@example.com', default_password_hash, '9876543210', '123 MG Road, Bhopal, Madhya Pradesh'),
    ('Sita Patel', 'sita.patel@example.com', default_password_hash, '8765432109', '45 Indore Main St, Indore, Madhya Pradesh'),
    ('Vikram Singh', 'vikram.singh@example.com', default_password_hash, '7654321098', '78 Jabalpur Lane, Jabalpur, Madhya Pradesh'),
    ('Anita Yadav', 'anita.yadav@example.com', default_password_hash, '6543210987', '12 Ujjain Rd, Ujjain, Madhya Pradesh'),
    ('Kiran Gupta', 'kiran.gupta@example.com', default_password_hash, '5432109876', '34 Gwalior St, Gwalior, Madhya Pradesh'),
    ('Mohan Kumar', 'mohan.kumar@example.com', default_password_hash, '4321098765', '56 Sagar Ave, Sagar, Madhya Pradesh'),
    ('Priya Sharma', 'priya.sharma@example.com', default_password_hash, '3210987654', '89 Lucknow Rd, Lucknow, Uttar Pradesh'),
    ('Amit Singh', 'amit.singh@example.com', default_password_hash, '2109876543', '23 Kanpur Lane, Kanpur, Uttar Pradesh'),
    ('Neha Reddy', 'neha.reddy@example.com', default_password_hash, '1098765432', '45 Varanasi St, Varanasi, Uttar Pradesh'),
    ('Rahul Verma', 'rahul.verma@example.com', default_password_hash, '9988776655', '67 Ludhiana Rd, Ludhiana, Punjab'),
    ('Sunita Kaur', 'sunita.kaur@example.com', default_password_hash, '8877665544', '12 Amritsar Ave, Amritsar, Punjab'),
    ('Arjun Patil', 'arjun.patil@example.com', default_password_hash, '7766554433', '34 Bengaluru St, Bengaluru, Karnataka'),
    ('Lata Shetty', 'lata.shetty@example.com', default_password_hash, '6655443322', '56 Mysuru Rd, Mysuru, Karnataka'),
    ('Rajesh Jain', 'rajesh.jain@example.com', default_password_hash, '5544332211', '78 Jaipur Lane, Jaipur, Rajasthan'),
    ('Meena Desai', 'meena.desai@example.com', default_password_hash, '4433221100', '90 Jodhpur St, Jodhpur, Rajasthan'),
    ('Suresh Patel', 'suresh.patel@example.com', default_password_hash, '3322110099', '12 Ahmedabad Rd, Ahmedabad, Gujarat'),
    ('Geeta Nair', 'geeta.nair@example.com', default_password_hash, '2211009988', '34 Surat Ave, Surat, Gujarat'),
    ('Vijay Iyer', 'vijay.iyer@example.com', default_password_hash, '1100998877', '56 Chennai St, Chennai, Tamil Nadu'),
    ('Kavita Rao', 'kavita.rao@example.com', default_password_hash, '0998877665', '78 Coimbatore Rd, Coimbatore, Tamil Nadu'),
    ('Anil Joshi', 'anil.joshi@example.com', default_password_hash, '8877665544', '90 Pune Lane, Pune, Maharashtra'),
    ('Sneha Mehra', 'sneha.mehra@example.com', default_password_hash, '7766554433', '12 Nagpur St, Nagpur, Maharashtra'),
    ('Hari Shankar', 'hari.shankar@example.com', default_password_hash, '6655443322', '34 Vijayawada Rd, Vijayawada, Andhra Pradesh'),
    ('Lakshmi Reddy', 'lakshmi.reddy@example.com', default_password_hash, '5544332211', '56 Visakhapatnam Ave, Visakhapatnam, Andhra Pradesh'),
    ('Deepak Yadav', 'deepak.yadav@example.com', default_password_hash, '4433221100', '78 Chandigarh St, Chandigarh, Haryana'),
    ('Rita Malhotra', 'rita.malhotra@example.com', default_password_hash, '3322110099', '90 Faridabad Rd, Faridabad, Haryana'),
    ('Santosh Kumar', 'santosh.kumar@example.com', default_password_hash, '2211009988', '12 Patna Lane, Patna, Bihar'),
    ('Poonam Gupta', 'poonam.gupta@example.com', default_password_hash, '1100998877', '34 Bhagalpur St, Bhagalpur, Bihar'),
    ('Rakesh Das', 'rakesh.das@example.com', default_password_hash, '0998877665', '56 Kolkata Rd, Kolkata, West Bengal'),
    ('Anjali Roy', 'anjali.roy@example.com', default_password_hash, '8877665544', '78 Darjeeling Ave, Darjeeling, West Bengal'),
    ('Babu Rao', 'babu.rao@example.com', default_password_hash, '7766554433', '90 Bhubaneswar St, Bhubaneswar, Odisha'),
    ('Seema Jena', 'seema.jena@example.com', default_password_hash, '6655443322', '12 Cuttack Rd, Cuttack, Odisha'),
    ('Prakash Bora', 'prakash.bora@example.com', default_password_hash, '5544332211', '34 Guwahati Lane, Guwahati, Assam'),
    ('Rina Saikia', 'rina.saikia@example.com', default_password_hash, '4433221100', '56 Dibrugarh St, Dibrugarh, Assam'),
    ('Vikram Singh', 'vikram.singh2@example.com', default_password_hash, '3322110099', '78 Srinagar Rd, Srinagar, Jammu & Kashmir'),
    ('Shamim Ahmad', 'shamim.ahmad@example.com', default_password_hash, '2211009988', '90 Jammu Ave, Jammu, Jammu & Kashmir'),
    ('Thomas Mathew', 'thomas.mathew@example.com', default_password_hash, '1100998877', '12 Thiruvananthapuram St, Thiruvananthapuram, Kerala'),
    ('Asha Varghese', 'asha.varghese@example.com', default_password_hash, '0998877665', '34 Kochi Rd, Kochi, Kerala'),
]

cursor.executemany('INSERT OR IGNORE INTO farmer (name, email, password_hash, phone, address) VALUES (?, ?, ?, ?, ?)', farmers_data)

# Insert large sample of products
products_data = [
    (1, 'Organic Soybean', 'Freshly harvested organic soybean', 2.50, 100, 'Self Ship'),
    (1, 'Wheat Grains', 'High-quality wheat for baking', 1.80, 150, 'Shiprocket'),
    (2, 'Indore Chickpea', 'Premium chickpea from Indore', 2.00, 120, 'Self Ship'),
    (2, 'Soybean Oil', 'Cold-pressed soybean oil', 5.00, 50, 'Shiprocket'),
    (3, 'Jabalpur Rice', 'Aromatic basmati rice', 3.20, 80, 'Self Ship'),
    (3, 'Wheat Flour', 'Whole wheat flour', 2.20, 200, 'Shiprocket'),
    (4, 'Ujjain Pulses', 'Mixed pulses pack', 1.50, 90, 'Self Ship'),
    (4, 'Cotton Seeds', 'Organic cotton seeds', 1.00, 300, 'Shiprocket'),
    (5, 'Gwalior Maize', 'Sweet corn maize', 1.80, 110, 'Self Ship'),
    (5, 'Rice Bran', 'Nutritious rice bran', 2.50, 60, 'Shiprocket'),
    (6, 'Sagar Cotton', 'Organic cotton bales', 4.00, 40, 'Self Ship'),
    (6, 'Soybean Meal', 'Protein-rich meal', 3.00, 70, 'Shiprocket'),
    (7, 'Lucknow Basmati', 'Premium basmati rice', 4.00, 100, 'Self Ship'),
    (7, 'Wheat Atta', 'Finest wheat atta', 2.50, 150, 'Shiprocket'),
    (8, 'Kanpur Sugarcane', 'Fresh sugarcane juice', 1.20, 200, 'Self Ship'),
    (8, 'Rice Powder', 'Organic rice powder', 2.00, 80, 'Shiprocket'),
    (9, 'Varanasi Wheat', 'Organic whole wheat', 1.90, 130, 'Self Ship'),
    (9, 'Sugarcane Jaggery', 'Natural jaggery', 3.50, 50, 'Shiprocket'),
    (10, 'Ludhiana Wheat', 'Premium wheat grains', 2.10, 140, 'Self Ship'),
    (10, 'Punjab Rice', 'Aromatic rice', 3.50, 90, 'Shiprocket'),
    (11, 'Amritsar Basmati', 'Long-grain basmati', 4.20, 70, 'Self Ship'),
    (11, 'Wheat Bran', 'Nutritious bran', 1.80, 100, 'Shiprocket'),
    (12, 'Bengaluru Coffee', 'Arabica coffee beans', 6.00, 40, 'Self Ship'),
    (12, 'Maize Flour', 'Organic maize flour', 2.30, 90, 'Shiprocket'),
    (13, 'Mysuru Maize', 'Sweet corn', 1.90, 110, 'Self Ship'),
    (13, 'Coffee Powder', 'Freshly ground coffee', 5.50, 50, 'Shiprocket'),
    (14, 'Jaipur Millet', 'Organic millet', 2.00, 120, 'Self Ship'),
    (14, 'Mustard Oil', 'Cold-pressed oil', 4.00, 60, 'Shiprocket'),
    (15, 'Jodhpur Mustard', 'Premium mustard seeds', 2.20, 80, 'Self Ship'),
    (15, 'Millet Flour', 'Nutritious flour', 2.10, 100, 'Shiprocket'),
    (16, 'Ahmedabad Cotton', 'Organic cotton', 3.50, 50, 'Self Ship'),
    (16, 'Groundnut Oil', 'Fresh groundnut oil', 5.00, 40, 'Shiprocket'),
    (17, 'Surat Groundnut', 'Roasted groundnuts', 2.50, 90, 'Self Ship'),
    (17, 'Cotton Yarn', 'Natural yarn', 4.20, 30, 'Shiprocket'),
    (18, 'Chennai Rice', 'Ponni rice', 3.00, 100, 'Self Ship'),
    (18, 'Banana Chips', 'Crispy banana chips', 2.00, 120, 'Shiprocket'),
    (19, 'Coimbatore Banana', 'Fresh bananas', 1.50, 150, 'Self Ship'),
    (19, 'Rice Bran Oil', 'Healthy oil', 5.50, 50, 'Shiprocket'),
    (20, 'Pune Sugarcane', 'Sweet sugarcane', 1.20, 200, 'Self Ship'),
    (20, 'Orange Juice', 'Fresh orange juice', 2.50, 80, 'Shiprocket'),
    (21, 'Nagpur Orange', 'Sweet oranges', 1.80, 110, 'Self Ship'),
    (21, 'Sugarcane Syrup', 'Natural syrup', 3.00, 60, 'Shiprocket'),
    (22, 'Vijayawada Rice', 'Sona Masoori rice', 2.90, 90, 'Self Ship'),
    (22, 'Cashew Nuts', 'Premium cashews', 6.00, 40, 'Shiprocket'),
    (23, 'Visakhapatnam Cashew', 'Roasted cashews', 5.50, 50, 'Self Ship'),
    (23, 'Rice Flour', 'Fine rice flour', 2.20, 100, 'Shiprocket'),
    (24, 'Chandigarh Wheat', 'Organic wheat', 2.00, 130, 'Self Ship'),
    (24, 'Mustard Seeds', 'Whole mustard', 1.90, 120, 'Shiprocket'),
    (25, 'Faridabad Mustard', 'Fresh mustard', 2.10, 100, 'Self Ship'),
    (25, 'Wheat Germ', 'Nutritious germ', 3.50, 70, 'Shiprocket'),
    (26, 'Patna Rice', 'Aromatic rice', 2.80, 110, 'Self Ship'),
    (26, 'Maize Meal', 'Organic meal', 2.00, 90, 'Shiprocket'),
    (27, 'Bhagalpur Maize', 'Sweet maize', 1.70, 120, 'Self Ship'),
    (27, 'Rice Husk', 'Natural husk', 1.50, 150, 'Shiprocket'),
    (28, 'Kolkata Rice', 'Gobindobhog rice', 3.20, 80, 'Self Ship'),
    (28, 'Tea Leaves', 'Darjeeling tea', 4.00, 60, 'Shiprocket'),
    (29, 'Darjeeling Tea', 'Premium tea', 4.50, 50, 'Self Ship'),
    (29, 'Rice Bran Meal', 'Protein meal', 2.80, 70, 'Shiprocket'),
    (30, 'Bhubaneswar Rice', 'Red rice', 2.90, 90, 'Self Ship'),
    (30, 'Pulses Mix', 'Mixed pulses', 1.80, 110, 'Shiprocket'),
    (31, 'Cuttack Pulses', 'Organic pulses', 1.70, 120, 'Self Ship'),
    (31, 'Rice Starch', 'Natural starch', 2.20, 80, 'Shiprocket'),
    (32, 'Guwahati Rice', 'Joha rice', 3.10, 100, 'Self Ship'),
    (32, 'Tea Powder', 'Assam tea', 4.20, 60, 'Shiprocket'),
    (33, 'Dibrugarh Tea', 'Organic tea', 4.30, 50, 'Self Ship'),
    (33, 'Rice Germ', 'Nutritious germ', 2.90, 70, 'Shiprocket'),
    (34, 'Srinagar Apple', 'Fresh apples', 2.50, 90, 'Self Ship'),
    (34, 'Walnut Kernels', 'Premium walnuts', 6.50, 40, 'Shiprocket'),
    (35, 'Jammu Walnut', 'Organic walnuts', 6.00, 50, 'Self Ship'),
    (35, 'Apple Juice', 'Natural juice', 2.80, 80, 'Shiprocket'),
    (36, 'Thiruvananthapuram Rubber', 'Natural rubber', 3.50, 60, 'Self Ship'),
    (36, 'Coconut Oil', 'Virgin coconut oil', 5.00, 40, 'Shiprocket'),
    (37, 'Kochi Coconut', 'Fresh coconuts', 2.20, 100, 'Self Ship'),
    (37, 'Rubber Sheets', 'Processed rubber', 4.00, 50, 'Shiprocket'),
]

cursor.executemany('INSERT OR IGNORE INTO product (farmer_id, name, description, price, quantity, shipping_option) VALUES (?, ?, ?, ?, ?, ?)', products_data)

# Insert example orders
orders_data = [
    (1, 1, 'Ajay Kumar', 10, 'Pending'),
    (1, 2, 'Priya Gupta', 5, 'Shipped'),
    (2, 3, 'Rahul Sharma', 15, 'Delivered'),
    (2, 4, 'Sneha Patel', 2, 'Pending'),
    (3, 5, 'Vikram Singh', 8, 'Shipped'),
    (3, 6, 'Anita Yadav', 20, 'Delivered'),
    (4, 7, 'Kiran Mehta', 12, 'Pending'),
    (4, 8, 'Mohan Das', 30, 'Shipped'),
    (5, 9, 'Sunita Rao', 7, 'Delivered'),
    (5, 10, 'Arjun Malhotra', 3, 'Pending'),
]

cursor.executemany('INSERT INTO orders (farmer_id, product_id, buyer_name, quantity, status) VALUES (?, ?, ?, ?, ?)', orders_data)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database initialized successfully with farmers, products, orders, and crop suggestions.")