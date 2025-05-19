from flask import Flask, render_template, request, jsonify, url_for, session
from gtts import gTTS
import os
import time
import re
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_profesional_2024'

# Configuración profesional
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Base de datos de menús con calorías
MENUS = {
    "bajar": {
        "vegetariano": {
            "items": [
                "Desayuno: Smoothie de plátano, espinaca y leche vegetal (250 kcal)",
                "Almuerzo: Ensalada de quinoa, tomate y aguacate (380 kcal)",
                "Cena: Sopa de lentejas, zanahoria y cebolla (320 kcal)",
                "Snack: Frutas mixtas, nueces y yogur natural (200 kcal)"
            ],
            "total": 1150,
            "shopping_list": ["plátano", "espinaca", "leche vegetal", "quinoa", "tomate", "aguacate", "lentejas", "zanahoria", "cebolla", "frutas mixtas", "nueces", "yogur natural"]
        },
        "vegano": {
            "items": [
                "Desayuno: Tostadas de aguacate, tomate y semillas de chía (300 kcal)",
                "Almuerzo: Buddha bowl de arroz integral, garbanzos y pepino (400 kcal)",
                "Cena: Curry de garbanzos, calabaza y espinaca (350 kcal)",
                "Snack: Hummus con zanahorias, apio y pan integral (200 kcal)"
            ],
            "total": 1250,
            "shopping_list": ["aguacate", "tomate", "semillas de chía", "arroz integral", "garbanzos", "pepino", "calabaza", "espinaca", "hummus", "zanahorias", "apio", "pan integral"]
        },
        "tradicional": {
            "items": [
                "Desayuno: Huevos, pan integral y tomate (350 kcal)",
                "Almuerzo: Pechuga de pollo, arroz y ensalada de huevo con tomate (450 kcal)",
                "Cena: Merluza, patatas y brócoli (400 kcal)",
                "Snack: Queso, galletas y fruta (200 kcal)"
            ],
            "total": 1400,
            "shopping_list": ["huevos", "pan integral", "tomate", "pechuga de pollo", "arroz", "merluza", "patatas", "brócoli", "queso", "galletas", "fruta"]
        }
    },
    "mantener": {
        "vegetariano": {
            "items": [
                "Desayuno: Frutas, avena y nueces (400 kcal)",
                "Almuerzo: Wrap de hummus, pepino y zanahoria (450 kcal)",
                "Cena: Pasta con tomate, albahaca y aceitunas (500 kcal)",
                "Snack: Yogur natural, miel y semillas de chía (250 kcal)"
            ],
            "total": 1600,
            "shopping_list": ["frutas variadas", "avena", "nueces", "hummus", "pepino", "zanahoria", "tortillas de trigo", "pasta", "tomate", "albahaca", "aceitunas", "yogur natural", "miel", "semillas de chía"]
        },
        "vegano": {
            "items": [
                "Desayuno: Avena con plátano, semillas de chía y leche de soja (450 kcal)",
                "Almuerzo: Falafel, arroz integral y ensalada de pepino y tomate (500 kcal)",
                "Cena: Tofu, espinaca y champiñones (450 kcal)",
                "Snack: Barritas energéticas, frutos secos y fruta fresca (300 kcal)"
            ],
            "total": 1700,
            "shopping_list": ["avena", "plátano", "semillas de chía", "leche de soja", "falafel", "arroz integral", "pepino", "tomate", "tofu", "espinaca", "champiñones", "barritas energéticas", "frutos secos", "fruta fresca"]
        },
        "tradicional": {
            "items": [
                "Desayuno: Tostadas, huevo y aguacate (500 kcal)",
                "Almuerzo: Pescado, arroz y ensalada de col (550 kcal)",
                "Cena: Carne de res, patatas y verduras al vapor (600 kcal)",
                "Snack: Queso, jamón y fruta (350 kcal)"
            ],
            "total": 2000,
            "shopping_list": ["pan para tostar", "huevo", "aguacate", "pescado", "arroz", "col", "carne de res", "patatas", "verduras variadas", "queso", "jamón", "fruta"]
        }
    },
    "aumentar": {
        "vegetariano": {
            "items": [
                "Desayuno: Batido de mango, espinaca y leche de almendra (500 kcal)",
                "Almuerzo: Lentejas, arroz y ensalada de huevo con tomate (600 kcal)",
                "Cena: Tofu salteado, brócoli y arroz integral (550 kcal)",
                "Snack: Nueces, plátano y yogur vegano (450 kcal)"
            ],
            "total": 2100,
            "shopping_list": ["mango", "espinaca", "leche de almendra", "lentejas", "arroz", "huevos", "tomate", "tofu", "brócoli", "arroz integral", "nueces", "plátano", "yogur vegano"]
        },
        "vegano": {
            "items": [
                "Desayuno: Cereal con semillas, frutos secos y leche de avena (550 kcal)",
                "Almuerzo: Seitan, arroz, calabaza y tomate (650 kcal)",
                "Cena: Hamburguesa de legumbres, ensalada de la huerta y pan integral (600 kcal)",
                "Snack: Frutos secos, fruta fresca y barritas naturales (500 kcal)"
            ],
            "total": 2300,
            "shopping_list": ["cereal", "semillas variadas", "frutos secos", "leche de avena", "seitan", "arroz", "calabaza", "tomate", "hamburguesas de legumbres", "lechuga", "pan integral", "fruta fresca", "barritas naturales"]
        },
        "tradicional": {
            "items": [
                "Desayuno: Tortilla, pan tostado y tomate (600 kcal)",
                "Almuerzo: Pollo, arroz, y ensalada de huevo y tomate (700 kcal)",
                "Cena: Salmón, patatas y espárragos (650 kcal)",
                "Snack: Chips de patata, queso y fruta (500 kcal)"
            ],
            "total": 2450,
            "shopping_list": ["huevos", "pan", "tomate", "pollo", "arroz", "salmón", "patatas", "espárragos", "chips de patata", "queso", "fruta"]
        }
    }
}

