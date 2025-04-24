# Farm Cart

Farm Cart is a Flask-based web application that serves as an online marketplace for farmers to list, manage, and sell their products directly to consumers. It provides features for farmers to add products, manage orders, view insights, and interact with customers through a contact form. The application is built with a focus on simplicity, security, and usability, using Tailwind CSS for styling and SQLite for data storage.

## Features

- **User Authentication**: Farmers can sign up, log in, and manage their profiles securely.
- **Product Management**: Farmers can add, edit, and view their product listings with details like name, description, price, quantity, and shipping options.
- **Order Management**: Farmers can view and update the status of orders received (as sellers) and track orders placed (as buyers).
- **Dashboard**: A centralized dashboard provides quick access to orders, products, insights, and customer support, with summary statistics.
- **Insights**: Location-based product and crop recommendations, including a profit graph for suggested crops (specific to Bhopal, Madhya Pradesh).
- **Search and Filter**: Users can search products by name/description and filter by farmer name.
- **Responsive Design**: Built with Tailwind CSS for a clean, mobile-friendly interface.
- **API Endpoints**: RESTful APIs for registering farmers, managing products, and placing orders programmatically.

## Tech Stack

- **Backend**: Flask (Python), Flask-SQLAlchemy, Flask-Login
- **Frontend**: Jinja2 templates, Tailwind CSS, Chart.js (for insights graph)
- **Database**: SQLite
- **Security**: Werkzeug for password hashing
- **Logging**: Python's logging module for debugging and monitoring
- **Dependencies**: Managed via `requirements.txt`

## Prerequisites

To run Farm Cart locally, ensure you have the following installed:

- Python 3.8+
- pip (Python package manager)
- Git (for cloning the repository)
- A web browser (e.g., Chrome, Firefox)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yash-goyal-0910/farm_cart.git
   cd farm_cart
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables** (optional):
   - Create a `.env` file in the root directory if you want to customize the secret key or database path:
     ```env
     SECRET_KEY=your-secret-key
     DB_PATH=/path/to/farmers_market.db
     ```
   - Default values are provided in `app.py` if not set.

5. **Initialize the Database**:
   - The SQLite database (`farmers_market.db`) is created automatically when you run the app for the first time.

6. **Run the Application**:
   ```bash
   python app.py
   ```
   - The app will start at `http://localhost:5000`.

## Usage

1. **Access the Application**:
   - Open `http://localhost:5000` in your browser.

2. **Sign Up**:
   - Navigate to `/signup` to create a farmer account with name, email, password, phone, and address.
   - Example: Sign up with `email: farmer@example.com`, `password: securepassword`.

3. **Log In**:
   - Go to `/login` and use your credentials to access the dashboard.

4. **Dashboard**:
   - At `/dashboard`, view:
     - Summary of listed products and received orders.
     - Quick links to:
       - **Orders** (`/orders`): View and manage orders.
       - **Products** (`/products`): Add and edit product listings.
       - **Insights** (`/insights`): See crop and product recommendations.
       - **Contact Us** (`/dashboard/contact`): Submit queries.

5. **Manage Products**:
   - Go to `/products` to:
     - Add a new product (e.g., Name: "Wheat", Price: ₹2.50/kg, Quantity: 100, Shipping: "Self Ship").
     - View and edit existing products via `/product/<product_id>`.

6. **Manage Orders**:
   - Go to `/orders` to:
     - View **Orders Received** (as a seller) and update their status (Pending, Completed, Cancelled).
     - View **Orders Placed** (as a buyer).

7. **Place an Order**:
   - Browse products at `/`, use search/filter, and click "Order Now" to place an order at `/order/<product_id>` (requires login).

8. **View Insights**:
   - Go to `/insights` to see product and crop recommendations for Bhopal, Madhya Pradesh, with a profit graph.

9. **Contact Support**:
   - Submit queries via `/dashboard/contact`.

10. **API Usage**:
    - Example: Register a farmer via API:
      ```bash
      curl -X POST http://localhost:5000/api/farmers/register \
      -H "Content-Type: application/json" \
      -d '{"name":"John Doe","email":"john@example.com","password":"securepassword","phone":"1234567890","address":"123 Farm Road"}'
      ```
    - See `app.py` for other endpoints (`/api/products`, `/api/orders`, etc.).

## Project Structure

```
farm_cart/
├── templates/
│   ├── base.html          # Base template with navbar and Tailwind CSS
│   ├── index.html        # Home page with product listings
│   ├── dashboard.html    # Farmer dashboard with summary and navigation
│   ├── products.html     # Manage products (add/edit)
│   ├── orders.html       # View and manage orders
│   ├── insights.html     # Crop/product recommendations and profit graph
│   ├── contact_us.html   # Contact form
│   ├── login.html        # Farmer login page
│   ├── signup.html       # Farmer signup page
│   ├── product.html      # Edit individual product
│   ├── order.html        # Place order for a product
│   ├── profile.html      # Farmer profile and order history
├── app.py                # Flask application with routes and logic
├── requirements.txt      # Python dependencies
├── farmers_market.db     # SQLite database (created on first run)
├── README.md             # This file
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request with a clear description of your changes.

Please ensure your code follows:
- PEP 8 style guidelines.
- Consistent Tailwind CSS usage.
- Proper error handling and logging.

## Issues

If you encounter bugs or have feature requests:
- Open an issue at `https://github.com/yash-goyal-0910/farm_cart/issues`.
- Provide details like steps to reproduce, expected behavior, and screenshots (if applicable).

## Contact

For questions or support:
- Author: Yash Goyal
- GitHub: [yash-goyal-0910](https://github.com/yash-goyal-0910)
- Email: [yashgoyal09102005@gmail.com](yashgoyal09102005@gmail.com)

Happy farming with Farm Cart! 🌾
