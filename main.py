from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import sqlite3

app = Flask(__name__)
app.secret_key ="Bekken01"
sensor_data = []

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
	def __init__(self, id_, username, password):
		self.id = id_
		self.username = username
		self.password = password

def get_user_by_username(username):
	conn = sqlite3.connect("users.db")
	cursor = conn.cursor()
	cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
	row = cursor.fetchone()
	conn.close()
	return User(*row) if row else None

@login_manager.user_loader
def load_user(user_id):
	conn = sqlite3.connect("users.db")
	cursor = conn.cursor()
	cursor.execute("SELECT id, username, password FROM users WHERE id = ?", (user_id,))
	row = cursor.fetchone()
	conn.close()
	return User(*row) if row else None

@app.route('/api/data', methods=['POST'])
def receive_data():
	data = request.get_json()
	sensor_data.append(data)
	print(data)
	return jsonify({'status': 'ok'})

@app.route('/')
@login_required
def dashboard():
    latest = sensor_data[-1] if sensor_data else {}
    return render_template('dashboard.html', data = latest)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = get_user_by_username(username)
		if user and user.password == password:
			login_user(user)
			return redirect(url_for('dashboard'))
		flash("Invalid credentials.")
	return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
