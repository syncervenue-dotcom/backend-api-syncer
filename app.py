import os
import re
import smtplib
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
import hashlib
import time

from flask import Flask, request, jsonify
from pymongo import MongoClient, ASCENDING, errors, GEOSPHERE
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

# Optional: Google ID token verification
try:
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests
    GOOGLE_LIBS_AVAILABLE = True
except Exception:
    GOOGLE_LIBS_AVAILABLE = False



# -------------------- Config --------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/halls_db")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-prod")
JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "72"))
RESET_TOKEN_TTL_MINUTES = int(os.getenv("RESET_TOKEN_TTL_MINUTES", "60"))
MAX_VIDEO_MB = int(os.getenv("MAX_VIDEO_MB", "25"))

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM")
APP_URL = os.getenv("APP_URL", "http://localhost:3000")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")



# Cloudinary (optional, signature only)
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
CLOUDINARY_UPLOAD_PRESET = os.getenv("CLOUDINARY_UPLOAD_PRESET")

app = Flask(__name__)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["halls_db"]
users = db["users"]
venues = db["venues"]
password_resets = db["password_resets"]
bookings = db["bookings"]

#--------------------------------------------------

# After: db = client[...] and collections like `users`, `venues`
bookings = db["bookings"]

# Create helpful index for availability checks and listing
from pymongo import ASCENDING, errors  # (already imported in your file)
try:
    bookings.create_index(
        [("venue_id", ASCENDING), ("date", ASCENDING), ("status", ASCENDING)],
        name="idx_booking_vds"
    )
except errors.PyMongoError:
    pass



















# -------------------- Indexes --------------------
try:
    users.create_index([("email", ASCENDING)], unique=True, name="uniq_email")
    venues.create_index([("owner_id", ASCENDING)], name="idx_owner")
    venues.create_index([("type", ASCENDING)], name="idx_type")
    venues.create_index([("capacity", ASCENDING)], name="idx_capacity")
    venues.create_index([("maps_location", GEOSPHERE)], name="idx_geo")
    venues.create_index([("pricing.overrides.date", ASCENDING)], name="idx_price_date")
    bookings.create_index([("venue_id", ASCENDING), ("date", ASCENDING), ("status", ASCENDING)], name="idx_booking_v_d_s")
    bookings.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)], name="idx_booking_user_time")
except errors.PyMongoError:
    pass


# -------------------- Helpers --------------------
def ok(data=None, status=200):
    return jsonify({"ok": True, **({"data": data} if data is not None else {})}), status


def err(message, status=400):
    return jsonify({"ok": False, "error": message}), status


def issue_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "is_venue_owner": bool(user.get("is_venue_owner", False)),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXPIRES_HOURS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def auth_required(owner_only=False):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return err("Missing or invalid Authorization header.", 401)
            token = auth.split(" ", 1)[1].strip()
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return err("Token expired.", 401)
            except Exception:
                return err("Invalid token.", 401)
            user_id = payload.get("sub")
            if not user_id:
                return err("Invalid token subject.", 401)
            user = users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return err("User not found.", 401)
            if owner_only and not bool(user.get("is_venue_owner", False)):
                return err("Owner access required.", 403)
            request.user = user
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


def send_email(to_email: str, subject: str, html_body: str, text_body: str = None):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and SMTP_FROM):
        print(f"[MAIL-DEV] To: {to_email} | Subject: {subject}\n{html_body}")
        return True
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    if text_body:
        msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    return True


def user_profile_doc(user):
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "full_name": user.get("full_name", ""),
        "contact_number": user.get("contact_number", ""),
        "is_venue_owner": bool(user.get("is_venue_owner", False)),
        "role": user.get("role", "user"),
        "auth_provider": user.get("auth_provider", "password")
    }


# -------------------- Health --------------------
@app.get("/health")
def health():
    return ok({"status": "up"})


