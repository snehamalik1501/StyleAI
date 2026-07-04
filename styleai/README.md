# StyleAI — Setup Guide

Follow these steps exactly, in order.

---

## Step 1 — Install Python tools

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```
pip install flask flask-bcrypt mysql-connector-python anthropic cloudinary python-dotenv
```

Or using the requirements file:
```
pip install -r requirements.txt
```

---

## Step 2 — Set up MySQL database

You already know MySQL from class 12. Open MySQL and run the setup file:

```
mysql -u root -p
```

Then inside MySQL:
```sql
source setup_db.sql
```

This creates all the tables automatically.

---

## Step 3 — Get your API keys

You need 3 free accounts:

### A. Claude API (Anthropic)
1. Go to https://console.anthropic.com
2. Sign up → go to "API Keys" → create a key
3. Copy it (starts with sk-ant-...)

### B. Cloudinary (free image hosting)
1. Go to https://cloudinary.com → Sign up free
2. Dashboard shows your Cloud Name, API Key, API Secret

---

## Step 4 — Create your .env file

Copy the example file:
```
cp .env.example .env
```

Open .env and fill in your real values:
```
SECRET_KEY=any-long-random-string
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=styleai
ANTHROPIC_API_KEY=sk-ant-your-key-here
CLOUDINARY_CLOUD_NAME=your-name
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
```

---

## Step 5 — Run the app

```
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

Open your browser and go to: **http://localhost:5000**

---

## Project Structure

```
styleai/
├── app.py              ← main Flask app (all routes)
├── setup_db.sql        ← run once to create MySQL tables
├── requirements.txt    ← Python packages needed
├── .env.example        ← copy to .env and fill in secrets
├── .env                ← your real secrets (never commit to GitHub!)
├── .gitignore          ← tells Git to ignore .env and uploads
├── templates/
│   ├── landing.html    ← home page (not logged in)
│   ├── login.html      ← login form
│   ├── register.html   ← register form
│   └── dashboard.html  ← main app page
└── static/
    ├── css/style.css   ← all styling
    └── js/dashboard.js ← all JavaScript
```

---

## How the code flows

1. User visits `/` → `home()` in app.py → shows landing.html
2. User registers → `register()` → saves to MySQL users table
3. User logs in → `login()` → sets session → redirects to dashboard
4. Dashboard loads → `dashboard()` → fetches accessories + prefs from MySQL → passes to dashboard.html via Jinja2
5. User uploads outfit + clicks Analyze → JS calls `/analyze` → Flask calls Claude API → returns JSON → JS renders results

---

## Common errors

**mysql.connector.errors.ProgrammingError: Table doesn't exist**
→ You haven't run setup_db.sql yet. Do Step 2.

**anthropic.AuthenticationError**
→ Your ANTHROPIC_API_KEY in .env is wrong or missing.

**ModuleNotFoundError: No module named 'flask'**
→ You haven't installed the packages yet. Do Step 1.