# Base de datos de calorías
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

# Videos recomendados
VIDEOS = {
    "ejercicio": {
        "sedentaria": "https://www.youtube.com/watch?v=JnDu110SBN0&list=PLn7X7_tj-QEe_fUDqwJM6RIOztfV8gugb",
        "moderada": "https://www.youtube.com/watch?v=6mWHrWZBTrY&list=PLmnnJQaGYjzjiguF6UIlvSy8Cua1_ZXk4",
        "activa": "https://www.youtube.com/watch?v=TASSTvigTlA"
    },
    "receta": {
        "vegano": "https://www.youtube.com/watch?v=mzhgQQ3Kaq4",
        "vegetariano": "https://www.youtube.com/watch?v=txGhIotItgE",
        "tradicional": "https://www.youtube.com/watch?v=QZXGZVIRGoU"
    }
}

# Videos profesionales (versión mejorada)
VIDEO_LINKS = {
    "ejercicios": {
        "sedentaria": "https://www.youtube.com/watch?v=JnDu110SBN0",
        "moderada": "https://www.youtube.com/watch?v=6mWHrWZBTrY",
        "activa": "https://www.youtube.com/watch?v=TASSTvigTlA"
    },
    "recetas": {
        "vegetariano": "https://www.youtube.com/watch?v=txGhIotItgE",
        "vegano": "https://www.youtube.com/watch?v=mzhgQQ3Kaq4",
        "tradicional": "https://www.youtube.com/watch?v=QZXGZVIRGoU"
    }
}

# Rutinas de ejercicio
EJERCICIOS = {
    "bajar": {
        "sedentaria": [" Cardio 30 min/día (caminata rápida)", " Yoga 20 min (flexibilidad)"],
        "moderada": [" Ciclo 45 min/día", " Pesas ligeras 3x12"],
        "activa": [" Natación 1h/día", " HIIT 20 min (quema grasa)"]
    },
    "mantener": {
        "sedentaria": [" Caminata 40 min/día", " Estiramientos 15 min"],
        "moderada": [" Deporte recreativo 1h", " Escalada 30 min"],
        "activa": [" Fútbol 1h/día", " CrossFit 45 min"]
    },
    "aumentar": {
        "sedentaria": [" Pesas 4x12 (3x/semana)", " Aumentar proteínas en dieta"],
        "moderada": [" Gym 5x/semana", " Dieta hipercalórica"],
        "activa": [" Entrenamiento intensivo 6x/semana", " Suplementos proteicos"]
    }
}

# Suplementos con dosis recomendadas
SUPLEMENTOS = {
    "bajar": [
        " Proteína Whey: 20-30g post-entreno (ayuda a mantener masa muscular)",
        " Termogénicos: 1-2 cápsulas/día con comida (consultar con profesional)",
        " Té verde: 2-3 tazas/día o 300-400mg extracto (antioxidante)"
    ],
    "mantener": [
        " Proteína vegetal: 20-30g/día (para mantenimiento muscular)",
        " Omega-3: 1-2g/día (salud cardiovascular)",
        " Multivitamínico: 1 tableta/día con comida (según formulación)"
    ],
    "aumentar": [
        "Ganador de peso: 1-2 servicios/día (mezclar con leche o agua)",
        "Creatina: 5g/día (mejora rendimiento muscular)",
        "Carbohidratos: 0.5-1g/kg post-entreno (para recuperación)"
    ]
}