# -------------------- Auth: Signup/Login/Google --------------------
@app.post("/auth/signup")
def signup():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password")
    full_name = (body.get("full_name") or "").strip()
    contact_number = (body.get("contact_number") or "").strip()
    is_venue_owner = body.get("is_venue_owner")

    if not validate_email(email):
        return err("Valid email is required.", 422)
    if not password or len(password) < 6:
        return err("Password must be at least 6 characters.", 422)
    if is_venue_owner is None:
        return err("Field 'is_venue_owner' is required (true/false).", 422)

    doc = {
        "full_name": full_name,
        "email": email,
        "password_hash": generate_password_hash(password),
        "contact_number": contact_number,
        "is_venue_owner": bool(is_venue_owner),
        "role": "owner" if is_venue_owner else "user",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "auth_provider": "password"
    }
    try:
        users.insert_one(doc)
    except errors.DuplicateKeyError:
        return err("Email already registered.", 409)

    user = users.find_one({"email": email})
    token = issue_token(user)
    return ok({"token": token, "profile": user_profile_doc(user)}, status=201)


@app.post("/auth/login")
def login():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password")

    if not email or not password:
        return err("Email and password are required.", 422)

    user = users.find_one({"email": email})
    if not user or not check_password_hash(user.get("password_hash", ""), password):
        return err("Invalid credentials.", 401)

    token = issue_token(user)
    return ok({"token": token, "profile": user_profile_doc(user)})


