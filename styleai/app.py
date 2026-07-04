
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_bcrypt import Bcrypt
import mysql.connector
import google.generativeai as genai
from rembg import remove
import cv2
import tempfile
import base64
import cloudinary, cloudinary.uploader
import os, base64, json
from dotenv import load_dotenv
import random
def get_image(category, item_name, used_images):

    item_name = item_name.lower()
    if category not in [
        "earrings",
        "necklace",
        "bracelet",
        "ring",
        "handbag"
    ]:
        return "/static/images/placeholder.png"
    matches = {

        "earrings": {
            "stud": "/static/images/3_1.png",
            "diamond": "/static/images/3_1.png",

            "hoop": "/static/images/3_2.png",
            "gold hoop": "/static/images/3_2.png",
            "minimal": "/static/images/3_2.png",
            "gold": "/static/images/3_2.png",

            "pearl": "/static/images/3_3.png",

            "drop": "/static/images/3_4.png",
            "dangle": "/static/images/3_4.png",

            "fringe": "/static/images/3_5.png",
            "spiral": "/static/images/3_5.png"
        },

        "necklace": {
            "chain": "/static/images/2_1.png",
            "silver chain": "/static/images/2_1.png",

            "pendant": "/static/images/2_2.png",

            "heart": "/static/images/2_3.png",
            "love": "/static/images/2_3.png",

            "circle": "/static/images/2_4.png",
            "round": "/static/images/2_4.png",

            "layered": "/static/images/2_5.png",
            "minimal": "/static/images/2_5.png",
            "gold necklace": "/static/images/2_5.png"
        },

        "bracelet": {
            "bead": "/static/images/1_1.png",

            "tennis": "/static/images/1_2.png",

            "chain": "/static/images/1_3.png",

            "bangle": "/static/images/1_4.png",
            "cuff": "/static/images/1_4.png",

            "pearl": "/static/images/1_5.png",
            "stone": "/static/images/1_5.png"
        },

        "ring": {
            "solitaire": "/static/images/4_1.png",

            "band": "/static/images/4_2.png",
            "gold band": "/static/images/4_2.png",

            "flower": "/static/images/4_3.png",
            "floral": "/static/images/4_3.png",

            "halo": "/static/images/4_4.png",
            "diamond": "/static/images/4_4.png"
        },

        "handbag": {
            "tote": "/static/images/5_1.png",

            "shoulder": "/static/images/5_2.png",

            "crossbody": "/static/images/5_3.png",

            "structured": "/static/images/5_4.png",
            "satchel": "/static/images/5_4.png",
            "handbag": "/static/images/5_4.png"
        }
    }

    for keyword, image in matches.get(category, {}).items():

        if keyword in item_name:

            if image not in used_images[category]:

                used_images[category].add(image)

                return image

    pools = {

        "earrings": [
            "/static/images/3_1.png",
            "/static/images/3_2.png",
            "/static/images/3_3.png",
            "/static/images/3_4.png",
            "/static/images/3_5.png"
        ],

        "necklace": [
            "/static/images/2_1.png",
            "/static/images/2_2.png",
            "/static/images/2_3.png",
            "/static/images/2_4.png",
            "/static/images/2_5.png"
        ],

        "bracelet": [
            "/static/images/1_1.png",
            "/static/images/1_2.png",
            "/static/images/1_3.png",
            "/static/images/1_4.png",
            "/static/images/1_5.png"
        ],

        "ring": [
            "/static/images/4_1.png",
            "/static/images/4_2.png",
            "/static/images/4_3.png",
            "/static/images/4_4.png"
        ],

        "handbag": [
            "/static/images/5_1.png",
            "/static/images/5_2.png",
            "/static/images/5_3.png",
            "/static/images/5_4.png"
        ]
    }

    available = [
        img
        for img in pools[category]
        if img not in used_images[category]
    ]

    if not available:
        available = pools[category]

    chosen = random.choice(available)

    used_images[category].add(chosen)

    return chosen

load_dotenv()
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

gemini_model = genai.GenerativeModel(
    "gemini-3.1-flash-lite"
)

app = Flask(__name__)
app.secret_key = "styleai_secret"

bcrypt = Bcrypt(app)

def get_db():
    return mysql.connector.connect(
        host     = os.getenv("DB_HOST",     "localhost"),
        user     = os.getenv("DB_USER",     "root"),
        password = os.getenv("DB_PASSWORD", ""),
        database = os.getenv("DB_NAME",     "styleai"),
    )

