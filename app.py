from flask import Flask, render_template, request, jsonify, url_for
from gtts import gTTS
import os
import time
import re

app = Flask(__name__)

# Base de datos de menús
MENUS = {
    "bajar": {
        "vegetariano": [
            "Desayuno: Smoothie de espinaca y plátano 🥤",
            "Almuerzo: Ensalada de quinoa y aguacate 🥗",
            "Cena: Sopas de lentejas y verduras 🍲",
            "Snack: Palitos de zanahoria y hummus 🥕"
        ],
        "vegano": [
            "Desayuno: Tostadas con aguacate y tomate 🥑🍅",
            "Almuerzo: Buddha bowl con tofu y vegetales 🌱",
            "Cena: Curry de garbanzos y espinacas 🍛",
            "Snack: Frutos secos y semillas 🌰"
        ],
        "tradicional": [
            "Desayuno: Huevos revueltos con tomate y pan 🍳",
            "Almuerzo: Pechuga de pollo a la parrilla 🍗",
            "Cena: Merluza al horno con verduras 🐟",
            "Snack: Yogurt natural con fruta 🍓"
        ]
    },
    "mantener": {
        "vegetariano": [
            "Desayuno: Frutas frescas y yogurt 🍓",
            "Almuerzo: Wrap de hummus con verduras 🥙",
            "Cena: Pasta con pesto y tomate 🍝",
            "Snack: Manzana con mantequilla de maní 🍏🥜"
        ],
        "vegano": [
            "Desayuno: Avena con frutas y semillas 🥣",
            "Almuerzo: Falafel con ensalada y pan pita 🌯",
            "Cena: Salteado de tofu y vegetales 🍜",
            "Snack: Batido de banana y espinaca 🍌"
        ],
        "tradicional": [
            "Desayuno: Tostadas integrales y mermelada 🍞",
            "Almuerzo: Pescado a la plancha con limón 🐠",
            "Cena: Roast de carne magra 🥩",
            "Snack: Barras de cereal caseras 🍫"
        ]
    },
    "aumentar": {
        "vegetariano": [
            "Desayuno: Batido de mango y espinaca 🥭",
            "Almuerzo: Lentejas con verduras y arroz 🥘",
            "Cena: Tofu marinado y salteado 🍳",
            "Snack: Chips de kale al horno 🥬"
        ],
        "vegano": [
            "Desayuno: Pudding de chía y fruta 🍮",
            "Almuerzo: Seitan con salsa barbacoa 🌭",
            "Cena: Hamburguesa vegana con guarniciones 🍔",
            "Snack: Fruta fresca y nueces 🥭🌰"
        ],
        "tradicional": [
            "Desayuno: Tortilla de espinaca y queso 🥚",
            "Almuerzo: Pollo asado con hierbas 🍗",
            "Cena: Salmón a la plancha con puré 🐟",
            "Snack: Queso y embutidos en pequeñas porciones 🧀"
        ]
    }
}

CALORIAS = {
    "Manzana": 52,
    "Plátano": 89,
    "Naranja": 47,
    "Fresa": 32,
    "Pera": 57,
    "Pollo": 165,
    "Carne de res": 250,
    "Pescado": 206,
    "Huevos": 68,
    "Arroz blanco": 130,
    "Arroz integral": 111,
    "Lentejas": 116,
    "Garbanzos": 164,
    "Tofu": 76,
    "Aguacate": 160,
    "Queso mozzarella": 280,
    "Yogur natural": 59,
    "Pan integral": 247,
    "Almendras": 579,
    "Cacahuetes": 567,
    "Aceite de oliva": 119,
    "Cacao puro en polvo": 228,
    "Chía": 486,
    "Semillas de girasol": 585,
    "Zanahoria": 41,
    "Brócoli": 55,
    "Espinaca": 23,
    "Pepino": 16,
    "Tomate": 18,
    "Papas": 77,
    "Batata": 86
}