@app.post("/auth/google")
def google_login():
    if not GOOGLE_LIBS_AVAILABLE:
        return err("Google auth libraries not installed. Add 'google-auth'.", 500)
    if not GOOGLE_CLIENT_ID:
        return err("GOOGLE_CLIENT_ID not configured on server.", 500)

    body = request.get_json(silent=True) or {}
    id_token_str = body.get("id_token")
    if not id_token_str:
        return err("Missing 'id_token'.", 422)

    try:
        idinfo = google_id_token.verify_oauth2_token(
            id_token_str, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        if idinfo.get("aud") != GOOGLE_CLIENT_ID:
            return err("Invalid audience for Google token.", 401)
        if not idinfo.get("email_verified", False):
            return err("Google email not verified.", 401)
    except Exception as e:
        return err(f"Invalid Google ID token: {str(e)}", 401)

    email = (idinfo.get("email") or "").lower()
    full_name = idinfo.get("name", "")
    contact_number = (body.get("contact_number") or "").strip()
    is_venue_owner = bool(body.get("is_venue_owner", False))

    user = users.find_one({"email": email})
    if not user:
        doc = {
            "full_name": full_name,
            "email": email,
            "password_hash": None,
            "contact_number": contact_number,
            "is_venue_owner": is_venue_owner,
            "role": "owner" if is_venue_owner else "user",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "auth_provider": "google"
        }
        try:
            users.insert_one(doc)
        except errors.DuplicateKeyError:
            user = users.find_one({"email": email})
        else:
            user = users.find_one({"email": email})

    if is_venue_owner and not bool(user.get("is_venue_owner", False)):
        users.update_one({"_id": user["_id"]}, {"$set": {"is_venue_owner": True, "role": "owner"}})
        user = users.find_one({"_id": user["_id"]})

    token = issue_token(user)
    return ok({"token": token, "profile": user_profile_doc(user)})


# Current user profile
@app.get("/auth/me")
@auth_required(owner_only=False)
def me():
    return ok({"profile": user_profile_doc(request.user)})


# -------------------- Forgot / Reset Password --------------------
@app.post("/auth/forgot-password")
def forgot_password():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    if not validate_email(email):
        return err("Valid email is required.", 422)

    user = users.find_one({"email": email})
    if user:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
        password_resets.insert_one({
            "user_id": user["_id"],
            "token": token,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        })
        reset_link = f"{APP_URL.rstrip('/')}/reset-password?token={token}"
        html = f"""
            <p>We received a request to reset your password.</p>
            <p><a href="{reset_link}">Click here to reset your password</a></p>
            <p>This link expires in {RESET_TOKEN_TTL_MINUTES} minutes.</p>
        """
        send_email(user["email"], "Reset your password", html, f"Reset link: {reset_link}")
    return ok({"message": "If the email exists, a reset link has been sent."})


@app.post("/auth/reset-password")
def reset_password():
    body = request.get_json(silent=True) or {}
    token = body.get("token")
    new_password = body.get("new_password")
    if not token or not new_password or len(new_password) < 6:
        return err("Token and a new password (min 6 chars) are required.", 422)

    rec = password_resets.find_one({"token": token})
    if not rec:
        return err("Invalid or expired token.", 400)
    if rec["expires_at"] < datetime.utcnow():
        return err("Token expired.", 400)

    user_id = rec["user_id"]
    users.update_one({"_id": user_id}, {
        "$set": {"password_hash": generate_password_hash(new_password), "updated_at": datetime.utcnow()}
    })
    password_resets.delete_one({"_id": rec["_id"]})
    return ok({"message": "Password reset successful."})


# -------------------- Venues: Register & Update --------------------
def validate_price_overrides(price_with_dates):
    for item in price_with_dates:
        if not isinstance(item, dict) or "date" not in item or "price" not in item:
            return "'price_with_dates' items must have 'date' and 'price'."
        try:
            float(item["price"])
        except Exception:
            return "'price' must be a number."
    return None





# -------------------- Uploads: Cloudinary --------------------
@app.post("/uploads/sign-cloudinary")
@auth_required(owner_only=True)
def sign_cloudinary():
    """
    Returns parameters for client-side upload to Cloudinary.

    If CLOUDINARY_API_SECRET is set -> Signed upload (recommended):
      Client will POST multipart/form-data to:
        https://api.cloudinary.com/v1_1/{cloud_name}/auto/upload
      Required form fields:
        - file: <binary>
        - api_key
        - timestamp
        - folder (optional but recommended)
        - public_id (optional)
        - signature (computed here)
        - resource_type (optional: 'image'|'video'|'auto')
        - overwrite (optional: true/false)
        - invalidate (optional: true/false)

    Else if only CLOUDINARY_UPLOAD_PRESET is set -> Unsigned upload:
      Client will POST to same endpoint with:
        - file
        - upload_preset
        - folder (optional)
        - public_id (optional)
    """
    if not CLOUDINARY_CLOUD_NAME:
        return err("CLOUDINARY_CLOUD_NAME not configured on server.", 500)

    body = request.get_json(silent=True) or {}
    folder = (body.get("folder") or "venues").strip()
    public_id = (body.get("public_id") or "").strip()
    resource_type = (body.get("resource_type") or "auto").strip()  # 'image' | 'video' | 'auto'
    overwrite = bool(body.get("overwrite", True))
    invalidate = bool(body.get("invalidate", False))

    upload_url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/{resource_type}/upload"

    # --- Signed uploads ---
    if CLOUDINARY_API_SECRET and CLOUDINARY_API_KEY:
        timestamp = int(time.time())
        # Params to sign (exclude file, api_key, signature)
        params_to_sign = {
            "timestamp": timestamp,
            "folder": folder,
            "public_id": public_id or None,
            "overwrite": "true" if overwrite else "false",
            "invalidate": "true" if invalidate else "false",
            # You can add more Cloudinary params here if you need them later (eager, context, tags, etc.)
        }
        # Build the string to sign: key=value joined by '&', keys sorted, skip None/empty
        filtered = {k: v for k, v in params_to_sign.items() if v not in (None, "", False)}
        sign_str = "&".join(f"{k}={filtered[k]}" for k in sorted(filtered.keys()))
        sign_str = f"{sign_str}{CLOUDINARY_API_SECRET}"
        signature = hashlib.sha1(sign_str.encode("utf-8")).hexdigest()

        return ok({
            "mode": "signed",
            "upload_url": upload_url,
            "params": {
                "api_key": CLOUDINARY_API_KEY,
                "timestamp": timestamp,
                "folder": folder,
                **({"public_id": public_id} if public_id else {}),
                "overwrite": overwrite,
                "invalidate": invalidate,
                "signature": signature
            }
        })

    # --- Unsigned uploads (MVP) ---
    if not CLOUDINARY_UPLOAD_PRESET:
        return err("Either (API_KEY + API_SECRET) for signed or CLOUDINARY_UPLOAD_PRESET for unsigned must be set.", 500)

    return ok({
        "mode": "unsigned",
        "upload_url": upload_url,
        "params": {
            "upload_preset": CLOUDINARY_UPLOAD_PRESET,
            "folder": folder,
            **({"public_id": public_id} if public_id else {})
        }
    })














@app.post("/venues/register")
@auth_required(owner_only=True)
def register_venue():
    b = request.get_json(silent=True) or {}
    required = ["venue_name", "type", "address", "maps_location", "capacity"]
    miss = [k for k in required if not b.get(k)]
    if miss:
        return err(f"Missing fields: {', '.join(miss)}", 422)

    vtype = b.get("type")
    if vtype not in ["Hall", "Auditorium", "Banquet", "Lawn"]:
        return err("Invalid 'type'. Must be one of: Hall, Auditorium, Banquet, Lawn.", 422)

    loc = b.get("maps_location") or {}
    if "lat" not in loc or "lng" not in loc:
        return err("'maps_location' must include 'lat' and 'lng'.", 422)
    try:
        lat = float(loc["lat"]); lng = float(loc["lng"])
    except Exception:
        return err("'maps_location.lat' and 'lng' must be numbers.", 422)

    try:
        capacity = int(b.get("capacity"))
        if capacity <= 0: raise ValueError()
    except Exception:
        return err("'capacity' must be a positive integer.", 422)

    dates_available = b.get("dates_available", [])
    if dates_available and not all(isinstance(d, str) for d in dates_available):
        return err("'dates_available' must be an array of 'YYYY-MM-DD' strings.", 422)

    price_with_dates = b.get("price_with_dates", [])
    if price_with_dates:
        msg = validate_price_overrides(price_with_dates)
        if msg: return err(msg, 422)

    space = b.get("space")
    if space is not None:
        try: space = float(space)
        except Exception: return err("'space' (sq-ft) must be a number.", 422)

    videos = b.get("videos", [])
    for vid in videos or []:
        if isinstance(vid, dict) and "size_mb" in vid:
            try:
                if float(vid["size_mb"]) > MAX_VIDEO_MB:
                    return err(f"Video exceeds {MAX_VIDEO_MB} MB limit.", 422)
            except Exception:
                return err("'videos.size_mb' must be a number if provided.", 422)

    doc = {
        "owner_id": request.user["_id"],
        "venue_name": b["venue_name"],
        "type": vtype,
        "address": b["address"],
        "maps_location": {"type": "Point", "coordinates": [lng, lat]},
        "capacity": capacity,
        "dates_available": dates_available,
        "pricing": {"overrides": [{"date": i["date"], "price": float(i["price"])} for i in price_with_dates]},
        "space_sqft": space,
        "amenities": {
            "parking_valet": bool(b.get("parking_valet", False)),
            "entry_package": bool(b.get("entry_package", False)),
            "water": bool(b.get("water", False)),
            "air_conditioner": bool(b.get("air_conditioner", False)),
            "partition_facility": bool(b.get("partition_facility", False)),
            "sound_system": bool(b.get("sound_system", False))
        },
        "additional_description": b.get("additional_description", ""),
        "pictures": b.get("pictures", []),
        "videos": videos,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = venues.insert_one(doc)
    return ok({"venue_id": str(result.inserted_id)}, 201)


@app.patch("/venues/<venue_id>")
@auth_required(owner_only=True)
def update_venue(venue_id):
    v = venues.find_one({"_id": ObjectId(venue_id)})
    if not v:
        return err("Venue not found.", 404)
    if str(v["owner_id"]) != str(request.user["_id"]):
        return err("You do not own this venue.", 403)

    b = request.get_json(silent=True) or {}
    update = {"updated_at": datetime.utcnow()}

    if "venue_name" in b: update["venue_name"] = str(b["venue_name"])
    if "type" in b:
        if b["type"] not in ["Hall", "Auditorium", "Banquet", "Lawn"]:
            return err("Invalid 'type'.", 422)
        update["type"] = b["type"]
    if "address" in b: update["address"] = str(b["address"])
    if "maps_location" in b:
        loc = b.get("maps_location") or {}
        if "lat" not in loc or "lng" not in loc:
            return err("'maps_location' must include 'lat' and 'lng'.", 422)
        try: lat = float(loc["lat"]); lng = float(loc["lng"])
        except Exception: return err("'maps_location.lat' and 'lng' must be numbers.", 422)
        update["maps_location"] = {"type": "Point", "coordinates": [lng, lat]}
    if "capacity" in b:
        try:
            cap = int(b["capacity"]); 
            if cap <= 0: raise ValueError()
            update["capacity"] = cap
        except Exception: return err("'capacity' must be positive integer.", 422)
    if "dates_available" in b:
        if b["dates_available"] and not all(isinstance(d, str) for d in b["dates_available"]):
            return err("'dates_available' must be an array of 'YYYY-MM-DD' strings.", 422)
        update["dates_available"] = b["dates_available"]
    if "price_with_dates" in b:
        msg = validate_price_overrides(b["price_with_dates"] or [])
        if msg: return err(msg, 422)
        update["pricing"] = {"overrides": [{"date": i["date"], "price": float(i["price"])} for i in (b["price_with_dates"] or [])]}
    if "space" in b:
        try: update["space_sqft"] = float(b["space"])
        except Exception: return err("'space' (sq-ft) must be a number.", 422)
    # amenities
    for k in ["parking_valet","entry_package","water","air_conditioner","partition_facility","sound_system"]:
        if k in b:
            update.setdefault("amenities", v.get("amenities", {}))
            update["amenities"][k] = bool(b[k])
    # media
    if "pictures" in b: update["pictures"] = b["pictures"]
    if "videos" in b:
        for vid in b["videos"] or []:
            if isinstance(vid, dict) and "size_mb" in vid:
                try:
                    if float(vid["size_mb"]) > MAX_VIDEO_MB:
                        return err(f"Video exceeds {MAX_VIDEO_MB} MB limit.", 422)
                except Exception:
                    return err("'videos.size_mb' must be a number if provided.", 422)
        update["videos"] = b["videos"]

    venues.update_one({"_id": v["_id"]}, {"$set": update})
    v2 = venues.find_one({"_id": v["_id"]})
    return ok({"venue": {
        "id": str(v2["_id"]),
        "venue_name": v2.get("venue_name"),
        "type": v2.get("type"),
        "address": v2.get("address"),
        "maps_location": v2.get("maps_location"),
        "capacity": v2.get("capacity"),
        "dates_available": v2.get("dates_available", []),
        "pricing": v2.get("pricing", {}),
        "space_sqft": v2.get("space_sqft"),
        "amenities": v2.get("amenities", {}),
        "pictures": v2.get("pictures", []),
        "videos": v2.get("videos", [])
    }})






# -------------------- Venues: Search (Public/User) --------------------
@app.get("/venues/search")
def search_venues():
    q = {}
    vtype = request.args.get("type")
    if vtype:
        q["type"] = vtype

    cap_min = request.args.get("capacity_min", type=int)
    cap_max = request.args.get("capacity_max", type=int)
    if cap_min is not None or cap_max is not None:
        q["capacity"] = {}
        if cap_min is not None:
            q["capacity"]["$gte"] = cap_min
        if cap_max is not None:
            q["capacity"]["$lte"] = cap_max
        if not q["capacity"]:
            q.pop("capacity")

    date = request.args.get("date")
    if date:
        q["dates_available"] = date

    near_lat = request.args.get("near_lat", type=float)
    near_lng = request.args.get("near_lng", type=float)
    near_km = request.args.get("near_km", type=float)
    if near_lat is not None and near_lng is not None and near_km is not None:
        q["maps_location"] = {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [near_lng, near_lat]},
                "$maxDistance": int(near_km * 1000)
            }
        }

    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    if price_min is not None or price_max is not None:
        elem = {}
        if date:
            elem["date"] = date
        if price_min is not None:
            elem["price"] = {**elem.get("price", {}), "$gte": price_min}
        if price_max is not None:
            elem["price"] = {**elem.get("price", {}), "$lte": price_max}
        q["pricing.overrides"] = {"$elemMatch": elem} if elem else {"$exists": True}

    cur = venues.find(q).limit(50)
    out = []
    for v in cur:
        out.append({
            "id": str(v["_id"]),
            "venue_name": v.get("venue_name"),
            "type": v.get("type"),
            "address": v.get("address"),
            "maps_location": v.get("maps_location"),
            "capacity": v.get("capacity"),
            "dates_available": v.get("dates_available", []),
            "pricing": v.get("pricing", {}),
            "space_sqft": v.get("space_sqft"),
            "amenities": v.get("amenities", {}),
            "pictures": v.get("pictures", []),
            "videos": v.get("videos", [])
        })
    return ok({"venues": out})