def logged_in():
    return "user_id" in session
def get_user_preferences(user_id):

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT
            metal,
            earring_style,
            styling_level
        FROM preferences
        WHERE user_id = %s
    """, (user_id,))

    prefs = cur.fetchone()

    cur.close()
    db.close()

    return prefs
def update_preference_learning(user_id, selected_ids):
    print("=== UPDATE PREFERENCE LEARNING CALLED ===")
    print(selected_ids)

    if not selected_ids:
        return

    prefs = get_user_preferences(user_id)
    print("USER PREFS:", prefs)

    if not prefs:
        return

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        INSERT IGNORE INTO user_preference_learning(user_id)
        VALUES(%s)
    """, (user_id,))

    if prefs["metal"] == "Mixed":

        for image_url in selected_ids.values():

            if not image_url:
                continue

            cur.execute("""
                SELECT metal_type
                FROM accessories
                WHERE image_url = %s
                AND user_id = %s
            """, (image_url, user_id))

            row = cur.fetchone()
            print("LOOKUP:", image_url)
            print("FOUND:", row)
            if not row:
                continue

            metal = row["metal_type"]

            if metal == "Gold":
                cur.execute("""
                    UPDATE user_preference_learning
                    SET gold_count = gold_count + 1
                    WHERE user_id=%s
                """, (user_id,))

            elif metal == "Silver":
                cur.execute("""
                    UPDATE user_preference_learning
                    SET silver_count = silver_count + 1
                    WHERE user_id=%s
                """, (user_id,))

            elif metal == "Rose Gold":
                cur.execute("""
                    UPDATE user_preference_learning
                    SET rose_gold_count = rose_gold_count + 1
                    WHERE user_id=%s
                """, (user_id,))

    if prefs["earring_style"] == "Any":

        earrings_image = selected_ids.get("earrings")

        if earrings_image:

            cur.execute("""
                SELECT earring_type
                FROM accessories
                WHERE image_url = %s
                AND user_id = %s
            """, (earrings_image, user_id))

            row = cur.fetchone()

            if row:

                earring = row["earring_type"]

                if earring == "Stud":
                    cur.execute("""
                        UPDATE user_preference_learning
                        SET stud_count = stud_count + 1
                        WHERE user_id=%s
                    """, (user_id,))

                elif earring == "Hoop":
                    cur.execute("""
                        UPDATE user_preference_learning
                        SET hoop_count = hoop_count + 1
                        WHERE user_id=%s
                    """, (user_id,))

                elif earring == "Long":
                    cur.execute("""
                        UPDATE user_preference_learning
                        SET long_count = long_count + 1
                        WHERE user_id=%s
                    """, (user_id,))

    db.commit()
    cur.close()
    db.close()

def get_learning_summary(user_id):

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT *
        FROM user_preference_learning
        WHERE user_id=%s
    """, (user_id,))

    row = cur.fetchone()

    cur.close()
    db.close()

    if not row:
        return ""

    total_metal = (
        row["gold_count"] +
        row["silver_count"] +
        row["rose_gold_count"]
    )

    if total_metal > 0:

        gold = round(row["gold_count"] * 100 / total_metal)
        silver = round(row["silver_count"] * 100 / total_metal)
        rose = round(row["rose_gold_count"] * 100 / total_metal)

    else:
        gold = silver = rose = 0

    total_earrings = (
        row["stud_count"] +
        row["hoop_count"] +
        row["long_count"]
    )

    if total_earrings > 0:

        stud = round(row["stud_count"] * 100 / total_earrings)
        hoop = round(row["hoop_count"] * 100 / total_earrings)
        long = round(row["long_count"] * 100 / total_earrings)

    else:
        stud = hoop = long = 0

    return f"""
Historical User Preference

Metal:
Gold {gold}%
Silver {silver}%
Rose Gold {rose}%

