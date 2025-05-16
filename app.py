from flask import Flask, render_template, request, jsonify, url_for
from gtts import gTTS
import os
import time

app = Flask(__name__)

# Base de datos mejorada
MENUS = {
    "bajar_peso": {
        "vegetariano": {
            "menu": ["Smoothie verde 🥤", "Ensalada de quinoa 🥗", "Sopa de lentejas 🍲"],
            "calorias": 1200
        },
        "vegano": {
            "menu": ["Tostadas de aguacate 🥑", "Buddha bowl 🌱", "Curry de garbanzos 🍛"],
            "calorias": 1100
        },
        "tradicional": {
            "menu": ["Huevos revueltos 🍳", "Pechuga a la plancha 🍗", "Merluza al horno 🐟"],
            "calorias": 1300
        }
    },
    "aumentar_masa": {
        "vegetariano": {
            "menu": ["Batido proteico 🥛", "Lentejas con arroz 🥘", "Tofu salteado 🍳"],
            "calorias": 2500
        },
        "vegano": {
            "menu": ["Batido de cacahuete 🥜", "Seitan a la parrilla 🌭", "Hamburguesa de lentejas 🍔"],
            "calorias": 2400
        },
        "tradicional": {
            "menu": ["Tortilla de claras 🥚", "Pollo con boniato 🍗", "Salmón con espárragos 🐟"],
            "calorias": 2600
        }
    }
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['message'].lower()
    response = generate_response(user_message)
    return jsonify(response)

def generate_response(message):
    if "hola" in message:
        return {
            "response": "¡Hola! 👋 Soy NutriBot. ¿Quieres bajar de peso o aumentar masa muscular?",
            "reset": False
        }
    elif "reiniciar" in message:
        return {
            "response": "Conversación reiniciada. ¿Quieres bajar de peso o aumentar masa muscular?",
            "reset": True
        }
    elif "bajar de peso" in message:
        return {
            "response": "¡Excelente! 💪 ¿Prefieres menú vegetariano, vegano o tradicional?",
            "goal": "bajar_peso"
        }
    elif "aumentar masa muscular" in message:
        return {
            "response": "¡Perfecto! 🏋️ ¿Prefieres menú vegetariano, vegano o tradicional?",
            "goal": "aumentar_masa"
        }
    elif "vegetariano" in message:
        return {
            "response": "Menú vegetariano seleccionado 🥕. ¿Quieres ver tu plan nutricional? (si/no)",
            "diet": "vegetariano"
        }
    elif "vegano" in message:
        return {
            "response": "Menú vegano seleccionado 🌱. ¿Quieres ver tu plan nutricional? (si/no)",
            "diet": "vegano"
        }
    elif "tradicional" in message:
        return {
            "response": "Menú tradicional seleccionado 🍗. ¿Quieres ver tu plan nutricional? (si/no)",
            "diet": "tradicional"
        }
    elif "si" in message:
        return {
            "response": generate_menu(),
            "show_menu": True
        }
    elif "no" in message:
        return {"response": "¡Entendido! ¿En qué más puedo ayudarte?"}
    else:
        return {"response": "No entendí. ¿Podrías repetirlo?"}

def generate_menu():
    # Esta función se completa con JavaScript para mantener el estado
    return "Menú generado dinámicamente"

@app.route('/get_full_menu', methods=['POST'])
def get_full_menu():
    data = request.json
    menu_data = MENUS[data['goal']][data['diet']]
    return jsonify({
        "menu": "🍽️ <strong>Menú recomendado:</strong><br>• " + "<br>• ".join(menu_data["menu"]),
        "calories": f"⚖️ <strong>Calorías diarias:</strong> {menu_data['calorias']} kcal"
    })

# Voz mejorada (ignora emojis)
@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    text = request.form['text']
    clean_text = ''.join([c for c in text if c.isalpha() or c.isspace() or c in ',.?!'])
    tts = gTTS(text=clean_text, lang='es', tld='es')
    filename = f"audio_{int(time.time())}.mp3"
    os.makedirs('static/audios', exist_ok=True)
    tts.save(f'static/audios/{filename}')
    return jsonify({'audio_url': url_for('static', filename=f'audios/{filename}')})

if __name__ == '__main__':
    app.run(debug=True)
