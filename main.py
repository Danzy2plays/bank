from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

USER_DATA_FILE = "users.json"

# Load user data from the JSON file
if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if username in users:
        return jsonify({"error": "User already exists"}), 400
    
    users[username] = {"password": password, "balance": 0, "is_admin": False}
    save_users()
    return jsonify({"message": "User created successfully!"}), 200

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if username not in users or users[username]["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    
    return jsonify({"message": "Login successful!"}), 200

@app.route('/balance', methods=['GET'])
def balance():
    username = request.args.get('username')
    if username in users:
        return jsonify({"balance": users[username]["balance"]}), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/transfer', methods=['POST'])
def transfer():
    sender = request.json.get('sender')
    receiver = request.json.get('receiver')
    amount = request.json.get('amount')

    if sender in users and receiver in users:
        if users[sender]["balance"] >= amount:
            users[sender]["balance"] -= amount
            users[receiver]["balance"] += amount
            save_users()
            return jsonify({"message": f"Transferred {amount} from {sender} to {receiver}"}), 200
        return jsonify({"error": "Insufficient funds"}), 400
    return jsonify({"error": "Invalid users"}), 404

def save_users():
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)

if __name__ == '__main__':
    app.run(debug=True)

