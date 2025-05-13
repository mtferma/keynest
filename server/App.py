from flask import Flask, request, jsonify
from flask_cors import CORS
from unidecode import unidecode
import random
import re
import hashlib
import requests
import os
import math

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

    cleaned = re.sub(r'[^а-яА-Яa-zA-Z]', '', seed)
    cleaned = re.sub(r'\d+', '', cleaned)

    transliterated = unidecode(cleaned)

    return transliterated[:3].lower()

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
        password = f"{seed_suffix}-{password}"
        associations.append(f"код: {seed_suffix}")

    return password, associations


def evaluate_password(password):
    suggestions = []
    leak_count = is_in_leaked_database(password)

    if leak_count > 0:
        return {
            "strength": "Компрометирован",
            "time": "Мгновенно",
            "suggestion": f"Этот пароль найден в базе утечек {leak_count:,} раз(а)."
        }

    length = len(password)
    char_sets = 0
    if re.search(r"[a-z]", password):
        char_sets += 26
    if re.search(r"[A-Z]", password):
        char_sets += 26
    if re.search(r"\d", password):
        char_sets += 10
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        char_sets += 32

    if char_sets == 0:
        entropy = 0
    else:
        entropy = length * math.log2(char_sets)

    combinations = 2 ** entropy
    attempts_per_second = 1e11
    seconds_to_crack = combinations / attempts_per_second

    def format_time(seconds):
        if seconds < 1:
            return "мгновенно"
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        years = days / 365
        if years >= 1:
            return f"{int(years)} лет"
        elif days >= 1:
            return f"{int(days)} дней"
        elif hours >= 1:
            return f"{int(hours)} часов"
        elif minutes >= 1:
            return f"{int(minutes)} минут"
        else:
            return f"{int(seconds)} секунд"

    if entropy >= 80:
        strength = "Надежный"
    elif entropy >= 50:
        strength = "Средний"
    else:
        strength = "Слабый"
        if length < 8:
            suggestions.append("Используйте минимум 8 символов.")
        if char_sets < 50:
            suggestions.append("Добавьте символы разных типов: заглавные, цифры и спецсимволы.")

    return {
        "strength": strength,
        "time": format_time(seconds_to_crack),
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
