from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Secret key for session management
DATA_FILE = "users.json"
ADMIN_USERNAME = "admin"  # Admin account name

# Load or initialize users
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# Serve the login/register page
@app.route('/')
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    if username in users:
        return jsonify({"error": "User already exists"}), 400
    users[username] = {"password": password, "balance": 0, "transactions": []}
    save()
    return redirect(url_for("login"))

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = users.get(username)
    if user and user["password"] == password:
        session["username"] = username
        return redirect(url_for("dashboard"))
    return jsonify({"error": "Invalid username or password"}), 400

@app.route("/dashboard")
def dashboard():
    username = session.get("username")
    if not username:
        return redirect(url_for("index"))
    user = users[username]
    return render_template("dashboard.html", user=user)

@app.route("/transfer", methods=["POST"])
def transfer():
    sender = session.get("username")
    if not sender:
        return redirect(url_for("index"))

    data = request.json
    receiver = data["receiver"]
    amount = int(data["amount"])

    if sender not in users or receiver not in users:
        return jsonify({"error": "User not found"}), 404

    if users[sender]["balance"] < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    users[sender]["balance"] -= amount
    users[receiver]["balance"] += amount
    users[sender]["transactions"].append(f"-{amount} to {receiver}")
    users[receiver]["transactions"].append(f"+{amount} from {sender}")
    save()

    return jsonify({"message": "Transfer successful"}), 200

@app.route("/add_money", methods=["POST"])
def add_money():
    admin_username = "admin"  # Hard-coded admin account
    data = request.json
    if session.get("username") != admin_username:
        return jsonify({"error": "Only admin can add money"}), 403

    target_user = data["target_user"]
    amount = int(data["amount"])

    if target_user not in users:
        return jsonify({"error": "User not found"}), 404

    users[target_user]["balance"] += amount
    users[target_user]["transactions"].append(f"+{amount} by admin")
    save()

    return jsonify({"message": "Money added successfully"}), 200

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

if __name__ == "__main__":
    app.run(debug=True)