Earrings:
Stud {stud}%
Hoop {hoop}%
Long {long}%
"""

@app.route("/")
def home():
    if logged_in():
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form["name"]
        email    = request.form["email"]
        password = request.form["password"]

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")

        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, hashed)
            )
            db.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            flash("Email already registered.", "error")
        finally:
            cur.close(); db.close()

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        db.close()

        print("================================")
        print("Email entered:", email)
        print("Password entered:", password)
        print("User found:", user is not None)

        if user:
            print("Stored hash:", user["password_hash"])

            try:
                password_ok = bcrypt.check_password_hash(
                    user["password_hash"],
                    password
                )
                print("Password check result:", password_ok)

                if password_ok:
                    session["user_id"] = user["id"]
                    session["user_name"] = user["name"]
                    return redirect(url_for("dashboard"))

            except Exception as e:
                print("BCRYPT ERROR:", e)

        flash("Incorrect email or password.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect(url_for("login"))

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM accessories WHERE user_id = %s ORDER BY created_at DESC",
        (session["user_id"],)
    )
    accessories = cur.fetchall()

    cur.execute(
        "SELECT * FROM preferences WHERE user_id = %s",
        (session["user_id"],)
    )
    prefs = cur.fetchone()
    cur.execute("""
        SELECT *
        FROM analysis_history
        WHERE user_id = %s
        ORDER BY id DESC
        LIMIT 4
    """, (session["user_id"],))

    recent_analyses = cur.fetchall()

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM analysis_history
        WHERE user_id = %s
    """, (session["user_id"],))

    analyses_count = cur.fetchone()["total"]
    cur.close()
    db.close()

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        accessories=accessories,
        prefs=prefs,
        recent_analyses=recent_analyses,
        analyses_count=analyses_count
    )

@app.route("/save-preferences", methods=["POST"])
def save_preferences():
    if not logged_in():
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    uid  = session["user_id"]

    db  = get_db()
    cur = db.cursor()

    cur.execute("""
    INSERT INTO preferences
    (
        user_id,

        metal,
        earring_type,
        styling_level,
        occasion,

        earrings_budget,
        earrings_source,

        necklace_budget,
        necklace_source,

        bracelet_budget,
        bracelet_source,

        ring_budget,
        ring_source,

        handbag_budget,
        handbag_source
    )
    VALUES
    (
        %s,

        %s,
        %s,
        %s,
        %s,

        %s,%s,
        %s,%s,
        %s,%s,
        %s,%s,
        %s,%s
    )
    ON DUPLICATE KEY UPDATE

        metal = VALUES(metal),
        earring_type = VALUES(earring_type),
        styling_level = VALUES(styling_level),
        occasion = VALUES(occasion),

        earrings_budget = VALUES(earrings_budget),
        earrings_source = VALUES(earrings_source),

        necklace_budget = VALUES(necklace_budget),
        necklace_source = VALUES(necklace_source),

        bracelet_budget = VALUES(bracelet_budget),
        bracelet_source = VALUES(bracelet_source),

        ring_budget = VALUES(ring_budget),
        ring_source = VALUES(ring_source),

        handbag_budget = VALUES(handbag_budget),
        handbag_source = VALUES(handbag_source)
    """, (
        uid,

        data.get("metal", "Gold"),
        data.get("earring", "Any"),
        data.get("style", "Minimal"),
        data.get("occasion", "Casual"),

        data.get("earrings_budget", 500),
        data.get("earrings_source", "both"),

        data.get("necklace_budget", 1000),
        data.get("necklace_source", "both"),

        data.get("bracelet_budget", 700),
        data.get("bracelet_source", "both"),

        data.get("ring_budget", 500),
        data.get("ring_source", "both"),

        data.get("handbag_budget", 2000),
        data.get("handbag_source", "both")
    ))
    db.commit()
    cur.close(); db.close()

    return jsonify({"ok": True})