# -------------------- Bookings: CRUD with availability checks --------------------
def compute_price_for_date(venue, date_str):
    for o in venue.get("pricing", {}).get("overrides", []):
        if o.get("date") == date_str:
            try:
                return float(o.get("price"))
            except Exception:
                return None
    return None

def resolve_price_for_date(venue: dict, date_str: str):
    """
    Returns the price for a given YYYY-MM-DD date from venue.pricing.overrides,
    or None if not defined.
    """
    overrides = (venue.get("pricing") or {}).get("overrides") or []
    for item in overrides:
        if item.get("date") == date_str:
            try:
                return float(item.get("price"))
            except Exception:
                return None
    return None


from bson import ObjectId  # you already import this above

@app.get("/venues/<venue_id>/availability")
def venue_availability(venue_id):
    """
    Query: ?date=YYYY-MM-DD
    Response: { ok: true, data: { available: bool, price: number|null } }
    """
    date_str = request.args.get("date")
    if not date_str:
        return err("Query param 'date' is required as YYYY-MM-DD.", 422)

    try:
        v_id = ObjectId(venue_id)
    except Exception:
        return err("Invalid venue_id.", 400)

    venue = venues.find_one({"_id": v_id})
    if not venue:
        return err("Venue not found.", 404)

    # Must be in venue's available dates
    if date_str not in (venue.get("dates_available") or []):
        return ok({"available": False, "price": None})

    # Not already booked (pending or confirmed)
    existing = bookings.find_one({
        "venue_id": venue["_id"],
        "date": date_str,
        "status": {"$in": ["pending", "confirmed"]}
    })
    available = existing is None
    price = resolve_price_for_date(venue, date_str)

    return ok({"available": available, "price": price})



