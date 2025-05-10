from flask import Flask, request, jsonify
from flask_cors import CORS
from deep_translator import GoogleTranslator
import random
import re
import hashlib
import requests
import os

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://keynest.ru",
            "https://mtferma.github.io",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

SYLLABLES_PATH = "/etc/secrets/SYLLABLES_DATA"
YEARS_PATH = "/etc/secrets/YEARS_DATA"

def load_and_exec_secret(path, default_dict_name):
    try:
        with open(path, "r") as f:
            code = f.read()
        exec_globals = {}
        exec(code, exec_globals)
        return exec_globals.get(default_dict_name, {})
    except Exception:
        return {}

SYLLABLES_TWO = load_and_exec_secret(SYLLABLES_PATH, "SYLLABLES_TWO")
SYLLABLES_THREE = load_and_exec_secret(SYLLABLES_PATH, "SYLLABLES_THREE")
YEARS_MEANING = load_and_exec_secret(YEARS_PATH, "YEARS_MEANING")

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to Keynest API! Use /generate to create a password or /check to evaluate a password."
    }), 200

@app.route('/generate', methods=['POST'])
def generate_password():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    try:
        seed = data.get('seed', '').strip()
        syllables = int(data.get('syllables', 2))
        include_numbers = data.get('numbers', False)
        include_symbols = data.get('symbols', False)

        if not SYLLABLES_TWO or not SYLLABLES_THREE:
            return jsonify({'error': 'Syllables dictionaries are empty'}), 500
        if include_numbers and not YEARS_MEANING:
            return jsonify({'error': 'Years dictionary is empty'}), 500

        seed_suffix = get_seed_suffix(seed)
        password, associations = generate_password_logic(
            syllables, include_numbers, include_symbols, seed_suffix
        )

        return jsonify({'password': password, 'associations': associations}), 200

    except ValueError:
        return jsonify({'error': 'Invalid syllables value, must be an integer'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check', methods=['POST'])
def check_password():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    password = data.get('password', '')
    if not isinstance(password, str):
        return jsonify({'error': 'Password must be a string'}), 400

    try:
        result = evaluate_password(password)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_seed_suffix(seed):
    if not seed:
        return ""
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(seed)
        return translated[:3].lower()
    except Exception:
        return ""

def generate_password_logic(syllables, include_numbers, include_symbols, seed_suffix=""):
    syllables_list = []
    associations = []

    for _ in range(syllables):
        use_two = random.choice([True, False])
        dictionary = SYLLABLES_TWO if use_two else SYLLABLES_THREE
        key = random.choice(list(dictionary.keys()))
        syllables_list.append(key)
        associations.append(dictionary[key])

    password = "-".join(syllables_list)

    if include_numbers:
        year = random.choice(list(YEARS_MEANING.keys()))
        password += str(year)
        associations.append(YEARS_MEANING[year])

    if include_symbols:
        symbol = random.choice(["!", "%", "@", "#", "&", "?"])
        password += symbol
        associations.append("спецсимвол")

    if seed_suffix:
        if random.choice([True, False]):
            password = f"{seed_suffix}-{password}"
        else:
            password = f"{password}{seed_suffix}"
        associations.append(f"сид: {seed_suffix}")

    return password, associations

def evaluate_password(password):
    score = 1
    suggestions = []

    if len(password) > 12:
        score *= 10
    elif len(password) >= 8:
        score *= 5
    elif len(password) > 5:
        score *= 2

    if re.search(r"\d", password):
        score *= 10
    if re.search(r"[A-Z]", password):
        score *= 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score *= 10

    leak_count = is_in_leaked_database(password)
    if leak_count > 0:
        score = 0
        suggestions.append(f"Этот пароль найден в базе утечек {leak_count:,} раз(а).")

    if score >= 5000:
        strength, time = "Надежный", "много лет"
    elif score >= 100:
        strength, time = "Средний", "несколько дней"
    else:
        strength, time = "Слабый", "несколько минут"

    return {
        "strength": strength,
        "time": time,
        "suggestion": " ".join(suggestions) if suggestions else None
    }

def is_in_leaked_database(password):
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"

    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"Pwned Passwords API error: {response.status_code}")

    hashes = (line.split(":") for line in response.text.splitlines())
    for hash_suffix, count in hashes:
        if hash_suffix == suffix:
            return int(count)

    return 0

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