def clean_text_for_speech(text):
    """Elimina emojis y tags HTML para el texto a voz"""
    # Eliminar emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # símbolos & pictogramas
        u"\U0001F680-\U0001F6FF"  # transporte & símbolos
        u"\U0001F1E0-\U0001F1FF"  # banderas (iOS)
                           "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    # Eliminar tags HTML
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form.get('message', '').lower().strip()
    step = request.form.get('step', '')
    
    # Manejar reinicio de conversación
    if user_message == 'reiniciar':
        return {
            "response": "¡Conversación reiniciada! 👋 ¿Cómo te llamas?",
            "step": "get_name",
            "reset": True
        }

    # Flujo de conversación
    if "hola" in user_message and not step:
        return {
            "response": "¡Hola! 👋 ¿Cómo te llamas?",
            "step": "get_name"
        }
    
    elif step == "get_name":
        return {
            "response": f"¡Gusto en conocerte, {user_message.capitalize()}! ¿Cuántos años tienes?",
            "step": "get_age",
            "name": user_message
        }
    
    elif step == "get_age":
        try:
            age = int(user_message)
            if age <= 0 or age > 120:
                return {"response": "Por favor ingresa una edad válida (1-120)"}
            return {
                "response": "¿Cuál es tu peso en kg? ",
                "step": "get_weight",
                "age": user_message
            }
        except ValueError:
            return {"response": "Por favor ingresa un número válido para la edad"}
    
    elif step == "get_weight":
        try:
            weight = float(user_message)
            if weight <= 0 or weight > 300:
                return {"response": "Por favor ingresa un peso válido (1-300 kg)"}
            return {
                "response": "¿Cuál es tu altura en cm?",
                "step": "get_height",
                "weight": user_message
            }
        except ValueError:
            return {"response": "Por favor ingresa un número válido para el peso"}
    
    elif step == "get_height":
        try:
            height = float(user_message)
            if height <= 0 or height > 250:
                return {"response": "Por favor ingresa una altura válida (1-250 cm)"}
            
            # Calcular IMC si tenemos peso y altura
            weight = float(request.form.get('weight', 0))
            if weight > 0:
                height_m = height / 100
                imc = weight / (height_m ** 2)
                imc_message = f" (Tu IMC es: {imc:.1f})"
            else:
                imc_message = ""
                
            return {
                "response": f"¿Quieres bajar, mantener o aumentar peso?{imc_message}",
                "step": "get_goal",
                "height": user_message
            }
        except ValueError:
            return {"response": "Por favor ingresa un número válido para la altura"}
    
    elif user_message in ["bajar", "mantener", "aumentar"]:
        return {
            "response": "¿Prefieres menú vegetariano, vegano o tradicional?",
            "step": "get_diet",
            "goal": user_message
        }
    
    elif user_message in ["vegetariano", "vegano", "tradicional"]:
        goal = request.form.get('goal')
        menu = MENUS[goal][user_message]
        
        # Calcular IMC para mostrarlo con el menú
        weight = float(request.form.get('weight', 0))
        height = float(request.form.get('height', 0))
        if weight > 0 and height > 0:
            height_m = height / 100
            imc = weight / (height_m ** 2)
            imc_message = f"<div class='imc-display'><strong>Tu IMC:</strong> {imc:.1f} - "
            if imc < 18.5:
                imc_message += "Bajo peso</div>"
            elif 18.5 <= imc < 25:
                imc_message += "Peso normal</div>"
            elif 25 <= imc < 30:
                imc_message += "Sobrepeso</div>"
            else:
                imc_message += "Obesidad</div>"
        else:
            imc_message = ""
            
        return {
            "response": f"🍽️ <strong>Menú recomendado:</strong><br>" + "<br>".join(menu) + "<br><br>" + imc_message,
            "show_menu": True,
            "diet": user_message
        }
    
    else:
        return {"response": "No entendí. ¿Podrías repetir o decir 'reiniciar' para comenzar de nuevo?"}

@app.route('/get_calories')
def get_calories():
    return jsonify(CALORIAS)

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    text = request.form['text']
    clean_text = clean_text_for_speech(text)
    if not clean_text:
        return jsonify({'audio_url': ''})
    
    tts = gTTS(text=clean_text, lang='es')
    filename = f"audio_{int(time.time())}.mp3"
    os.makedirs('static/audios', exist_ok=True)
    tts.save(f'static/audios/{filename}')
    return jsonify({'audio_url': url_for('static', filename=f'audios/{filename}')})

if __name__ == '__main__':
    app.run(debug=True)
