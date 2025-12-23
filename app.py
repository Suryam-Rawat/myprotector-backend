from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from cryptography.fernet import Fernet

app = Flask(__name__)
CORS(app)

# =========================
# ENCRYPTION SETUP
# =========================
FERNET_KEY = Fernet.generate_key()
cipher = Fernet(FERNET_KEY)

def encrypt(text):
    return cipher.encrypt(text.encode()).decode()

# =========================
# REGEX DETECTORS
# =========================
AADHAAR = re.compile(r"\b[2-9][0-9]{11}\b")
EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE = re.compile(r"\b[6-9][0-9]{9}\b")
API_KEY = re.compile(r"(sk-|AKIA|AIza)[A-Za-z0-9_-]{10,}")

# =========================
# CORE SCAN LOGIC
# =========================
def scan_prompt(prompt):
    risk = 0
    reasons = []
    sanitized = prompt

    def detect(regex, label, score):
        nonlocal risk, sanitized
        matches = regex.findall(prompt)
        for m in matches:
            risk += score
            reasons.append(f"{label} detected")
            sanitized = sanitized.replace(
                m, f"[ENCRYPTED:{encrypt(m)[:16]}...]"
            )

    detect(AADHAAR, "Aadhaar number", 80)
    detect(API_KEY, "API key", 90)
    detect(EMAIL, "Email address", 30)
    detect(PHONE, "Phone number", 30)

    if risk >= 80:
        decision = "BLOCK"
    elif risk >= 30:
        decision = "WARN"
    else:
        decision = "ALLOW"

    return {
        "decision": decision,
        "risk_score": min(risk, 100),
        "reasons": reasons,
        "sanitized_prompt": sanitized
    }

# =========================
# ROUTES (VERY IMPORTANT)
# =========================

@app.route("/")
def home():
    return "MyProtector backend running"

# 🔍 TEST ROUTE (BROWSER)
@app.route("/v1/prompt/scan", methods=["GET"])
def test_scan():
    return "SCAN ROUTE EXISTS"

# 🔐 MAIN SCAN API (POST)
@app.route("/v1/prompt/scan", methods=["POST"])
def scan():
    data = request.get_json()
    prompt = data.get("prompt", "")
    return jsonify(scan_prompt(prompt))

# 🔑 CLAIM API KEY
@app.route("/v1/api/claim", methods=["POST"])
def claim():
    data = request.get_json()
    email = data.get("email", "")
    key = "mp_live_" + encrypt(email)[:24]
    return jsonify({
        "api_key": key,
        "limit": "100 scans/day",
        "retention": "0 days"
    })

# =========================
# START SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
