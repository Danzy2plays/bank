from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = "users.json"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Admin login details

# Load or initialize users
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# Homepage
@app.route('/')
def home():
    return render_template("index.html")

# Register a new user
@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    username = data["username"]
    password = data["password"]
    
    if username in users:
        return jsonify({"error": "User already exists"}), 400
    
    # Create a new user account with initial balance 0
    users[username] = {"password": password, "balance": 0, "transactions": []}
    save()
    return jsonify({"message": "Account created"}), 200

# Login user
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]
    
    user = users.get(username)
    if user and user["password"] == password:
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid username or password"}), 401

# Transfer money
@app.route("/transfer", methods=["POST"])
def transfer():
    data = request.json
    sender = data["sender"]
    receiver = data["receiver"]
    amount = int(data["amount"])

    if sender in users and receiver in users:
        if users[sender]["balance"] >= amount:
            users[sender]["balance"] -= amount
            users[receiver]["balance"] += amount
            users[sender]["transactions"].append(f"-{amount} to {receiver}")
            users[receiver]["transactions"].append(f"+{amount} from {sender}")
            save()
            return jsonify({"sender_balance": users[sender]["balance"], "receiver_balance": users[receiver]["balance"]}), 200
        return jsonify({"error": "Insufficient funds"}), 400
    return jsonify({"error": "Invalid sender or receiver"}), 404

# Admin functionality: add or subtract money
@app.route("/admin", methods=["POST"])
def admin_actions():
    data = request.json
    admin_username = data["username"]
    admin_password = data["password"]
    target_user = data["target_user"]
    amount = int(data["amount"])
    
    if admin_username == ADMIN_USERNAME and admin_password == ADMIN_PASSWORD:
        if target_user in users:
            users[target_user]["balance"] += amount
            users[target_user]["transactions"].append(f"{'+' if amount >= 0 else '-'}{amount} by admin")
            save()
            return jsonify({"message": f"Admin updated {target_user}'s balance"}), 200
        return jsonify({"error": "Target user not found"}), 404
    return jsonify({"error": "Invalid admin credentials"}), 403

# Save users to file
def save():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

if __name__ == '__main__':
    app.run(debug=True)
