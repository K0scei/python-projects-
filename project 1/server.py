from flask import Flask, request, send_from_directory, render_template, redirect, url_for, flash, session
import socket
import os
import threading


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

@app.route("/login")
def login():
	return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
	error = None
	username = ''

	if request.method == 'POST':
		username = request.form.get('username', '').strip()

		if not username:
			error = "The username can not be empty!"
		elif len(username) < 4:
			error = "The username should be more than 4 characters!"
		elif len(username) > 12:
			error = "The username should be less than 12 characters!"

		if not error:
			session['username'] = username
			print(f"New user: {username}")
			return redirect(url_for('home'))
	return render_template("signup.html", error=error, username=username)

@app.route("/upload", methods=["GET", "POST"])
def upload():
	if request.method == "POST":
		if "file" not in request.files:
			flash("File Not Found!")
			return redirect(url_for("upload"))

		file = request.files["file"]
		if file.filename == "":
			flash("No File Selected!")
			return redirect(url_for("upload"))

		filename = file.filename
		file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
		flash(f"{filename} uploaded successfully.")
		return redirect(url_for("upload"))
	return render_template("upload.html")

# !!! ^use common whitespace (tab 4 spaces)

@app.route("/download/<filename>")
def download(filename):
	return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment = True)
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000, debug=True)

# özgür allahın varsa biraz whitespace bırak bu ne ya


@app.route("/home")
def home():
	username = session.get('username')
	return render_template("home.html")

@app.route("/logout")
def logout():
	session.pop("username")
	return redirect(url_for("login"))
