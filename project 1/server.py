from flask import Flask, request, send_from_directory, render_template, redirect, url_for, flash, session
import socket
import os
import threading
import json

""""
HEADER = 64

PORT = 5050
SERVER = "1.1.1.1"
ADDR = (SERVER.PORT)
FORMAT = "utf-8"
DISCONNECT_MSG ="!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

connected = True

def send(msg):
	message = msg.encode(FORMAT)
	msg_length = len(message)
	send_length = str(msg_length).encode(FORMAT)
	send_length += b''*(HEADER-len(send_length))
	client.send(send_length)
	client.send(message)

send("hello server")

while connected:
	message = input("Whats your massage to the server")
	if message =="disconnect":
		send(DISCONNECT_MSG)
		connected = False
		quit()
	else:
		send(message)
"""
app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok = True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def server():
	return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
	error = None

	if request.method == 'POST':
		from werkzeug.security import check_password_hash
		provided_username = request.form.get('username', '').strip()
		provided_password = request.form.get('password', '').strip()

		with open('./data/userdata.json', "r", encoding='utf-8') as f:
			data = json.load(f)
			user = data["users"].get(provided_username)
		if not user:
			error = "No username given! Please check your inputs!"
		else:
			hashed_password = user["password"]
		if not provided_password:
			error = "No password given! Please check your inputs!"
		elif not user:
			error = "No user found with this username. Did you mean to sign in?"
		elif not check_password_hash(hashed_password, provided_password):
			error = "The password is wrong, please try again!"

		if not error:
			print(f"User {provided_password} has logged in!")
			session['username'] = provided_username
			return redirect(url_for('home'))

	return render_template("login.html", error=error)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
	error = None
	username = ''

	if request.method == 'POST':
		username = request.form.get('username', '').strip()
		password = request.form.get('password', '').strip()

		if not username:
			error = "The username can not be empty!"
		elif len(username) < 4:
			error = "The username should be more than 4 characters!"

		if not error:
			from werkzeug.security import generate_password_hash
			hashed_password = generate_password_hash(password=password)
			session['username'] = username
			os.makedirs('./data', exist_ok=True)
			#not ethical, but who cares at this point
			#write data to the file /data/userdata.json
			try:
				with open('./data/userdata.json', "r", encoding='utf-8') as f:
					data = json.load(f)
			except (json.JSONDecodeError, FileNotFoundError):
					data = {"users":{}}

			if username not in data["users"]:
				data["users"][username] = {"password": hashed_password,"uploadids": [], 'downloadids':[]}

			with open('./data/userdata.json', "w", encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=4)
				print(f"New user: {username} dumped to the file successfully!!")

			return redirect(url_for('home'))
	return render_template("signup.html", error=error, username=username)


@app.route("/upload")
def upload():
	return render_template("upload.html")


@app.route("/download/<filename>")
def download(filename):
	return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment = True)

# özgür allahın varsa biraz whitespace bırak bu ne ya


@app.route("/home")
def home():
	username = session.get('username')
	return render_template("home.html", username=username)

@app.route("/logout")
def logout():
	session.pop("username")
	return redirect(url_for("login"))

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000, debug=True)

# !!! ^use common whitespace (tab / 4 spaces)