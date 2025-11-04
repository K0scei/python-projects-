# AirShare

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)
![Status](https://img.shields.io/badge/Status-Beta-yellow)

<h1>What is it?</h1>

AirShare is a web-app to file transmit without any hardware required.\
AirShare guarantees secrecy and privacy among sent files and sender/reciever.

---

<h1>Dependency List</h1>
Python 3.10 or higher,\
Flask web framework\
A modern web browser

---



<h1>Installation</h1>

Firstly, open your terminal and clone the repo:

```bash
git clone github.com/K0scei/python-projects-/
cd ./python-projects-
```

Then, <strong>optionally</strong> create a virtual enviroment (venv):

```bash
python -m venv venv
source venv/bin/activate    # macOS / Linux
venv\Scripts\activate       # Windows
```

Install the required dependencies with:

```bash
pip install -r requirements.txt
```

And finally, to run the file locally, simply use the command: 

```bash
flask --app ./server.py run
```

The output will give you the local link to the website opened. (e.g. 127.0.0.1:5000)

---

<h1>Folder Structure</h1>

AirShare/
│
├── server.py
├── requirements.txt
├── .gitignore
│
├── static/
│   ├── index.css
│   ├── home.css
│   ├── upload.css
│   ├── signup.css
│   └── login.css
│
├── templates/
│   ├── index.html
│   ├── home.html
│   ├── upload.html
│   ├── signup.html
│   └── login.html
│
├── data/
│   └── userdata.json (this is not feasable, but for beta versions this can make do.)
│
└── uploads/
