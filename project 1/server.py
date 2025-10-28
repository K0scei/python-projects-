from flask import Flask, request, send_from_directory, render_template, redirect, url_for, flash
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
	files = os.listdir(app.config["UPLOAD_FOLDER"])
	return render_template("upload.html", files = files)
@app.route("/login")
def login():
	return render_template("login.html")
@app.route("/signup")
def signup():
	return render_template("signup.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("Dosya bulunamadı!")
            return redirect(url_for("upload"))

        file = request.files["file"]
        if file.filename == "":
            flash("Hiç dosya seçilmedi!")
            return redirect(url_for("upload"))

        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        flash(f"{filename} başarıyla yüklendi.")
        return redirect(url_for("upload"))
    return render_template("upload.html")

@app.route("/donwload/<filename>")
def download(filename):
	return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment = True)
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000, debug=True)