from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import re
import hashlib
import requests
import os
# Загружаем данные из секретов
secret_syllables = os.getenv("SYLLABLES_DATA", "")
secret_years = os.getenv("YEARS_DATA", "")

# Инициализируем словари
if secret_syllables:
    exec_globals = {}
    exec(secret_syllables, exec_globals)
    SYLLABLES_TWO = exec_globals.get("SYLLABLES_TWO", {})
    SYLLABLES_THREE = exec_globals.get("SYLLABLES_THREE", {})
else:
    SYLLABLES_TWO = {}
    SYLLABLES_THREE = {}

if secret_years:
    exec_globals = {}
    exec(secret_years, exec_globals)
    YEARS_MEANING = exec_globals.get("YEARS_MEANING", {})
else:
    YEARS_MEANING = {}

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://mtferma.github.io",  # URL вашего GitHub Pages
            "http://localhost:3000"            # Для локальной разработки
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Добавляем маршрут для корневого пути
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to Keynest API! Use /generate to create a password or /check to evaluate a password."}), 200

@app.route('/generate', methods=['POST'])
def generate_password():
    try:
        data = request.get_json()
        
        syllables = int(data.get('syllables', 2)) 
        include_numbers = data.get('numbers', False)
        include_symbols = data.get('symbols', False)

        password, associations = generate_password_logic(syllables, include_numbers, include_symbols)
        return jsonify({'password': password, 'associations': associations}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check', methods=['POST'])
def check_password():
    try:
        data = request.get_json()
        password = data.get('password', '')

        result = evaluate_password(password)
        return jsonify(result), 200
    except Exception as e:
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
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    res = requests.get(url)

    if res.status_code != 200:
        raise RuntimeError("Ошибка при обращении к pwnedpasswords API")

    hashes = (line.split(":") for line in res.text.splitlines())
    
    for h, count in hashes:
        if h == suffix:
            return int(count) 

    return 0 

if __name__ == '__main__':
    # Используем порт из переменной окружения PORT, заданной Render
    port = int(os.getenv("PORT", 5000))  # По умолчанию 5000, если PORT не задан
    app.run(debug=False, host="0.0.0.0", port=port)  # Слушаем на 0.0.0.0 для Render