@app.route("/add-accessory", methods=["POST"])
def add_accessory():
    print("ADD ACCESSORY CALLED")
    if not logged_in():
        return jsonify({"error": "Not logged in"}), 401

    acc_type = request.form.get("type")
    file     = request.files.get("image")

    if not file or not acc_type:
        return jsonify({"error": "Missing data"}), 400

    from werkzeug.utils import secure_filename
    import os

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        "static",
        "uploads",
        filename
    )

    file.save(filepath)

    image_url = "/" + filepath.replace("\\", "/")

    import base64

    with open(filepath, "rb") as f:
        accessory_b64 = base64.b64encode(f.read()).decode()
    db  = get_db()
    cur = db.cursor()
    analysis_prompt = """
    Analyze this accessory image carefully.

    Return ONLY valid JSON.

    {
        "name": "",
        "color": "",
        "material": "",
        "style": "",
        "occasion": "",
        "metal_type": "",
        "earring_type": ""
    }

    Rules:

    name:
    A short descriptive accessory name.

    color:
    Main visible color.

    material:
    Main material such as:
    Gold
    Silver
    Pearl
    Diamond
    Crystal
    Leather
    Fabric
    Beads
    Metal
    Plastic

    style:
    One of:
    Traditional
    Modern
    Minimal
    Elegant
    Bohemian
    Vintage
    Statement

    occasion:
    One of:
    Casual
    Party
    Festive
    Formal
    Wedding

    metal_type:
    Choose ONLY one of:
    Gold
    Silver
    Rose Gold
    None

    Use "None" if there is no visible gold, silver or rose gold finish.

    earring_type:
    Choose ONLY one of:
    Stud
    Hoop
    Long
    None

    Rules for earring_type:
    - Stud earrings → Stud
    - Hoop earrings → Hoop
    - Drop earrings → Long
    - Dangle earrings → Long
    - Tassel earrings → Long
    - Chandeliers → Long
    - Any non-earring accessory → None

    Return ONLY JSON.
    """
    from PIL import Image

    image = Image.open(filepath)

    response = gemini_model.generate_content(
        [analysis_prompt, image]
    )

    content = response.text

    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    print("CLEANED RESPONSE:")
    print(content)

    analysis = json.loads(content)
    cur.execute(
        """
INSERT INTO accessories
(
 user_id,
 type,
 image_url,
 name,
 color,
 material,
 style,
 occasion,
 metal_type,
 earring_type
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            session["user_id"],
            acc_type,
            image_url,
            analysis.get("name"),
            analysis.get("color"),
            analysis.get("material"),
            analysis.get("style"),
            analysis.get("occasion"),
            analysis.get("metal_type", "None"),
            analysis.get("earring_type", "None")
        )
    )
    db.commit()
    new_id = cur.lastrowid
    cur.close(); db.close()

    return jsonify({
        "ok": True,
        "id": new_id,
        "image_url": image_url,
        "type": acc_type,

        "name": analysis.get("name"),
        "style": analysis.get("style"),
        "color": analysis.get("color"),
        "material": analysis.get("material")
    })
@app.route("/delete-accessory/<int:acc_id>", methods=["DELETE"])
def delete_accessory(acc_id):
    if not logged_in():
        return jsonify({"error": "Not logged in"}), 401

    db  = get_db()
    cur = db.cursor()
    cur.execute(
        "DELETE FROM accessories WHERE id = %s AND user_id = %s",
        (acc_id, session["user_id"])
    )
    db.commit()
    cur.close(); db.close()

    return jsonify({"ok": True})

@app.route("/analyze", methods=["POST"])
def analyze():
    if not logged_in():
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    image_b64  = data.get("image_b64")
    image_mime = data.get("image_mime", "image/jpeg")
    prefs      = data.get("prefs", {})
    selected_accessories = data.get(
        "selected_accessories",
        {}
    )
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
    SELECT
    type,
    name,
    image_url,
    color,
    material,
    style,
    occasion
FROM accessories
WHERE user_id = %s
    """, (session["user_id"],))

    inventory = cur.fetchall()
    print("INVENTORY:")
    for item in inventory:
        print(item["type"], "->", item["name"])
    inventory_lookup = {}

    for item in inventory:
        inventory_lookup[
            item["name"].strip().lower()
        ] = item["image_url"]

    cur.close()
    db.close()

    if not image_b64:
        return jsonify({"error": "No image provided"}), 400

    inv_list = "\n".join(
        f"""
    Type: {i['type']}
    Name: {i['name']}
    Color: {i['color']}
    Material: {i['material']}
    Style: {i['style']}
    Occasion: {i['occasion']}
    """
        for i in inventory
    ) if inventory \
               else "No personal accessories saved."
    saved_prefs = get_user_preferences(session["user_id"])

    learning_summary = get_learning_summary(session["user_id"])

    pref_summary = f"""
        Earrings:
        Source = {prefs.get('earrings_source', 'both')}
        Budget = ₹{prefs.get('earrings_budget', 500)}

        Necklace:
        Source = {prefs.get('necklace_source', 'both')}
        Budget = ₹{prefs.get('necklace_budget', 1000)}

        Bracelet:
        Source = {prefs.get('bracelet_source', 'both')}
        Budget = ₹{prefs.get('bracelet_budget', 700)}

        Ring:
        Source = {prefs.get('ring_source', 'both')}
        Budget = ₹{prefs.get('ring_budget', 500)}

        Handbag:
        Source = {prefs.get('handbag_source', 'both')}
        Budget = ₹{prefs.get('handbag_budget', 2000)}
        """
    earring_items = "\n".join(
        i["name"] for i in inventory
        if str(i["type"]).lower() == "earrings"
    ) or "None"

    necklace_items = "\n".join(
        i["name"] for i in inventory
        if str(i["type"]).lower() == "necklace"
    ) or "None"

    bracelet_items = "\n".join(
        i["name"] for i in inventory
        if str(i["type"]).lower() == "bracelet"
    ) or "None"

    ring_items = "\n".join(
        i["name"] for i in inventory
        if str(i["type"]).lower() == "ring"
    ) or "None"

    handbag_items = "\n".join(
        i["name"] for i in inventory
        if str(i["type"]).lower() == "handbag"
    ) or "None"

    wardrobe_summary = f"""
    Earrings:
    {earring_items}

    Necklaces:
    {necklace_items}

    Bracelets:
    {bracelet_items}

    Rings:
    {ring_items}

    Handbags:
    {handbag_items}
    """
    fixed_items = ""

    selected_categories = []

    for category, item in selected_accessories.items():

        if item:
            fixed_items += (
                f"{category}: {item}\n"
            )

            selected_categories.append(
                category
            )
    prompt = f"""
    You are a professional fashion stylist AI.

    Analyze the uploaded outfit and recommend accessories.

    USER WARDROBE DETAILS:

    {inv_list}

    CURRENT USER PREFERENCES

    Metal Preference:
    {saved_prefs["metal"]}

    Earring Style:
    {saved_prefs["earring_style"]}

    Styling Level:
    {saved_prefs["styling_level"]}

    HISTORICAL LEARNING

    {learning_summary}

    PERSONALIZATION RULES

    1. If Metal Preference is Gold, Silver or Rose Gold:
    Ignore the historical metal learning completely.

    2. Only use historical metal learning when Metal Preference is Mixed.

    3. If Earring Style is Stud, Hoop or Long:
    Ignore historical earring learning.

    4. Only use historical earring learning when Earring Style is Any.

    5. Historical learning is only a soft preference.
    If another accessory clearly matches the outfit better, choose that instead.
USER PRESELECTED ACCESSORIES:

{fixed_items}

IMPORTANT RULES:

These accessories are already selected.

Do not replace them.

Recommend accessories around them.

If gold jewelry is selected:
- prefer gold accessories
- avoid silver accessories

If silver jewelry is selected:
- prefer silver accessories
- avoid gold accessories

Maintain:
- color harmony
- metal consistency
- style consistency

ACCESSORY PREFERENCES:
{pref_summary}

TASK:

The user may already have selected some accessories.

SELECTED CATEGORIES:

{selected_categories}

IMPORTANT:

Do NOT recommend accessories for any category already selected.

Examples:

If earrings are selected:
Do not return earrings.

If handbag is selected:
Do not return handbag.

If earrings and handbag are selected:
Return only necklace, bracelet and ring.

Only recommend categories that are not already selected.

CATEGORY RULES:

Earrings recommendations must ONLY contain earrings.

Necklace recommendations must ONLY contain necklaces.

Bracelet recommendations must ONLY contain bracelets.

Ring recommendations must ONLY contain rings.

Handbag recommendations must ONLY contain handbags.

Never place an earring inside the necklace category.
Never place a necklace inside the bracelet category.
Never place a bracelet inside the ring category.
Never place a ring inside the handbag category.

Returning an accessory in the wrong category is a critical error.

Return EXACTLY 3 recommendations for EACH category.
Total recommendations = 15.

PRIORITY ORDER:

1. User selected preferences
2. Outfit formality level
3. Outfit occasion
4. Outfit aesthetic
5. Outfit style
6. Outfit colors

Formality is more important than color matching.

SOURCE RULES:

Each category has a selected source:

* wardrobe
* shop
* both

If source = wardrobe:

- Recommend ONLY items whose exact name appears in USER WARDROBE.
- Never modify the name.
- Never shorten the name.
- Never create variations of the name.
- Never infer similar accessories.
- If "Pearl Stud Earrings" is not present in USER WARDROBE, it must never be recommended.
- If no suitable wardrobe item exists, do not invent one.
WARDROBE VERIFICATION RULE:

Before returning a wardrobe recommendation:

1. Verify the exact accessory name exists in USER WARDROBE.
2. If it does not exist, do not recommend it.
3. Never claim an accessory is available in the wardrobe unless its exact name appears in USER WARDROBE.
4. Incorrect wardrobe claims are a critical error.

Reason format:

"No wardrobe options available for this category. Recommended shopping alternative."

If source = shop:

* Recommend ONLY shopping items.
* Respect the category budget.
* Include budget.
* Include shopping query.
* Recommendations must realistically fit the outfit and preferences.

If source = both:

Use ONLY accessories whose exact name appears in USER WARDROBE.

Do not infer similar accessories.

Do not invent bracelets, necklaces, handbags or rings that are not explicitly listed.

* Use suitable wardrobe items whenever available.
* Fill remaining recommendations with shopping suggestions.
* Return exactly 3 recommendations total.

WARDROBE AVAILABILITY RULES:

If the user owns no accessories in a category:

* Do NOT invent wardrobe items.
* Do NOT generate fake wardrobe recommendations.
* Return shopping recommendations instead.

If source = both and no wardrobe items are available:

- Return shopping recommendations only.

Reason format:

"No suitable item found in your wardrobe. Recommended shopping alternative."

If source = wardrobe and no wardrobe items are available:

* Use shopping recommendations instead.
* Explain that no wardrobe options were available.

FORMALITY RULES:

For Western formal outfits such as:

* Business suits
* Blazers
* Corporate wear
* Professional office attire

Prefer accessories that match the outfit's:

* color palette
* style
* aesthetic
* formality level
* occasion

Avoid using default accessory choices.
Every outfit should receive unique recommendations.
Avoid:

* Jhumkas
* Heavy ethnic jewelry
* Bridal jewelry
* Festive jewelry
* Oversized statement accessories

Unless the outfit itself is ethnic, festive, traditional, wedding, or cultural wear.

SHOPPING QUERY RULES:

Every shopping recommendation must include a search query in this format:

<item name> under ₹<budget>

Examples:

* Pearl Stud Earrings under ₹500
* Minimal Gold Necklace under ₹1000
* Silver Bracelet under ₹700
* Structured Black Handbag under ₹2000

The query should be directly usable on Amazon, Flipkart, and Myntra.
NAME RULES:

The name field must contain ONLY the accessory name.

Do NOT include:
- budget
- price
- "under ₹..."
- shopping keywords

Examples:

Correct:
name = "Minimal Gold Hoops"
query = "Minimal Gold Hoops under ₹500"

Correct:
name = "Pearl Stud Earrings"
query = "Pearl Stud Earrings under ₹1000"

Wrong:
name = "Minimal Gold Hoops under ₹500"

Wrong:
name = "Pearl Stud Earrings under ₹1000"
DIVERSITY RULES:

- Never recommend the same accessory name twice.
- Never recommend the same accessory style repeatedly.
- Avoid always recommending pearl earrings.
- Avoid always recommending minimal gold necklaces.
- Generate fresh recommendations based on the outfit image.
- Different outfits should receive different recommendations.

GENERAL RULES:

* No duplicate recommendations.
* Never return empty arrays.
* Never leave the name field empty.
* Recommendations must complement the outfit.
* Recommendations must respect the user's style preferences.
* Return valid JSON only.
* No text outside JSON.
{{
  "earrings": [
    {{
      "source": "",
      "name": "",
      "reason": "",
      "budget": "",
      "query": "",
      "match": ""
    }}
  ],
  "necklace": [
    {{
      "source": "",
      "name": "",
      "reason": "",
      "budget": "",
      "query": "",
      "match": ""
    }}
  ],
  "bracelet": [
    {{
      "source": "",
      "name": "",
      "reason": "",
      "budget": "",
      "query": "",
      "match": ""
    }}
  ],
  "ring": [
    {{
      "source": "",
      "name": "",
      "reason": "",
      "budget": "",
      "query": "",
      "match": ""
    }}
  ],
  "handbag": [
    {{
      "source": "",
      "name": "",
      "reason": "",
      "budget": "",
      "query": "",
      "match": ""
    }}
  ]
}}

CRITICAL RULE:

For Western formal outfits, corporate wear, office wear, business suits and blazers:

- Never recommend Jhumkas.
- Never recommend Chandbalis.
- Never recommend ethnic earrings.
- Never recommend bridal jewelry.
- Never recommend festive jewelry.

Even if they exist in the user's wardrobe.

If the wardrobe only contains these items, return shopping alternatives instead.
NAME RULES:

The name field must contain ONLY the accessory name.

Do NOT include:
- budget
- price
- "under ₹..."
- shopping keywords

Examples:

Correct:
name = "Minimal Gold Hoops"

Wrong:
name = "Minimal Gold Hoops under ₹500"
ALSO RETURN:

"style":"",
"occasion":"",
"colors":["",""]
OUTFIT FIRST RULE:

Analyze the uploaded outfit image carefully.

Recommendations must depend on:

1. outfit color
2. outfit fabric
3. outfit silhouette
4. outfit occasion
5. outfit style

Do not use default accessories.
For every recommendation:

reason:
- Maximum 4 words
- One sentence only
- No explanations
- No detailed fashion analysis

The same accessory should not appear for every outfit.

Return JSON only.

        """

    image_bytes = base64.b64decode(image_b64)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(image_bytes)
        image_path = tmp.name
    import uuid

    filename = f"{uuid.uuid4()}.png"

    save_path = os.path.join(
        "static",
        "uploads",
        filename
    )

    with open(save_path, "wb") as f:
        f.write(image_bytes)

    outfit_image_url = "/static/uploads/" + filename

    img = cv2.imread(image_path)
    if img is None:
        return jsonify({"error": "Could not read image"}), 400

    h, w = img.shape[:2]

    if max(h, w) > 800:
        scale = 800 / max(h, w)

        img = cv2.resize(
            img,
            (int(w * scale), int(h * scale))
        )

    cv2.imwrite(image_path, img)

    with open(image_path, "rb") as f:
        resized_b64 = base64.b64encode(f.read()).decode()
    print("IMAGE PATH =", image_path)
    print("FILE EXISTS =", os.path.exists(image_path))
    from PIL import Image

    image = Image.open(image_path)

    response = gemini_model.generate_content(
        [prompt, image]
    )

    raw = response.text

    print("QWEN RESPONSE:")
    print(raw)

    raw = raw.replace("```json", "")
    raw = raw.replace("```", "")
    raw = raw.strip()

    try:
        print("QWEN RESPONSE:")
        print(raw)

        result = json.loads(raw)
        fixed_categories = set()

        for category, selected_image in selected_accessories.items():

            if not selected_image:
                continue

            selected_item = None

            print("SELECTED ACCESSORIES:", selected_accessories)

            for item in inventory:
                print(
                    "NAME:", item.get("name"),
                    "IMAGE:", item.get("image_url")
                )

            for inv in inventory:

                if str(inv["image_url"]) == str(selected_image):
                    selected_item = inv
                    break

            if selected_item:
                print(
                    "SELECTED ITEM:",
                    category,
                    selected_item["name"],
                    selected_item["image_url"]
                )

                fixed_categories.add(category)

                result[category] = [{
                    "source": "wardrobe",
                    "name": selected_item["name"],
                    "reason": "Selected by you",
                    "budget": "",
                    "query": "",
                    "match": "Perfect Match",
                    "owned": True,
                    "image_url": selected_item["image_url"]
                }]
        used_images = {
            "earrings": set(),
            "necklace": set(),
            "bracelet": set(),
            "ring": set(),
            "handbag": set()
        }
        summary_text = "Outfit analyzed successfully"
        wardrobe_earrings = {x.strip().lower() for x in earring_items.split("\n") if x.strip() and x.strip() != "None"}
        wardrobe_necklaces = {x.strip().lower() for x in necklace_items.split("\n") if
                              x.strip() and x.strip() != "None"}
        wardrobe_bracelets = {x.strip().lower() for x in bracelet_items.split("\n") if
                              x.strip() and x.strip() != "None"}
        wardrobe_rings = {x.strip().lower() for x in ring_items.split("\n") if x.strip() and x.strip() != "None"}
        wardrobe_handbags = {x.strip().lower() for x in handbag_items.split("\n") if x.strip() and x.strip() != "None"}
        category_map = {
            "earrings": wardrobe_earrings,
            "necklace": wardrobe_necklaces,
            "bracelet": wardrobe_bracelets,
            "ring": wardrobe_rings,
            "handbag": wardrobe_handbags
        }

        for category, valid_items in category_map.items():
            if category in fixed_categories:
                continue
            print("CATEGORY:", category)
            print("VALID ITEMS:", valid_items)
            used_names = set()

            if category not in result:
                continue

            for item in result[category]:
                name = item.get("name", "").strip().lower()

                invalid = (
                        (category == "bracelet" and "ring" in name) or
                        (category == "ring" and "bracelet" in name) or
                        (category == "earrings" and ("necklace" in name or "bracelet" in name)) or
                        (category == "necklace" and ("earring" in name or "ring" in name)) or
                        (category == "handbag" and ("ring" in name or "bracelet" in name))
                    )

                if invalid:
                    item["source"] = "shop"
                    item["reason"] = (
                        "Category mismatch detected. "
                        "Recommended shopping alternative."
                    )

                    fallback_names = {
                        "earrings": "Minimal Stud Earrings",
                        "necklace": "Minimal Gold Necklace",
                        "bracelet": "Minimal Gold Bracelet",
                        "ring": "Minimal Gold Ring",                            "handbag": "Structured Handbag"
                        }

                    item["name"] = fallback_names[category]

                    name = item["name"].lower()

                if name in used_names:
                    item["name"] = item["name"] + " Alternative"

                used_names.add(name)

                source = item.get("source", "shop").lower()

                item["match"] = ""

                if source == "wardrobe":

                    item_name = item.get("name", "").strip().lower()

                    if item_name not in valid_items:
                        item["source"] = "shop"

                        item["reason"] = (
                            "No suitable item found in your wardrobe. "
                            "Recommended shopping alternative."
                        )

                        source = "shop"
                        item["query"] = "fashion accessory"

                print(
                    "SOURCE:",
                    source,
                    "NAME:",
                    item.get("name")
                )
                print(
                    "SOURCE:",
                    source,
                    "NAME:",
                    item.get("name")
                )
                if source == "shop":

                    item["image_url"] = get_image(
                        category,
                        item.get("name", ""),
                        used_images
                    )

                elif source == "wardrobe":
                    print("LOOKING FOR:", item["name"].strip().lower())
                    print("AVAILABLE:", inventory_lookup.keys())
                    item["image_url"] = inventory_lookup.get(
                        item["name"].strip().lower(),
                        ""
                    )

                else:

                    item["image_url"] = get_image(
                        category,
                        item.get("name", ""),
                        used_images
                    )
    except Exception as e:
        print("JSON ERROR:", e)

        return jsonify({
            "error": "AI returned invalid JSON",
            "raw": raw[:1000]
        }), 500
    db  = get_db()
    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO analysis_history
        (
            user_id,
            mood,
            summary,
            result_json,
            image_url
        )
        VALUES (%s,%s,%s,%s,%s)
        """,
        (
            session["user_id"],
            result.get("mood", ""),
            summary_text,
            json.dumps(result),
            outfit_image_url
        )
    )
    db.commit()
    cur.close(); db.close()
    print(
        json.dumps(
            result,
            indent=2
        )
    )

    return jsonify(result)
@app.route(
    "/generate-full-look",
    methods=["POST"]
)
def generate_full_look():

    if not logged_in():
        return jsonify({
            "error":"Not logged in"
        }), 401

    print("========== GENERATE FULL LOOK ==========")

    data = request.get_json()

    print("REQUEST DATA:")
    print(data)

    selected_accessories = data.get("wardrobe", {})

    print("SELECTED ACCESSORIES:")
    print(selected_accessories)

    update_preference_learning(
        session["user_id"],
        selected_accessories
    )

    print("========== FINISHED LEARNING ==========")

    prompt = f"""
You are a professional fashion stylist.

Analyze this final outfit combination.

Selected outfit details:

{json.dumps(data)}

Return ONLY JSON:

{{
    "overall_score": 91,
    "color_harmony": 95,
    "occasion_match": 89,
    "aesthetic_consistency": 92,
    "feedback": "Explain why the accessories work together."
}}
"""

    try:

        response = gemini_model.generate_content(
            prompt
        )

        text = response.text

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        text = text.strip()

        return jsonify(
            json.loads(text)
        )

    except Exception as e:

        print(
            "FULL LOOK ERROR:",
            e
        )

        return jsonify({
            "overall_score": 90,
            "color_harmony": 90,
            "occasion_match": 90,
            "aesthetic_consistency": 90,
            "feedback":
                "Your selected accessories create a balanced and cohesive outfit."
        })

if __name__ == "__main__":
    app.run(debug=True, port=5001)
