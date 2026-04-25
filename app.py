import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

# .env dosyasındaki gizli verileri (DATABASE_URL) sisteme yükler
load_dotenv()

app = Flask(__name__)
app.secret_key = 'cosmos_cafe_cok_gizli_anahtar'

# Postgres Baglantisi
def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("HATA: DATABASE_URL bulunamadı. .env dosyanı kontrol et!")

    # Postgres için bağlantıyı kuruyoruz
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return conn

# --- MÜŞTERİ (PUBLİC) ROTALARI ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    db = get_db_connection()
    cursor = db.cursor() # Postgres'te cursor açmak şart kanka

    cursor.execute('SELECT * FROM categories')
    categories_query = cursor.fetchall()

    menu_data = []
    for cat in categories_query:
        # Soru işareti (?) yerine %s kullanıyoruz
        cursor.execute(
            'SELECT * FROM products WHERE category_id = %s AND is_active = 1',
            (cat['id'],)
        )
        items = cursor.fetchall()

        menu_data.append({
            'name': cat['name'],
            'icon': cat['icon'],
            'products': items
        })

    cursor.close()
    db.close()
    return render_template('menu.html', categories=menu_data)

@app.route('/about')
def about():
    return render_template('about.html')


# --- ADMİN PANELİ ROTALARI ---

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if 'logged_in' in session:
        return redirect(url_for('admin_dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Kullanıcı adı veya şifre hatalı dostum!'

    return render_template('admin_login.html', error=error)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute('''
        SELECT p.*, c.name as cat_name 
        FROM products p 
        JOIN categories c ON p.category_id = c.id
        ORDER BY p.category_id, p.id
    ''')
    products = cursor.fetchall()

    cursor.execute('SELECT * FROM categories')
    categories = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_dashboard.html', products=products, categories=categories)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

# Ürün güncelleme rotası (POST ile çalışır)
@app.route('/admin/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    # Formdan gelen tum verileri yakaliyoruz
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    tag = request.form.get('tag')
    is_active = 1 if request.form.get('is_active') else 0

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute('''
        UPDATE products 
        SET name = %s, description = %s, price = %s, tag = %s, is_active = %s 
        WHERE id = %s
    ''', (name, description, price, tag, is_active, product_id))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('admin_dashboard'))

# Menuye yeni urun ekleme rotasi
@app.route('/admin/add', methods=['POST'])
def add_product():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    cat_id = request.form.get('category_id')
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    tag = request.form.get('tag')

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute('''
        INSERT INTO products (category_id, name, description, price, tag, is_active)
        VALUES (%s, %s, %s, %s, %s, 1)
    ''', (cat_id, name, description, price, tag))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('admin_dashboard'))

# Urunu veritabanindan tamamen silme rotasi
@app.route('/admin/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute('DELETE FROM products WHERE id = %s', (product_id,))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)