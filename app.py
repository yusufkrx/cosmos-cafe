import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'cosmos_cafe_cok_gizli_anahtar'

# Postgres Baglantisi
def get_db_connection():
    # Render'daki veritabanı adresini çekiyoruz, lokalde test için default bir adres de koyabiliriz
    database_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return conn



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    db = get_db_connection()
    categories_query = db.execute('SELECT * FROM categories').fetchall()

    menu_data = []
    for cat in categories_query:
        items = db.execute(
            'SELECT * FROM products WHERE category_id = ? AND is_active = 1',
            (cat['id'],)
        ).fetchall()

        menu_data.append({
            'name': cat['name'],
            'icon': cat['icon'],
            'products': items
        })

    db.close()
    return render_template('menu.html', categories=menu_data)

@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if 'logged_in' in session:
        return redirect(url_for('admin_dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()

        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Kullanıcı adı veya şifre hatalı dostum!'

    return render_template('admin_login.html', error=error)

@app.route('/admin/dashboard')
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    db = get_db_connection()
    products = db.execute('''
        SELECT p.*, c.name as cat_name 
        FROM products p 
        JOIN categories c ON p.category_id = c.id
    ''').fetchall()

    # YENI: Kategorileri de cekiyoruz ki "Urun Ekle" formunda dropdown yapalim
    categories = db.execute('SELECT * FROM categories').fetchall()
    db.close()

    return render_template('admin_dashboard.html', products=products, categories=categories)
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

# Ürün güncelleme rotası (POST ile çalışır)
# Mevcut update_product fonksiyonunu bununla degistir kanka
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
    db.execute('''
        UPDATE products 
        SET name = ?, description = ?, price = ?, tag = ?, is_active = ? 
        WHERE id = ?
    ''', (name, description, price, tag, is_active, product_id))
    db.commit()
    db.close()

    return redirect(url_for('admin_dashboard'))

# YENI: Menuye yeni urun ekleme rotasi
@app.route('/admin/add', methods=['POST'])
def add_product():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    # Yeni urun bilgilerini alalim
    cat_id = request.form.get('category_id')
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    tag = request.form.get('tag')

    db = get_db_connection()
    db.execute('''
        INSERT INTO products (category_id, name, description, price, tag, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (cat_id, name, description, price, tag))
    db.commit()
    db.close()

    # YENI: Urunu veritabanindan tamamen silme rotasi
@app.route('/admin/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    db = get_db_connection()
    db.execute('DELETE FROM products WHERE id = ?', (product_id,))
    db.commit()
    db.close()

    return redirect(url_for('admin_dashboard'))


    return redirect(url_for('admin_dashboard'))
if __name__ == '__main__':
    app.run(debug=True)