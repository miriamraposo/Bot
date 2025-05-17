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
            "Desayuno: Smoothie de plátano, espinaca y leche vegetal ",
            "Almuerzo: Ensalada de quinoa, tomate y aguacate ",
            "Cena: Sopa de lentejas, zanahoria y cebolla ",
            "Snack: Frutas mixtas, nueces y yogur natural "
        ],
        "vegano": [
            "Desayuno: Tostadas de aguacate, tomate y semillas de chía ",
            "Almuerzo: Buddha bowl de arroz integral, garbanzos y pepino ",
            "Cena: Curry de garbanzos, calabaza y espinaca ",
            "Snack: Hummus con zanahorias, apio y pan integral "
        ],
        "tradicional": [
            "Desayuno: Huevos, pan integral y tomate ",
            "Almuerzo: Pechuga de pollo, arroz y ensalada de huevo con tomate ",
            "Cena: Merluza, patatas y brócoli ",
            "Snack: Queso, galletas y fruta "
        ]
    },
    "mantener": {
        "vegetariano": [
            "Desayuno: Frutas, avena y nueces ",
            "Almuerzo: Wrap de hummus, pepino y zanahoria ",
            "Cena: Pasta con tomate, albahaca y aceitunas ",
            "Snack: Yogur natural, miel y semillas de chía "
        ],
        "vegano": [
            "Desayuno: Avena con plátano, semillas de chía y leche de soja ",
            "Almuerzo: Falafel, arroz integral y ensalada de pepino y tomate ",
            "Cena: Tofu, espinaca y champiñones ",
            "Snack: Barritas energéticas, frutos secos y fruta fresca "
        ],
        "tradicional": [
            "Desayuno: Tostadas, huevo y aguacate ",
            "Almuerzo: Pescado, arroz y ensalada de col ",
            "Cena: Carne de res, patatas y verduras al vapor ",
            "Snack: Queso, jamón y fruta "
        ]
    },
    "aumentar": {
        "vegetariano": [
            "Desayuno: Batido de mango, espinaca y leche de almendra ",
            "Almuerzo: Lentejas, arroz y ensalada de huevo con tomate ",
            "Cena: Tofu salteado, brócoli y arroz integral ",
            "Snack: Nueces, plátano y yogur vegano "
        ],
        "vegano": [
            "Desayuno: Cereal con semillas, frutos secos y leche de avena ",
            "Almuerzo: Seitan, arroz, calabaza y tomate ",
            "Cena: Hamburguesa de legumbres, ensalada de la huerta y pan integral ",
            "Snack: Frutos secos, fruta fresca y barritas naturales "
        ],
        "tradicional": [
            "Desayuno: Tortilla, pan tostado y tomate ",
            "Almuerzo: Pollo, arroz, y ensalada de huevo y tomate ",
            "Cena: Salmón, patatas y espárragos ",
            "Snack: Chips de patata, queso y fruta "
        ]
    }
}

CALORIAS = {
    "Manzana": 52,
    "Pollo": 165,
    "Arroz": 130,
    "Lentejas": 116,
    "Tofu": 76,
    "Aguacate": 160,
    "Plátano": 89,
    "Tomate": 18,
    "Quinoa": 120,
    "Brócoli": 55,
    "Pescado": 206,
    "Espinaca": 23,
    "Nueces": 654,
    "Yogur": 59,
    "Pan integral": 247,
    "Pasta": 131,
    "Zanahoria": 41,
    "Champiñones": 22,
    "Hummus": 166,
    "Queso": 402,
    "Avena": 389,
    "Chía": 486,
    "Semillas de girasol": 584
}

# Nuevo: Base de datos de suplementos (Fase 1)
SUPLEMENTOS = {
    "bajar": "🔹 Proteínas en polvo para saciedad, BCAA en ayunas.",
    "aumentar": "🔹 Creatina (5g/día), proteína en polvo y carbohidratos post-entreno para aumentar masa muscular.",
    "mantener": "🔹 Multivitamínico, omega-3 y proteínas para mantener la salud y la masa muscular."
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
                return {"response": "Por favor ingresa una edad válida (1-120)", "step": step}
            return {
                "response": "¿Cuál es tu peso en kg? ",
                "step": "get_weight",
                "age": user_message
            }
        except ValueError:
            return {"response": "Por favor ingresa un número válido para la edad", "step": step}
    
    elif step == "get_weight":
        try:
            weight = float(user_message)
            if weight <= 0 or weight > 300:
                return {"response": "Por favor ingresa un peso válido (1-300 kg)", "step": step}
            return {
                "response": "¿Cuál es tu altura en cm? ",
                "step": "get_height",
                "weight": user_message
            }
        except ValueError:
            return {"response": "Por favor ingresa un número válido para el peso", "step": step}
    
    elif step == "get_height":
        try:
            height = float(user_message)
            if height <= 0 or height > 250:
                return {"response": "Por favor ingresa una altura válida (1-250 cm)", "step": step}
            
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
            return {"response": "Por favor ingresa un número válido para la altura", "step": step}
    
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
        
        # Nuevo: Cálculo de macronutrientes (Fase 1)
        if weight > 0:
            if goal == "bajar":
                protein = weight * 1.6
                carbs = weight * 1.5
            elif goal == "aumentar":
                protein = weight * 2.2
                carbs = weight * 3
            else:  # mantener
                protein = weight * 1.8
                carbs = weight * 2.2
            fat = weight * 0.8
            
            macros_msg = (
                f"📊 <strong>Macros diarios (aprox):</strong><br>"
                f"Proteína: {protein:.1f}g<br>"
                f"Carbohidratos: {carbs:.1f}g<br>"
                f"Grasas: {fat:.1f}g<br>"
                f"💧 Toma al menos {int(weight * 35)}ml de agua al día<br><br>"
                f"{SUPLEMENTOS.get(goal, '')}"
            )
        else:
            macros_msg = ""
            
        return {
            "response": (
                f"🍽️ <strong>Menú recomendado:</strong><br>" + "<br>".join(menu) + 
                f"<br><br>{imc_message}<br>{macros_msg}"
            ),
            "show_menu": True,
            "diet": user_message
        }
    
    else:
        return {"response": "No entendí. ¿Podrías repetir o decir 'reiniciar' para comenzar de nuevo?", "step": step}

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
