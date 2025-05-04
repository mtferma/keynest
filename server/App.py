from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import re
import hashlib
import requests
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://mtferma.github.io",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Логируем запуск приложения
app.logger.debug("Starting Flask application...")

# Загружаем данные из секретов
secret_syllables = os.getenv("SYLLABLES_DATA", "")
secret_years = os.getenv("YEARS_DATA", "")
app.logger.debug(f"Loaded SYLLABLES_DATA: {bool(secret_syllables)}")
app.logger.debug(f"Loaded YEARS_DATA: {bool(secret_years)}")

# Инициализируем словари
try:
    if secret_syllables:
        exec_globals = {}
        exec(secret_syllables, exec_globals)
        SYLLABLES_TWO = exec_globals.get("SYLLABLES_TWO", {})
        SYLLABLES_THREE = exec_globals.get("SYLLABLES_THREE", {})
        app.logger.debug(f"SYLLABLES_TWO keys: {list(SYLLABLES_TWO.keys())}")
        app.logger.debug(f"SYLLABLES_THREE keys: {list(SYLLABLES_THREE.keys())}")
    else:
        SYLLABLES_TWO = {}
        SYLLABLES_THREE = {}
        app.logger.warning("SYLLABLES_DATA is empty")
except Exception as e:
    app.logger.error(f"Error loading SYLLABLES_DATA: {str(e)}")
    raise

try:
    if secret_years:
        exec_globals = {}
        exec(secret_years, exec_globals)
        YEARS_MEANING = exec_globals.get("YEARS_MEANING", {})
        app.logger.debug(f"YEARS_MEANING keys: {list(YEARS_MEANING.keys())}")
    else:
        YEARS_MEANING = {}
        app.logger.warning("YEARS_DATA is empty")
except Exception as e:
    app.logger.error(f"Error loading YEARS_DATA: {str(e)}")
    raise

@app.route('/', methods=['GET'])
def home():
    app.logger.debug("Received request to /")
    return jsonify({"message": "Welcome to Keynest API! Use /generate to create a password or /check to evaluate a password."}), 200

@app.route('/generate', methods=['POST'])
def generate_password():
    try:
        app.logger.debug("Received /generate request")
        data = request.get_json()
        if not data:
            app.logger.error("No JSON data received")
            return jsonify({'error': 'No JSON data received'}), 400

        app.logger.debug(f"Request data: {data}")
        syllables = int(data.get('syllables', 2))
        include_numbers = data.get('numbers', False)
        include_symbols = data.get('symbols', False)

        app.logger.debug(f"Parsed: syllables={syllables}, numbers={include_numbers}, symbols={include_symbols}")

        if not SYLLABLES_TWO or not SYLLABLES_THREE:
            app.logger.error("SYLLABLES_TWO or SYLLABLES_THREE is empty")
            return jsonify({'error': 'Syllables dictionaries are empty'}), 500
        if include_numbers and not YEARS_MEANING:
            app.logger.error("YEARS_MEANING is empty")
            return jsonify({'error': 'Years dictionary is empty'}), 500

        password, associations = generate_password_logic(syllables, include_numbers, include_symbols)
        app.logger.debug(f"Generated password: {password}, associations: {associations}")
        
        return jsonify({'password': password, 'associations': associations}), 200

    except ValueError as ve:
        app.logger.error(f"ValueError in /generate: {str(ve)}")
        return jsonify({'error': 'Invalid syllables value, must be an integer'}), 400
    except Exception as e:
        app.logger.error(f"Error in /generate: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/check', methods=['POST'])
def check_password():
    try:
        app.logger.debug("Received /check request")
        data = request.get_json()
        if not data:
            app.logger.error("No JSON data received")
            return jsonify({'error': 'No JSON data received'}), 400

        app.logger.debug(f"Request data: {data}")
        password = data.get('password', '')
        if not isinstance(password, str):
            app.logger.error("Password must be a string")
            return jsonify({'error': 'Password must be a string'}), 400

        app.logger.debug(f"Password to check: {password}")
        result = evaluate_password(password)
        app.logger.debug(f"Check result: {result}")
        
        return jsonify(result), 200

    except Exception as e:
        app.logger.error(f"Error in /check: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_password_logic(syllables, include_numbers, include_symbols):
    syllables_list = []
    associations = []

    for _ in range(syllables):
        if random.choice([True, False]):
            key = random.choice(list(SYLLABLES_TWO.keys()))
            value = SYLLABLES_TWO[key]
        else:
            key = random.choice(list(SYLLABLES_THREE.keys()))
            value = SYLLABLES_THREE[key]
        syllables_list.append(key)
        associations.append(value)

    password = "-".join(syllables_list)

    if include_numbers:
        year = random.choice(list(YEARS_MEANING.keys()))
        password += str(year)
        associations.append(YEARS_MEANING[year])

    if include_symbols:
        symbol = random.choice(["!", "%", "@", "#", "&", "?"])
        password += symbol
        associations.append("спецсимвол")

    return password, associations

def evaluate_password(password):
    score = 1
    suggestions = []

    if len(password) > 12:
        score *= 10
    elif 12 >= len(password) >= 8:
        score *= 5
    elif 8 > len(password) > 5:
        score *= 2

    if re.search(r"\d", password):
        score *= 10
        
    if re.search(r"[A-Z]", password):
        score *= 10

    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score *= 10

    leak_count = is_in_leaked_database(password)
    if leak_count > 0:
        score *= 0
        suggestions.append(
            f"Этот пароль найден в базе утечек {leak_count:,} раз(а)."
        )

    if score >= 5000:
        strength = "Надежный"
        time = "много лет"
    elif score >= 100:
        strength = "Средний"
        time = "несколько дней"
    else:
        strength = "Слабый"
        time = "несколько минут"

    return {
        "strength": strength,
        "time": time,
        "suggestion": " ".join(suggestions) if suggestions else None
    }

def is_in_leaked_database(password):
    try:
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]

        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        res = requests.get(url)

        if res.status_code != 200:
            raise RuntimeError(f"Ошибка при обращении к pwnedpasswords API: {res.status_code}")

        hashes = (line.split(":") for line in res.text.splitlines())
        
        for h, count in hashes:
            if h == suffix:
                return int(count)

        return 0
    except Exception as e:
        app.logger.error(f"Error in is_in_leaked_database: {str(e)}")
        raise

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.logger.debug(f"Starting server on port {port}")
    app.run(debug=False, host="0.0.0.0", port=port)
    app.logger.debug("Server started successfully")