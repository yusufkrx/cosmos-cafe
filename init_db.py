import os
import psycopg2
from werkzeug.security import generate_password_hash

def init_db():
    database_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    # SQLite'daki AUTOINCREMENT yerine Postgres'te SERIAL kullanilir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')


    conn.commit()
    conn.close()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY SERIAL,
            name TEXT NOT NULL,
            icon TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY SERIAL,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            tag TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:

        hashed_pw = generate_password_hash('123456')
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', hashed_pw))

        # Örnek Kategoriler
        categories = [
            ('PS Saatlik Ücretler', '🕹️'),
            ('Maç Günleri', '⚽'),
            ('İçecekler', '☕'),
            ('Atıştırmalıklar', '🍿')
        ]
        cursor.executemany('INSERT INTO categories (name, icon) VALUES (?, ?)', categories)

        # Örnek Ürünler (Tuple sırası: category_id, name, description, price, tag)
        products = [
            # PS Kategorisi (ID 1)
            (1, 'Bireysel (1 Kişi)', 'PS5 veya PS4 — 1 saat', 60.0, None),
            (1, '2 Kişilik Paket', 'Aynı konsol — 1 saat', 100.0, 'Popüler'),

            # Maç Kategorisi (ID 2)
            (2, 'Maç Grubu Paketi', '4 kişi — içecek dahil', 200.0, 'Popüler'),

            # İçecekler (ID 3)
            (3, 'Türk Kahvesi', 'Sade, orta veya şekerli', 25.0, None),
            (3, 'Soğuk Kahve', 'Iced latte / cold brew', 45.0, 'Yeni'),

            # Atıştırmalıklar (ID 4)
            (4, 'Popcorn', 'Tuzlu veya karamel — büyük boy', 30.0, 'Popüler'),
            (4, 'Gamer Combo', 'Energy + Popcorn + Cips', 90.0, 'Avantajlı')
        ]
        cursor.executemany('''
            INSERT INTO products (category_id, name, description, price, tag) 
            VALUES (?, ?, ?, ?, ?)
        ''', products)

        print("Veritabanı oluşturuldu ve örnek veriler eklendi!")
    else:
        print("Veritabanı zaten mevcut, yeni veri eklenmedi.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()