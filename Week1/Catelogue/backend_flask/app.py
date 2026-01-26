import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime, timedelta
from flask import send_from_directory
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename


load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB upload limit

# Mail config
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

mail = Mail(app)


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# Vendor Signup
# -----------------------------
@app.post("/api/vendor/signup")
def vendor_signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    whatsapp = data.get("whatsapp")

    if not all([name, email, password, whatsapp]):
        return jsonify({"error": "name,email,password,whatsapp required"}), 400

    pw_hash = generate_password_hash(password)

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO vendors (name,email,password,whatsapp)
            VALUES (%s,%s,%s,%s)
            RETURNING id
            """,
            (name, email, pw_hash, whatsapp),
        )
        vendor_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"message": "signup success", "vendor_id": vendor_id})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


# -----------------------------
# Vendor Login
# -----------------------------
@app.post("/api/vendor/login")
def vendor_login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id,password,name,whatsapp,is_verified FROM vendors WHERE email=%s", (email,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return jsonify({"error": "invalid email"}), 401

    vendor_id, pw_hash, name, whatsapp ,is_verified = row

    if not check_password_hash(pw_hash, password):
        return jsonify({"error": "invalid password"}), 401
    
    if not is_verified:
        return jsonify({"error": "Vendor not verified. Complete OTP registration."}), 403

    return jsonify({"message": "login success", "vendor_id": vendor_id, "name": name, "whatsapp": whatsapp})


# -----------------------------
# Add Item
# -----------------------------
@app.post("/api/items")
def add_item():
    data = request.json
    vendor_id = data.get("vendor_id")
    title = data.get("title")
    price = data.get("price")
    in_stock = data.get("in_stock", True)
    image_url = data.get("image_url")

    if not all([vendor_id, title, price]):
        return jsonify({"error": "vendor_id,title,price required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    image_path = data.get("image_path")  # NEW

    cur.execute(
    """
    INSERT INTO items (vendor_id,title,price,in_stock,image_url,image_path)
    VALUES (%s,%s,%s,%s,%s,%s)
    RETURNING id
    """,
    (vendor_id, title, price, in_stock, image_url, image_path),
)

    item_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "item added", "item_id": item_id})


# -----------------------------
# Public Catalog (Customer view)
# -----------------------------
@app.get("/api/catalog/<int:vendor_id>")
def vendor_catalog(vendor_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT name, logo_url, logo_path, about, whatsapp FROM vendors WHERE id=%s", (vendor_id,))
    vendor = cur.fetchone()

    if not vendor:
        cur.close()
        conn.close()
        return jsonify({"error": "vendor not found"}), 404

    name, logo_url, logo_path, about, whatsapp = vendor

    cur.execute(
        """
        SELECT id, title, price, in_stock, image_url, image_path
        FROM items
        WHERE vendor_id=%s
        ORDER BY created_at DESC
        """,
        (vendor_id,),
    )
    items = cur.fetchall()

    cur.close()
    conn.close()

    item_list = []
    for r in items:
        item_list.append(
           {"id": r[0], "title": r[1], "price": float(r[2]), "in_stock": r[3], "image_url": r[4], "image_path": r[5]}
        )

    if logo_path:
        logo_url = f"http://127.0.0.1:5000/uploads/{logo_path}"

    return jsonify(
        {
            "vendor": {"id": vendor_id, "name": name, "logo_url": logo_url, "about": about, "whatsapp": whatsapp},
            "items": item_list,
        }
    )

@app.get("/api/vendors")
def list_vendors():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, logo_url, logo_path, about
        FROM vendors
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    vendors = []
    for r in rows:
        vendor_id = r[0]
        name = r[1]
        logo_url = r[2]
        logo_path = r[3]
        about = r[4]

        # ✅ if uploaded logo exists, use it
        if logo_path:
            logo_url = f"http://127.0.0.1:5000/uploads/{logo_path}"

        vendors.append({
            "id": vendor_id,
            "name": name,
            "logo_url": logo_url,
            "logo_path": logo_path,
            "about": about
        })

    return jsonify({"vendors": vendors})


@app.get("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.post("/api/vendor/request-otp")
def request_otp():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "email required"}), 400

    otp = str(random.randint(100000, 999999))

    otp_hash = generate_password_hash(otp)
    expires_at = datetime.now() + timedelta(minutes=5)

    conn = get_conn()
    cur = conn.cursor()

    # store latest OTP
    cur.execute(
        """
        INSERT INTO vendor_otps (email, otp_hash, expires_at)
        VALUES (%s, %s, %s)
        """,
        (email, otp_hash, expires_at),
    )
    conn.commit()
    cur.close()
    conn.close()

    try:
        msg = Message(
            subject="Your Vendor OTP Verification Code",
            recipients=[email],
            body=f"Your OTP is: {otp}\nIt will expire in 5 minutes."
        )
        mail.send(msg)
    except Exception as e:
        return jsonify({"error": f"Email send failed: {str(e)}"}), 500

    return jsonify({"message": "OTP sent to email"})

@app.post("/api/vendor/register")
def vendor_register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    whatsapp = data.get("whatsapp")
    otp = data.get("otp")
    about = data.get("about")
    logo_url = data.get("logo_url")  # optional now; we later upload

    if not all([name, email, password, whatsapp, otp]):
        return jsonify({"error": "name,email,password,whatsapp,otp required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    # Find latest OTP
    cur.execute(
        """
        SELECT otp_hash, expires_at
        FROM vendor_otps
        WHERE email=%s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (email,),
    )
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return jsonify({"error": "OTP not found. Request OTP again."}), 400

    otp_hash, expires_at = row
    if datetime.now() > expires_at:
        cur.close()
        conn.close()
        return jsonify({"error": "OTP expired. Request new OTP."}), 400

    if not check_password_hash(otp_hash, otp):
        cur.close()
        conn.close()
        return jsonify({"error": "Invalid OTP"}), 400

    pw_hash = generate_password_hash(password)

    try:
        cur.execute(
            """
            INSERT INTO vendors (name,email,password,whatsapp,about,logo_url,is_verified)
            VALUES (%s,%s,%s,%s,%s,%s,true)
            RETURNING id
            """,
            (name, email, pw_hash, whatsapp, about, logo_url),
        )
        vendor_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"message": "vendor registered", "vendor_id": vendor_id})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.post("/api/items/upload-image")
