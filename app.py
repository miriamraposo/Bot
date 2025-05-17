from flask import Flask, render_template, request, jsonify, url_for
from gtts import gTTS
import os
import time
import re

app = Flask(__name__)

# Base de datos de menús (original conservado)
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
    "Manzana": 52, "Pollo": 165, "Arroz": 130,
    "Lentejas": 116, "Tofu": 76, "Aguacate": 160,
    "Plátano": 89, "Tomate": 18, "Quinoa": 120,
    "Brócoli": 55, "Pescado": 206, "Espinaca": 23,
    "Nueces": 654, "Yogur": 59, "Pan integral": 247,
    "Pasta": 131, "Zanahoria": 41, "Champiñones": 22,
    "Hummus": 166, "Queso": 402, "Avena": 389,
    "Chía": 486, "Semillas de girasol": 584
}

# Fase 1: Suplementos
SUPLEMENTOS = {
    "bajar": "🔹 Proteínas en polvo para saciedad, BCAA en ayunas.",
    "aumentar": "🔹 Creatina (5g/día), proteína en polvo y carbohidratos post-entreno.",
    "mantener": "🔹 Multivitamínico, omega-3 y proteínas para mantener la salud."
}

# Fase 2: Ingredientes
INGREDIENTES_BASE = {
    "smoothie": ["plátano", "espinaca", "leche vegetal"],
    "ensalada": ["quinoa", "tomate", "aguacate"],
    "sopa": ["lentejas", "zanahoria", "cebolla"],
    "huevos": ["huevos", "pan integral", "tomate"],
    "tofu": ["tofu", "brócoli", "arroz integral"],
    "pollo": ["pollo", "arroz", "ensalada"],
    "pescado": ["merluza", "patatas", "brócoli"],
    "pasta": ["pasta", "tomate", "albahaca"],
    "wrap": ["pan integral", "hummus", "pepino"],
    "batido": ["mango", "espinaca", "leche de almendra"]
}

# Fase 3: Ejercicios
EJERCICIOS = {
    "bajar": [
        "🏃‍♂️ Cardio 30-45 min (3-4x/semana)",
        "🤸‍♀️ HIIT 20 min (2x/semana)",
        "🧘‍♀️ Yoga para flexibilidad (1x/semana)"
    ],
    "aumentar": [
        "🏋️‍♂️ Pesas 4x12 rep (4x/semana)",
        "🦵 Descansos 90s entre series",
        "💪 Ejercicios compuestos (sentadilla, press banca)"
    ],
    "mantener": [
        "🚴‍♂️ Ciclo 30 min (3x/semana)",
        "🏊‍♀️ Natación 45 min (2x/semana)",
        "🤸‍♂️ Entrenamiento funcional (2x/semana)"
    ]
}

def clean_text_for_speech(text):
    """Elimina emojis y tags HTML para el texto a voz"""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # símbolos & pictogramas
        u"\U0001F680-\U0001F6FF"  # transporte & símbolos
        u"\U0001F1E0-\U0001F1FF"  # banderas (iOS)
                           "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

@app.route('/')
def home():
    return render_template('index.html')

# Fase 2: Lista de compra
@app.route('/get_shopping_list', methods=['POST'])
def get_shopping_list():
    goal = request.form['goal']
    diet = request.form['diet']
    items = set()
    
    for meal in MENUS[goal][diet]:
        for keyword, ingredientes in INGREDIENTES_BASE.items():
            if keyword in meal.lower():
                items.update(ingredientes)
    
    return jsonify({"items": list(items)})

# Fase 2: Análisis de comidas
def analyze_meal(meal_desc):
    meal_desc = meal_desc.lower()
    tips = []
    
    if "frito" in meal_desc or "empanizado" in meal_desc:
        tips.append("🔹 Considera cocinar al horno o vapor en lugar de frito.")
    if "arroz" in meal_desc or "pasta" in meal_desc:
        tips.append("🔹 Controla las porciones de carbohidratos (1 taza cocida aprox).")
    if "verduras" not in meal_desc and "ensalada" not in meal_desc:
        tips.append("🔹 Añade verduras para aumentar fibra y nutrientes.")
    if not tips:
        tips.append("🔹 ¡Buena elección! Equilibra con proteínas y verduras.")
    
    return "🍽️ <strong>Análisis nutricional:</strong><br>" + "<br>".join(tips)

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form.get('message', '').lower().strip()
    step = request.form.get('step', '')
    
    if user_message == 'reiniciar':
        return {
            "response": "¡Conversación reiniciada! 👋 ¿Cómo te llamas?",
            "step": "get_name",
            "reset": True
        }

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
        
        if weight > 0:
            if goal == "bajar":
                protein = weight * 1.6
                carbs = weight * 1.5
            elif goal == "aumentar":
                protein = weight * 2.2
                carbs = weight * 3
            else:
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
        
        # Fase 3: Añadir ejercicios
        ejercicios_msg = (
            f"🏋️‍♂️ <strong>Rutina recomendada:</strong><br>" + 
            "<br>".join(EJERCICIOS.get(goal, [])) + "<br><br>"
        )
        
        return {
            "response": (
                f"🍽️ <strong>Menú recomendado:</strong><br>" + "<br>".join(menu) + 
                f"<br><br>{imc_message}<br>{ejercicios_msg}{macros_msg}"
            ),
            "show_menu": True,
            "diet": user_message,
            "goal": goal  # Para recompensas
        }
    
    # Fase 2: Análisis de comidas
    elif "analizar comida" in user_message:
        return {
            "response": "Describe tu plato principal (ej: 'ensalada de quinoa con pollo')",
            "step": "analyze_meal"
        }
    elif step == "analyze_meal":
        return {
            "response": analyze_meal(user_message),
            "step": step
        }
    
    else:
        return {"response": "No entendí. ¿Podrías repetir o decir 'reiniciar'?", "step": step}

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