@app.delete("/bookings/<booking_id>")
@auth_required()
def cancel_booking(booking_id):
    try:
        b_id = ObjectId(booking_id)
    except Exception:
        return err("Invalid booking_id.", 400)

    b = bookings.find_one({"_id": b_id})
    if not b:
        return err("Booking not found.", 404)

    v = venues.find_one({"_id": b["venue_id"]})
    if not v:
        return err("Venue not found for booking.", 404)

    user = request.user
    is_booker = b["user_id"] == user["_id"]
    is_owner = v["owner_id"] == user["_id"]
    if not (is_booker or is_owner):
        return err("Not allowed to cancel this booking.", 403)

    if b.get("status") == "cancelled":
        return ok({"cancelled": True})

    bookings.update_one(
        {"_id": b["_id"]},
        {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
    )
    return ok({"cancelled": True})

@app.get("/bookings")
@auth_required()  # any authenticated user
def list_bookings():
    user = request.user

    if bool(user.get("is_venue_owner", False)):
        # Collect owner’s venue IDs
        owned = list(venues.find({"owner_id": user["_id"]}, {"_id": 1}))
        owner_venue_ids = [v["_id"] for v in owned]
        if not owner_venue_ids:
            return ok({"bookings": []})
        query = {"venue_id": {"$in": owner_venue_ids}}
    else:
        # Regular user → only their bookings
        query = {"user_id": user["_id"]}

    cur = bookings.find(query).sort("date", 1).limit(200)
    out = []
    for b in cur:
        out.append({
            "id": str(b["_id"]),
            "venue_id": str(b["venue_id"]),
            "user_id": str(b["user_id"]),
            "date": b.get("date"),
            "guests": b.get("guests"),
            "status": b.get("status"),
            "price_locked": b.get("price_locked"),
            "created_at": b.get("created_at"),
            "updated_at": b.get("updated_at"),
        })
    return ok({"bookings": out})




@app.post("/bookings")
@auth_required(owner_only=False)
def create_booking():
    """
    Request JSON:
    {
      "venue_id": "<venue_id>",
      "date": "2025-09-01",
      "guests_count": 300,
      "notes": "optional"
    }
    """
    b = request.get_json(silent=True) or {}
    venue_id = b.get("venue_id")
    date_str = b.get("date")
    guests = b.get("guests_count")

    if not venue_id or not date_str or guests is None:
        return err("Fields 'venue_id', 'date', 'guests_count' are required.", 422)
    try:
        guests = int(guests); 
        if guests <= 0: raise ValueError()
    except Exception:
        return err("'guests_count' must be a positive integer.", 422)

    try:
        v = venues.find_one({"_id": ObjectId(venue_id)})
    except Exception:
        return err("Invalid venue_id.", 422)
    if not v:
        return err("Venue not found.", 404)

    if date_str not in (v.get("dates_available") or []):
        return err("Venue not available on that date.", 409)

    # Check if already booked (pending or confirmed)
    existing = bookings.find_one({
        "venue_id": v["_id"],
        "date": date_str,
        "status": {"$in": ["pending", "confirmed"]}
    })
    if existing:
        return err("Date already booked or pending.", 409)

    price = compute_price_for_date(v, date_str)
    doc = {
        "venue_id": v["_id"],
        "user_id": request.user["_id"],
        "date": date_str,
        "guests_count": guests,
        "price": price,
        "status": "pending",
        "notes": b.get("notes", ""),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    res = bookings.insert_one(doc)
    return ok({"booking_id": str(res.inserted_id), "price": price, "status": "pending"}, 201)


@app.get("/bookings/my-requests")
@auth_required(owner_only=False)
def my_bookings():
    cur = bookings.find({"user_id": request.user["_id"]}).sort("created_at", ASCENDING)
    data = []
    for bk in cur:
        data.append({
            "id": str(bk["_id"]),
            "venue_id": str(bk["venue_id"]),
            "date": bk["date"],
            "guests_count": bk.get("guests_count"),
            "price": bk.get("price"),
            "status": bk.get("status"),
            "notes": bk.get("notes", "")
        })
    return ok({"bookings": data})


@app.get("/bookings/for-my-venues")
@auth_required(owner_only=True)
def bookings_for_owner():
    status = request.args.get("status")
    venue_ids = [v["_id"] for v in venues.find({"owner_id": request.user["_id"]}, {"_id": 1})]
    q = {"venue_id": {"$in": venue_ids}}
    if status:
        q["status"] = status
    cur = bookings.find(q).sort("date", ASCENDING)
    data = []
    for bk in cur:
        data.append({
            "id": str(bk["_id"]),
            "venue_id": str(bk["venue_id"]),
            "user_id": str(bk["user_id"]),
            "date": bk["date"],
            "guests_count": bk.get("guests_count"),
            "price": bk.get("price"),
            "status": bk.get("status"),
            "notes": bk.get("notes", "")
        })
    return ok({"bookings": data})


@app.patch("/bookings/<booking_id>")
@auth_required(owner_only=False)
def update_booking(booking_id):
    b = request.get_json(silent=True) or {}
    new_status = b.get("status")
    if new_status not in ["confirmed", "rejected", "cancelled"]:
        return err("Status must be one of: confirmed, rejected, cancelled.", 422)

    try:
        bk = bookings.find_one({"_id": ObjectId(booking_id)})
    except Exception:
        return err("Invalid booking_id.", 422)
    if not bk:
        return err("Booking not found.", 404)

    # Owner or booker actions
    is_owner = False
    v = venues.find_one({"_id": bk["venue_id"]})
    if v and str(v["owner_id"]) == str(request.user["_id"]):
        is_owner = True

    if new_status in ["confirmed", "rejected"]:
        if not is_owner:
            return err("Only the venue owner can confirm/reject.", 403)
        if bk["status"] != "pending":
            return err("Only pending bookings can be confirmed/rejected.", 409)
    if new_status == "cancelled":
        # Booker can cancel their own; owner can also cancel? We'll allow booker only
        if str(bk["user_id"]) != str(request.user["_id"]):
            return err("Only the booking user can cancel.", 403)

    bookings.update_one({"_id": bk["_id"]}, {"$set": {"status": new_status, "updated_at": datetime.utcnow()}})
    bk2 = bookings.find_one({"_id": bk["_id"]})
    return ok({
        "booking": {
            "id": str(bk2["_id"]),
            "venue_id": str(bk2["venue_id"]),
            "user_id": str(bk2["user_id"]),
            "date": bk2["date"],
            "guests_count": bk2["guests_count"],
            "price": bk2.get("price"),
            "status": bk2["status"],
            "notes": bk2.get("notes", "")
        }
    })


# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
