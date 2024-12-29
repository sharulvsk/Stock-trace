from flask import Flask, request, jsonify, session, render_template, send_file, redirect, url_for, flash
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph
from reportlab.lib import colors
from reportlab.platypus import Image
from reportlab.lib.styles import getSampleStyleSheet
import io
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from datetime import datetime
from func import validate_user
from connection import get_connection

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key_here'


@app.route('/')
def index():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/reports')
def reports():
    try:
        conn = get_connection()
        if conn is None:
            return "Database connection error", 500
        cur = conn.cursor()

        cur.execute("""
            SELECT name, 'Electronics' AS category, stock
            FROM electronics
            WHERE stock < 10
            UNION ALL
            SELECT name, 'Groceries' AS category, stock
            FROM groceries
            WHERE stock < 10
            UNION ALL
            SELECT name, 'Clothing' AS category, stock
            FROM clothing
            WHERE stock < 10
            UNION ALL
            SELECT name, 'Household Items' AS category, stock
            FROM household_items
            WHERE stock < 10
            UNION ALL
            SELECT name, 'Personal Care' AS category, stock
            FROM personal_care
            WHERE stock < 10;
        """)
        low_inventory_items = cur.fetchall()

        cur.execute("""
            SELECT name, 'Electronics' AS category, expiry_date
            FROM electronics
            WHERE expiry_date < CURRENT_DATE
            UNION ALL
            SELECT name, 'Groceries' AS category, expiry_date
            FROM groceries
            WHERE expiry_date < CURRENT_DATE
            UNION ALL
            SELECT name, 'Clothing' AS category, expiry_date
            FROM clothing
            WHERE expiry_date < CURRENT_DATE
            UNION ALL
            SELECT name, 'Household Items' AS category, expiry_date
            FROM household_items
            WHERE expiry_date < CURRENT_DATE
            UNION ALL
            SELECT name, 'Personal Care' AS category, expiry_date
            FROM personal_care
            WHERE expiry_date < CURRENT_DATE;
        """)
        expired_items = cur.fetchall()

        cur.close()
        conn.close()

        return render_template('reports.html', low_inventory_items=low_inventory_items, expired_items=expired_items)

    except Exception as e:
        print(f"Error in reports route: {e}")
        return "An error occurred while fetching reports", 500

@app.route('/managestock', methods=['GET', 'POST'])
def manage_stock():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        items = request.form.getlist('item')
        stocks = request.form.getlist('stock')
        
        for item, stock in zip(items, stocks):
            cur.execute('UPDATE electronics SET stock = %s WHERE name = %s', (stock, item))
        
        conn.commit()
    cur.execute('SELECT name, category, stock FROM (SELECT name, \'Electronics\' AS category, stock FROM electronics UNION ALL SELECT name, \'Groceries\' AS category, stock FROM groceries UNION ALL SELECT name, \'Clothing\' AS category, stock FROM clothing UNION ALL SELECT name, \'Household Items\' AS category, stock FROM household_items UNION ALL SELECT name, \'Personal Care\' AS category, stock FROM personal_care) AS all_items')
    stock_data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('managestock.html', stock_data=stock_data)

@app.route('/dashboard')
def dashboard():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT COUNT(*) FROM (SELECT * FROM groceries UNION ALL SELECT * FROM clothing UNION ALL SELECT * FROM household_items UNION ALL SELECT * FROM personal_care UNION ALL SELECT * FROM electronics) AS all_items')
    total_items = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM categories')
    total_categories = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM (SELECT * FROM groceries WHERE stock = 0 UNION ALL SELECT * FROM clothing WHERE stock = 0 UNION ALL SELECT * FROM household_items WHERE stock = 0 UNION ALL SELECT * FROM personal_care WHERE stock = 0 UNION ALL SELECT * FROM electronics WHERE stock = 0) AS out_of_stock')
    out_of_stock = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM (SELECT * FROM groceries WHERE stock < 10 UNION ALL SELECT * FROM clothing WHERE stock < 10 UNION ALL SELECT * FROM household_items WHERE stock < 10 UNION ALL SELECT * FROM personal_care WHERE stock < 10 UNION ALL SELECT * FROM electronics WHERE stock < 10) AS low_stock')
    low_stock_alerts = cur.fetchone()[0]

    cur.execute('''
        SELECT name, category, stock FROM (
            SELECT name, 'Groceries' AS category, stock FROM groceries WHERE stock < 10
            UNION ALL
            SELECT name, 'Clothing' AS category, stock FROM clothing WHERE stock < 10
            UNION ALL
            SELECT name, 'Household Items' AS category, stock FROM household_items WHERE stock < 10
            UNION ALL
            SELECT name, 'Personal Care' AS category, stock FROM personal_care WHERE stock < 10
            UNION ALL
            SELECT name, 'Electronics' AS category, stock FROM electronics WHERE stock < 10
        ) AS low_stock_items
    ''')
    low_stock_items = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('dashboard.html', 
                           total_items=total_items,
                           total_categories=total_categories,
                           out_of_stock=out_of_stock,
                           low_stock_alerts=low_stock_alerts,
                           low_stock_items=low_stock_items)

@app.route('/clothing')
def clothing():
    try:
        conn = get_connection()
        if conn is None:
            return "Database connection error", 500
        cur = conn.cursor()
        cur.execute('SELECT * FROM clothing')
        clothing = cur.fetchall()
        print("Clothing fetched:", clothing)  
        cur.close()
        conn.close()
        return render_template('clothing.html', items=clothing)
    except Exception as e:
        print("Error fetching data:", e)
        return "Error fetching data", 500

