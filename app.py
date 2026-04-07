from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from database import Database
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
CORS(app)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# API: Получить все товары
@app.route('/api/products')
def get_products():
    category = request.args.get('category')
    if category and category != 'all':
        products = Database.get_all_products(int(category))
    else:
        products = Database.get_all_products()
    return jsonify(products)

# API: Получить новинки
@app.route('/api/new-products')
def get_new_products():
    products = Database.get_new_products(8)
    return jsonify(products)

# API: Получить категории
@app.route('/api/categories')
def get_categories():
    categories = Database.get_all_categories()
    return jsonify(categories)

# API: Добавить заявку на установку
@app.route('/api/install-request', methods=['POST'])
def add_install_request():
    data = request.json
    request_id = Database.add_install_request(
        data.get('name'),
        data.get('phone'),
        data.get('message', '')
    )
    return jsonify({'success': True, 'request_id': request_id})

# Админ-панель: вход
@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

# Админ-панель: главная
@app.route('/admin')
def admin_panel():
    # Проверка сессии (упрощённо)
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    categories = Database.get_all_categories()
    return render_template('admin_panel.html', categories=categories)

# API: Админ-логин
@app.route('/api/admin/login', methods=['POST'])
def admin_auth():
    data = request.json
    user = Database.verify_admin(data.get('username'), data.get('password'))
    if user:
        session['is_admin'] = True
        session['username'] = user['username']
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Неверные данные'})

# API: Админ-логаут
@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({'success': True})

# API: Добавить товар (админ)
@app.route('/api/admin/products', methods=['POST'])
def add_product():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    data = request.json
    product_id = Database.add_product(
        data.get('name'),
        data.get('brand'),
        data.get('price'),
        data.get('category_id'),
        data.get('specs'),
        data.get('image_icon', '🔊'),
        data.get('is_new', False)
    )
    return jsonify({'success': True, 'product_id': product_id})

# API: Обновить товар (админ)
@app.route('/api/admin/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    data = request.json
    rows = Database.update_product(
        product_id,
        data.get('name'),
        data.get('brand'),
        data.get('price'),
        data.get('category_id'),
        data.get('specs'),
        data.get('image_icon', '🔊'),
        data.get('is_new', False)
    )
    return jsonify({'success': rows > 0})

# API: Удалить товар (админ)
@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    rows = Database.delete_product(product_id)
    return jsonify({'success': rows > 0})

# API: Получить заявки на установку (админ)
@app.route('/api/admin/install-requests')
def get_install_requests():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Не авторизован'}), 401
    requests = Database.get_install_requests()
    return jsonify(requests)

if __name__ == '__main__':
    app.run(debug=True, port=5000)