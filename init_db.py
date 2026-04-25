import os
import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

def init_db():
    # .env dosyasındaki gizli değişkenleri sisteme yükler
    load_dotenv()

    # Artık linki koda yazmıyoruz, güvenli bir şekilde çekiyoruz
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("HATA: .env dosyasında DATABASE_URL bulunamadı!")
        return

    # Veritabanına bağlan
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    # 1. USERS Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # 2. CATEGORIES Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            icon TEXT
        )
    ''')

    # 3. PRODUCTS Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            tag TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # Önce tablolarda veri var mı diye kontrol edelim
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        hashed_pw = generate_password_hash('123456')
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', ('admin', hashed_pw))

        categories = [
            ('PS Saatlik Ücretler', '🕹️'),
            ('Maç Günleri', '⚽'),
            ('İçecekler', '☕'),
            ('Atıştırmalıklar', '🍿')
        ]
        cursor.executemany('INSERT INTO categories (name, icon) VALUES (%s, %s)', categories)

        products = [
            (1, 'Bireysel (1 Kişi)', 'PS5 veya PS4 — 1 saat', 60.0, None),
            (1, '2 Kişilik Paket', 'Aynı konsol — 1 saat', 100.0, 'Popüler'),
            (2, 'Maç Grubu Paketi', '4 kişi — içecek dahil', 200.0, 'Popüler'),
            (3, 'Türk Kahvesi', 'Sade, orta veya şekerli', 25.0, None),
            (3, 'Soğuk Kahve', 'Iced latte / cold brew', 45.0, 'Yeni'),
            (4, 'Popcorn', 'Tuzlu veya karamel — büyük boy', 30.0, 'Popüler'),
            (4, 'Gamer Combo', 'Energy + Popcorn + Cips', 90.0, 'Avantajlı')
        ]
        cursor.executemany('''
            INSERT INTO products (category_id, name, description, price, tag) 
            VALUES (%s, %s, %s, %s, %s)
        ''', products)

        print("Veritabanı oluşturuldu ve örnek veriler başarıyla eklendi!")
    else:
        print("Veritabanı zaten dolu, yeni veri eklenmedi.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()