@app.route('/groceries')
def groceries():
    try:
        conn = get_connection()
        if conn is None:
            return "Database connection error", 500
        cur = conn.cursor()
        cur.execute('SELECT * FROM groceries')
        groceries = cur.fetchall()
        print("Groceries fetched:", groceries)  
        cur.close()
        conn.close()
        return render_template('groceries.html', items=groceries)
    except Exception as e:
        print("Error fetching data:", e)
        return "Error fetching data", 500

@app.route('/householditems')
def household_items():
    try:
        conn = get_connection()
        if conn is None:
            return "Database connection error", 500
        cur = conn.cursor()
        cur.execute('SELECT * FROM household_items')
        household_items = cur.fetchall()
        print("Household items fetched:", household_items)  
        cur.close()
        conn.close()
        return render_template('householditems.html', items=household_items)
    except Exception as e:
        print("Error fetching data:", e)
        return "Error fetching data", 500

@app.route('/personalcare')
def personal_care():
    try:
        conn = get_connection()
        if conn is None:
            return "Database connection error", 500
        cur = conn.cursor()
        cur.execute('SELECT * FROM personal_care')
        personal_care_items = cur.fetchall()
        print("Personal care items fetched:", personal_care_items)  
        cur.close()
        conn.close()
        return render_template('personalcare.html', items=personal_care_items)
    except Exception as e:
        print("Error fetching data:", e)
        return "Error fetching data", 500

@app.route('/logout',methods = ['GET'])
def logout():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if validate_user(username, password):
            session['username'] = username  
            return render_template('home.html')
        else:
            return render_template('login.html', error="Invalid Username or Password.")
    
    return render_template('login.html')

@app.route('/electronics')
def electronics():
    try:
        conn = get_connection()
        if conn is None:
            return "Database connection error", 500
        cur = conn.cursor()
        cur.execute('SELECT * FROM electronics')
        electronics = cur.fetchall()
        print("Electronics fetched:", electronics) 
        cur.close()
        conn.close()
        return render_template('electronics.html', items=electronics)
    except Exception as e:
        print("Error fetching data:", e)
        return "Error fetching data", 500
    

@app.route('/additem', methods=['GET', 'POST'])
def additem():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        stock = request.form['stock']
        price = request.form['price']
        expiry_date = request.form['expiry_date']
        category = request.form['category']

        valid_categories = ['electronics', 'groceries', 'clothing', 'household_items', 'personal_care']

        if category in valid_categories:
            conn = get_connection()
            cur = conn.cursor()
            query = f"INSERT INTO {category} (name, description, stock, price, expiry_date) VALUES (%s, %s, %s, %s, %s)"
            cur.execute(query, (name, description, stock, price, expiry_date))
            conn.commit()
            cur.close()
            conn.close()
            return redirect('/dashboard')
        else:
            return "Invalid category", 400

    return render_template('additem.html')



@app.route('/removeitem', methods=['GET', 'POST'])
def removeitem():
    conn = get_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        
        category_id = request.form['category']
        cur.execute("DELETE FROM items WHERE id = %s", (category_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('dashboard'))

    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('removeitem.html', categories=categories)

@app.route('/display_category/<category>', methods=['GET'])
def display_category(category):
    try:
        valid_categories = ['electronics', 'groceries', 'clothing', 'household_items', 'personal_care']
        
        if category not in valid_categories:
            return "Invalid category", 400
        conn = get_connection()
        if conn is None:
            return "Database connection error", 500
        cur = conn.cursor()
        query = f"SELECT * FROM {category}"
        cur.execute(query)
        items = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('display_category.html', category=category, items=items)
    except Exception as e:
        print(f"Error fetching data for category {category}: {e}")
        return "An error occurred", 500

    
@app.route('/edit/<string:category>/<int:item_id>', methods=['GET', 'POST'])
def edit_item(category, item_id):
    conn = get_connection()
    if conn is None:
        return "Database connection error", 500

    cur = conn.cursor()

    valid_categories = ['electronics', 'groceries', 'clothing', 'household_items', 'personal_care']
    if category not in valid_categories:
        return "Invalid category", 400

    if request.method == 'POST':
        name = request.form.get('name', '')
        description = request.form.get('description', '')
        stock = request.form.get('stock', '')
        price = request.form.get('price', '')
        expiry_date = request.form.get('expiry_date', '')
        cur.execute(
            f'UPDATE {category} SET name=%s, description=%s, stock=%s, price=%s, expiry_date=%s WHERE id=%s',
            (name, description, stock, price, expiry_date, item_id)
        )
        conn.commit()

        cur.close()
        conn.close()
        return redirect(url_for('display_category', category=category)) 
    cur.execute(f'SELECT * FROM {category} WHERE id=%s', (item_id,))
    item = cur.fetchone()

    cur.close()
    conn.close()

    if item is None:
        return "Item not found", 404

    return render_template('edit.html', category=category, item=item)



@app.route('/delete/<string:category>/<int:item_id>', methods=['POST'])
def delete_item(category, item_id):
    try:
        conn = get_connection()
        if conn is None:
            return "Database connection error", 500

        cur = conn.cursor()

        valid_categories = ['electronics', 'groceries', 'clothing', 'household_items', 'personal_care']
        if category not in valid_categories:
            return "Invalid category", 400

        cur.execute(f'DELETE FROM {category} WHERE id=%s', (item_id,))
        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for(category))
    except Exception as e:
        print("Error deleting item:", e)
        return "Error deleting item", 500


if __name__ == "__main__":
    app.run(debug=True)