# Sistema de recompensas profesional
REWARDS = {
    3: "🎉 ¡Has planificado 3 comidas! Beneficio: Ebook de recetas saludables.",
    5: "🏆 ¡5 semanas cumpliendo el objetivo! Obtén un 20% de descuento en suplementos con el codigo PROMOS25.",
    7: "💎 ¡7 semanas cumpliendo el objetivo!Un dia de entrenamiento personla de regalo y Sesión de nutrición gratis con nuestros expertos enviando captura de pantalla al mail marketing.info@megatlon.com.ar."
}

def clean_text_for_speech(text):
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

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        user_message = request.form.get('message', '').lower().strip()
        step = request.form.get('step', '')
        
        if user_message == 'reiniciar':
            session.clear()
            return jsonify({
                "response": "¡Conversación reiniciada! 👋 ¿Cómo te llamas?",
                "step": "get_name",
                "reset": True
            })

        if "hola" in user_message and not step:
            return jsonify({
                "response": "¡Hola! 👋 Soy NutriBot, tu asistente nutricional. ¿Cómo te llamas?",
                "step": "get_name"
            })
        
        elif step == "get_name":
            session['name'] = user_message
            return jsonify({
                "response": f"¡Gusto en conocerte, {user_message.capitalize()}! ¿Cuántos años tienes?",
                "step": "get_age",
                "name": user_message
            })
        
        elif step == "get_age":
            try:
                age = int(user_message)
                if age <= 0 or age > 120:
                    return jsonify({"response": "Por favor ingresa una edad válida (1-120)", "step": step})
                session['age'] = age
                return jsonify({
                    "response": "¿Cuál es tu peso en kg?",
                    "step": "get_weight",
                    "age": age
                })
            except ValueError:
                return jsonify({"response": "Por favor ingresa un número válido para la edad", "step": step})
        
        elif step == "get_weight":
            try:
                weight = float(user_message)
                if weight <= 0 or weight > 300:
                    return jsonify({"response": "Por favor ingresa un peso válido (1-300 kg)", "step": step})
                session['weight'] = weight
                return jsonify({
                    "response": "¿Cuál es tu altura en cm?",
                    "step": "get_height",
                    "weight": weight
                })
            except ValueError:
                return jsonify({"response": "Por favor ingresa un número válido para el peso", "step": step})
        
        elif step == "get_height":
            try:
                height = float(user_message)
                if height <= 0 or height > 250:
                    return jsonify({"response": "Por favor ingresa una altura válida (1-250 cm)", "step": step})
                session['height'] = height
                return jsonify({
                    "response": "¿Tu actividad diaria es sedentaria, moderada o activa?",
                    "step": "get_activity",
                    "height": height,
                    "show_activity_question": True
                })
            except ValueError:
                return jsonify({"response": "Por favor ingresa un número válido para la altura", "step": step})
        
        elif step == "get_activity":
            activity = user_message.lower()
            if activity not in ["sedentaria", "moderada", "activa"]:
                return jsonify({"response": "Por favor elige: sedentaria, moderada o activa", "step": step})
            
            session['activity'] = activity
            weight = session.get('weight', 0)
            height = session.get('height', 0)
            
            imc_msg = ""
            if weight > 0 and height > 0:
                height_m = height / 100
                imc = weight / (height_m ** 2)
                imc_msg = f" (Tu IMC es: {imc:.1f})"
            
            return jsonify({
                "response": f"¿Quieres bajar, mantener o aumentar peso?{imc_msg}",
                "step": "get_goal",
                "activity": activity
            })
        
        elif step == "get_goal" and user_message in ["bajar", "mantener", "aumentar"]:
            session['goal'] = user_message
            return jsonify({
                "response": "¿Prefieres menú vegetariano, vegano o tradicional?",
                "step": "get_diet",
                "goal": user_message
            })
        
        elif step == "get_diet" and user_message in ["vegetariano", "vegano", "tradicional"]:
            goal = session.get('goal')
            diet = user_message
            activity = session.get('activity', 'moderada')
            menu_data = MENUS[goal][diet]
            
            # Formato mejorado del menú
            menu_html = "<div class='menu-container'>"
            menu_html += "<h4>🍽️ Menú Recomendado</h4>"
            menu_html += "<ul class='menu-items'>"
            
            for item in menu_data["items"]:
                menu_html += f"<li>{item}</li>"
            
            menu_html += f"</ul><p class='total-calories'>Total calorías: {menu_data['total']} kcal</p></div>"
            
            # Calcular IMC
            weight = session.get('weight', 0)
            height = session.get('height', 0)
            imc_msg = ""
            if weight > 0 and height > 0:
                height_m = height / 100
                imc = weight / (height_m ** 2)
                imc_msg = f"<div class='imc-display'><strong>Tu IMC:</strong> {imc:.1f} - "
                if imc < 18.5:
                    imc_msg += "Bajo peso</div>"
                elif 18.5 <= imc < 25:
                    imc_msg += "Peso normal</div>"
                elif 25 <= imc < 30:
                    imc_msg += "Sobrepeso</div>"
                else:
                    imc_msg += "Obesidad</div>"
            
            # Obtener ejercicios
            ejercicios = EJERCICIOS[goal][activity]
            ejercicios_msg = "<div class='exercise-container'><h4>💪 Rutina Recomendada</h4><ul>"
            for ejercicio in ejercicios:
                ejercicios_msg += f"<li>{ejercicio}</li>"
            ejercicios_msg += "</ul></div>"
            
            # Obtener suplementos
            suplementos = SUPLEMENTOS[goal]
            suplementos_msg = "<div class='supplements-container'><h4>✨ Suplementos Recomendados</h4><p>(consultar con profesional)</p><ul>"
            for suplemento in suplementos:
                suplementos_msg += f"<li>{suplemento}</li>"
            suplementos_msg += "</ul></div>"
            
            # Lista de compras
            shopping_list_html = "<div class='shopping-list'><h4>🛒 Lista de Compras</h4><ul>"
            for item in menu_data["shopping_list"]:
                shopping_list_html += f"<li>{item}</li>"
            shopping_list_html += "</ul></div>"
            
            # Sistema de recompensas
            meals_planned = session.get('meals_planned', 0) + 1
            session['meals_planned'] = meals_planned
            reward_msg = ""
            if meals_planned in REWARDS:
                reward_msg = f"<div class='reward-message'>{REWARDS[meals_planned]}</div>"
            
            return jsonify({
                "response": f"{menu_html}{imc_msg}{ejercicios_msg}{suplementos_msg}{shopping_list_html}{reward_msg}",
                "show_menu": True,
                "diet": diet,
                "menu_calories": menu_data['total'],
                "video_options": True,
                "exercise_video": VIDEO_LINKS["ejercicios"][activity],
                "recipe_video": VIDEO_LINKS["recetas"][diet],
                "activity": activity,
                "shopping_list": menu_data["shopping_list"]
            })
        
        elif step == "get_video_choice":
            diet = session.get('diet')
            activity = session.get('activity')
            
            if user_message in ["ejercicio", "rutina"]:
                video_url = VIDEOS["ejercicio"][activity]
                return jsonify({
                    "response": f"🎥 <strong>Video de ejercicio para nivel {activity}:</strong> <a href='{video_url}' target='_blank'>Ver rutina completa</a>"
                })
            elif user_message in ["receta", "comida"]:
                video_url = VIDEOS["receta"][diet]
                return jsonify({
                    "response": f"🍳 <strong>Video de recetas {diet}:</strong> <a href='{video_url}' target='_blank'>Ver recetas</a>"
                })
            else:
                return jsonify({
                    "response": "Opción no válida. ¿Quieres ver un video de ejercicio o de receta?"
                })
        
        else:
            return jsonify({
                "response": "No entendí. ¿Podrías repetir o decir 'reiniciar'?", 
                "step": step
            })
            
    except Exception as e:
        app.logger.error(f"Error en get_response: {str(e)}")
        return jsonify({
            "response": "⚠️ Error en el servidor. Por favor intenta nuevamente.",
            "step": step
        }), 500

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

# Nuevos endpoints para la aplicación mejorada

@app.route('/save_progress', methods=['POST'])
def save_progress():
    """Guarda el progreso del usuario en la base de datos"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            # Generar un ID único para el usuario si no existe
            user_id = f"user_{int(time.time())}"
            session['user_id'] = user_id
            
        name = session.get('name', 'Usuario')
        goal = session.get('goal', '')
        diet = session.get('diet', '')
        
        # Aquí se implementaría la lógica para guardar en la base de datos
        # Por simplicidad, solo devolvemos un mensaje de éxito
        
        return jsonify({
            "success": True,
            "message": f"Progreso de {name} guardado correctamente"
        })
    except Exception as e:
        app.logger.error(f"Error al guardar progreso: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error al guardar tu progreso"
        }), 500

@app.route('/export_plan', methods=['POST'])
def export_plan():
    """Genera un PDF o formato exportable del plan nutricional"""
    try:
        # Aquí iría la lógica para generar un PDF del plan
        # Por simplicidad, solo devolvemos un mensaje
        
        return jsonify({
            "success": True,
            "message": "Plan exportado correctamente. Revisa tu correo electrónico."
        })
    except Exception as e:
        app.logger.error(f"Error al exportar plan: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error al exportar el plan"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)