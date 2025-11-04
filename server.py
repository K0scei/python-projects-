from flask import Flask, request, send_from_directory, render_template, redirect, url_for, flash, session, jsonify, abort
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

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
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

		try:
			with open('./data/userdata.json', "r", encoding='utf-8') as f:
				data = json.load(f)
		except (json.JSONDecodeError, FileNotFoundError):
			data = {}

		users_data = data.get("users", {})
		user = users_data.get(provided_username)

		if not provided_username:
			error = "No username given! Please check your inputs!"
		elif not provided_password:
			error = "No password given! Please check your inputs!"
		elif not user:
			error = "USER_NOT_FOUND"
		else:
			hashed_password = user.get("password")
			if not hashed_password:
				error = "User data corrupted. Please contact support!"
			elif not check_password_hash(hashed_password, provided_password):
				error = "The password is wrong, please try again!"

		if not error:
			print(f"User {provided_username} has logged in!")
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

		try:
			with open('./data/userdata.json', "r", encoding='utf-8') as f:
				data = json.load(f)
		except (json.JSONDecodeError, FileNotFoundError):
			data = {}

		users_data = data.get("users", {})

		if username in users_data:
			error = "USER_EXISTS_ERROR"
		elif not username:
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
				data["users"][username] = {"password": hashed_password, "uploadnames":[], "uploadids": [], "downloadnames": [], 'downloadids':[]}

			with open('./data/userdata.json', "w", encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=4)
				print(f"New user: {username} dumped to the file successfully!!")

			return redirect(url_for('home'))
	return render_template("signup.html", error=error, username=username)


@app.route("/upload", methods = ["GET", "POST"])
def upload():
	user = session.get("username") #is username
	if not user:
		flash("You must be logged in!")
		return redirect(url_for('login'))

	from werkzeug.utils import secure_filename
	from uuid import uuid4

	try:
		with open('./data/userdata.json', "r", encoding='utf-8') as f:
			data = json.load(f)
	except(FileNotFoundError, json.JSONDecodeError):
		data = {"users": {}}

	user_data = data["users"][user]

	if request.method == "POST":
		file = request.files.get("file")
		sendto = request.form.get("text")

		if not file or file.filename == "":
			flash("No file selected!")
			return render_template("upload.html", file=None, sendto=None, files=user_data["uploadnames"])
		else:
			filename = secure_filename(file.filename)
		if not sendto or sendto == '':
			flash("Please specify who to send!")
			return render_template("upload.html", file=filename, sendto=None, files=user_data["uploadnames"])

		elif not sendto in data["users"]:
			flash("The person you are trying to send does NOT have a account!")
			return render_template("upload.html", file=None, sendto=None, files=user_data["uploadnames"])

		sendto_data = data["users"].get(sendto)

		file_uuid = str(uuid4())

		sendto_data["downloadnames"].append({"name": filename, "sentfrom": session["username"], "uuid": file_uuid})

		user_data["uploadnames"].append({"name": filename, "sendto": sendto, "uuid": file_uuid})

		with open('./data/userdata.json', "w", encoding='utf-8') as f:
			json.dump(data, f, indent=4)

		save_path = os.path.join(app.config['UPLOAD_FOLDER'], file_uuid)

		file.save(save_path)

		return redirect(url_for('upload'))

	return render_template("upload.html", file=None, sendto=None, files=user_data["uploadnames"])


@app.route("/download/<path:file_uuid>") # ! path tamamen test materyali silinebilir
def download(file_uuid):

	with open('./data/userdata.json', 'r', encoding='utf-8') as f:
		data = json.load(f)
	user = session['username']

	user_downloadables = data["users"][user]["downloadnames"]

	file_record = next((f for f in user_downloadables if f.get("uuid") == file_uuid), None)

	if not file_record:
		abort(403, description='You do not have the permission to download this file.')

	original_filename = file_record.get('name', 'unknown_file')

	disk_filename = file_uuid

	return send_from_directory(
		app.config['UPLOAD_FOLDER'],
		disk_filename,
		as_attachment = True,
		download_name = original_filename
	)

# özgür allahın varsa biraz whitespace bırak bu ne ya
@app.route("/delete-file/<filename>", methods=["DELETE"])
def delete_file(filename):
	current_user = session.get("username")
	if not current_user:
		return jsonify({"success": False, "message": "Not logged in."}), 401

	data_path = "./data/userdata.json"

	try:
		with open(data_path, "r", encoding="utf-8") as f:
			data = json.load(f)

		user_data = data.get("users", {}).get(current_user)
		if not user_data:
			return (
				jsonify({"success": False, "message": "No user data."}),
				404,
			)

		incoming_files = user_data.get("downloadnames", [])

		file_record_to_delete = next(
			(f for f in incoming_files if f.get("name") == filename), None
		)

		if not file_record_to_delete:
			return (
					jsonify(
					{
						"success": False,
						"message": "The file was not sent for you.",
					}
					),
				404,
			)

		file_uuid = file_record_to_delete.get("uuid")
		sender_username = file_record_to_delete.get(
			"sentfrom"
		)
		file_name = file_record_to_delete.get("name")

		data["users"][current_user]["downloadnames"] = [
			f for f in incoming_files if f.get("uuid") != file_uuid
		]

		if sender_username and sender_username in data["users"]:
			sender_files = data["users"][sender_username].get("uploadnames", [])

			data["users"][sender_username]["uploadnames"] = [
				f for f in sender_files if f.get("uuid") != file_uuid
			]

		file_to_delete_disk_name = file_uuid
		disk_path = os.path.join(app.config["UPLOAD_FOLDER"], file_to_delete_disk_name)

		if os.path.exists(disk_path):
			os.remove(disk_path)
			print(f"Removed from disk: {disk_path}")
		else:
			print(
				f"THE FILE WAS NOT FOUND IN THE PATH: {disk_path}"
			)

		with open(data_path, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=4)

		return jsonify(
			{
				"success": True,
				"message": f"'{file_name}' removed successfully.",
			}
		)

	except Exception as e:
		print(f"Critical Error: {e}")
		return jsonify({"success": False, "message": f"Server Error: {e}"}), 500


@app.route("/home")
def home():
	username = session.get('username')

	with open('./data/userdata.json', "r", encoding='utf-8') as f:
		data = json.load(f)

	downloadables = data["users"][username]["downloadnames"]

	return render_template("home.html", username=username, downloadables=downloadables)

@app.route("/logout")
def logout():
	session.pop("username")
	return redirect(url_for("login"))

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000, debug=True)

# !!! ^use common whitespace (tab / 4 spaces)