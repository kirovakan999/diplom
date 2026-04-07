import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

# Конфигурация базы данных
DB_CONFIG = {
    'host': 'localhost',
    'database': 'car_audio_shop',
    'user': 'root',  # Ваш пользователь MySQL
    'password': '',  # Ваш пароль MySQL
    'charset': 'utf8mb4'
}

@contextmanager
def get_db_connection():
    """Контекстный менеджер для работы с БД"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        yield connection
    except Error as e:
        print(f"Ошибка подключения к БД: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()

class Database:
    @staticmethod
    def get_all_products(category_id=None):
        """Получить все товары или по категории"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            if category_id:
                cursor.execute("""
                    SELECT p.*, c.name as category_name, c.icon as category_icon 
                    FROM products p 
                    JOIN categories c ON p.category_id = c.id 
                    WHERE p.category_id = %s 
                    ORDER BY p.id DESC
                """, (category_id,))
            else:
                cursor.execute("""
                    SELECT p.*, c.name as category_name, c.icon as category_icon 
                    FROM products p 
                    JOIN categories c ON p.category_id = c.id 
                    ORDER BY p.id DESC
                """)
            return cursor.fetchall()
    
    @staticmethod
    def get_new_products(limit=8):
        """Получить новинки"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, c.name as category_name 
                FROM products p 
                JOIN categories c ON p.category_id = c.id 
                WHERE p.is_new = TRUE 
                ORDER BY p.created_at DESC 
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
    
    @staticmethod
    def get_all_categories():
        """Получить все категории"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categories ORDER BY id")
            return cursor.fetchall()
    
    @staticmethod
    def add_product(name, brand, price, category_id, specs, image_icon, is_new):
        """Добавить товар"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, brand, price, category_id, specs, image_icon, is_new)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, brand, price, category_id, specs, image_icon, is_new))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update_product(product_id, name, brand, price, category_id, specs, image_icon, is_new):
        """Обновить товар"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products 
                SET name=%s, brand=%s, price=%s, category_id=%s, specs=%s, image_icon=%s, is_new=%s
                WHERE id=%s
            """, (name, brand, price, category_id, specs, image_icon, is_new, product_id))
            conn.commit()
            return cursor.rowcount
    
    @staticmethod
    def delete_product(product_id):
        """Удалить товар"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
            conn.commit()
            return cursor.rowcount
    
    @staticmethod
    def get_product_by_id(product_id):
        """Получить товар по ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
            return cursor.fetchone()
    
    @staticmethod
    def add_install_request(name, phone, message):
        """Добавить заявку на установку"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO install_requests (name, phone, message)
                VALUES (%s, %s, %s)
            """, (name, phone, message))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_install_requests(status=None):
        """Получить заявки на установку"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            if status:
                cursor.execute("SELECT * FROM install_requests WHERE status=%s ORDER BY created_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM install_requests ORDER BY created_at DESC")
            return cursor.fetchall()
    
    @staticmethod
    def update_request_status(request_id, status):
        """Обновить статус заявки"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE install_requests SET status=%s WHERE id=%s", (status, request_id))
            conn.commit()
            return cursor.rowcount
    
    @staticmethod
    def verify_admin(username, password):
        """Проверка администратора (упрощённая версия)"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()
            if user:
                # В реальном проекте используйте hashlib или werkzeug.security
                if password == 'admin123':  # Временное решение
                    return user
            return None