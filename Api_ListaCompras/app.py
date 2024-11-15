from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
#funcao para criar as atabelas no banco de daos no SQLITE3
def init_db():
    # Cria tabelas se elas ainda não existirem
    with sqlite3.connect("shopping_list.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS block_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (block_id) REFERENCES blocks (id)
            )
        ''')
        conn.commit()

# Inicializa o banco de dados ao iniciar a aplicação
init_db()

@app.route('/add_item', methods=['POST'])
def add_item():
    try:
        data = request.get_json()
        item_name = data.get('name')

        if not item_name:
            return jsonify({'error': 'Item name is required'}), 400

        with sqlite3.connect("shopping_list.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO shopping_list (name) VALUES (?)", (item_name,))
            conn.commit()

        return jsonify({'message': 'Item added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_items', methods=['GET'])
def get_items():
    try:
        with sqlite3.connect("shopping_list.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM shopping_list")
            items = cursor.fetchall()

        items_list = [{'id': row[0], 'name': row[1]} for row in items]
        return jsonify(items_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        with sqlite3.connect("shopping_list.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shopping_list WHERE id = ?", (item_id,))
            conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Item not found'}), 404

        return jsonify({'message': 'Item deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_block', methods=['POST'])
def add_block():
    try:
        data = request.get_json()
        block_name = data.get('name')

        if not block_name:
            return jsonify({'error': 'Block name is required'}), 400

        with sqlite3.connect("shopping_list.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO blocks (name) VALUES (?)", (block_name,))
            block_id = cursor.lastrowid
            conn.commit()

        return jsonify({'message': 'Block added successfully', 'id': block_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_block_item', methods=['POST'])
def add_block_item():
    try:
        data = request.get_json()
        block_id = data.get('block_id')
        item_name = data.get('name')

        if not block_id or not item_name:
            return jsonify({'error': 'Block ID and item name are required'}), 400

        with sqlite3.connect("shopping_list.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO block_items (block_id, name) VALUES (?, ?)", (block_id, item_name))
            conn.commit()

        return jsonify({'message': 'Item added to block successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_blocks', methods=['GET'])
def get_blocks():
    try:
        with sqlite3.connect("shopping_list.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blocks")
            blocks = cursor.fetchall()

            blocks_list = []
            for block in blocks:
                cursor.execute("SELECT * FROM block_items WHERE block_id = ?", (block[0],))
                items = cursor.fetchall()
                items_list = [{'id': item[0], 'name': item[2]} for item in items]
                blocks_list.append({'id': block[0], 'name': block[1], 'items': items_list})

        return jsonify(blocks_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_block/<int:block_id>', methods=['DELETE'])
def delete_block(block_id):
    try:
        with sqlite3.connect("shopping_list.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM block_items WHERE block_id = ?", (block_id,))
            cursor.execute("DELETE FROM blocks WHERE id = ?", (block_id,))
            conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Block not found'}), 404

        return jsonify({'message': 'Block deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