def upload_item_image():
    if "file" not in request.files:
        return jsonify({"error": "file missing"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "empty filename"}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{int(datetime.now().timestamp())}_{filename}"

    save_dir = os.path.join(app.config["UPLOAD_FOLDER"], "items")
    os.makedirs(save_dir, exist_ok=True)

    filepath = os.path.join(save_dir, unique_name)
    file.save(filepath)

    # return relative path usable for /uploads
    relative_path = f"items/{unique_name}"
    public_url = f"http://127.0.0.1:5000/uploads/{relative_path}"

    return jsonify({"message": "uploaded", "image_path": relative_path, "image_url": public_url})


@app.put("/api/vendor/profile/<int:vendor_id>")
def update_vendor_profile(vendor_id):
    data = request.json
    about = data.get("about")
    logo_url = data.get("logo_url")

    conn = get_conn()
    cur = conn.cursor()

    logo_path = data.get("logo_path")

    cur.execute("""
    UPDATE vendors
    SET about=%s, logo_url=%s, logo_path=%s, updated_at=NOW()
    WHERE id=%s
""", (about, logo_url, logo_path, vendor_id))

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "profile updated"})

@app.delete("/api/items/<int:item_id>")
def delete_item(item_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id=%s", (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "item deleted"})

@app.put("/api/items/<int:item_id>")
def update_item(item_id):
    data = request.json
    title = data.get("title")
    price = data.get("price")
    in_stock = data.get("in_stock")
    image_url = data.get("image_url")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE items
        SET title=%s, price=%s, in_stock=%s, image_url=%s
        WHERE id=%s
    """, (title, price, in_stock, image_url, item_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "item updated"})


@app.post("/api/vendor/upload-logo")
def upload_vendor_logo():
    if "file" not in request.files:
        return jsonify({"error": "file missing"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "empty filename"}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{int(datetime.now().timestamp())}_{filename}"

    save_dir = os.path.join(app.config["UPLOAD_FOLDER"], "logos")
    os.makedirs(save_dir, exist_ok=True)

    filepath = os.path.join(save_dir, unique_name)
    file.save(filepath)

    relative_path = f"logos/{unique_name}"
    public_url = f"http://127.0.0.1:5000/uploads/{relative_path}"

    return jsonify({"message": "uploaded", "logo_path": relative_path, "logo_url": public_url})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
