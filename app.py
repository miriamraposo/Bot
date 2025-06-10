# app.py
from flask import Flask, render_template, request, jsonify, url_for, session, g, send_file, make_response
from flask_cors import CORS 
from gtts import gTTS
import os
import time
import re
import sqlite3
from datetime import datetime
import json

# Para PDF
from weasyprint import HTML, CSS
import io

# Para Email
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'clave_secreta_profesional_2024'
app.config['DATABASE'] = 'nutribot.db'
app.config['UPLOAD_FOLDER'] = 'static/audios'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora de sesión

# Configuración de Flask-Mail (¡IMPORTANTE: REEMPLAZA CON TUS CREDENCIALES!)
app.config['MAIL_SERVER'] = 'smtp.gmail.com' # Por ejemplo, para Gmail
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'chatbot.nutricion.app@gmail.com' # Reemplaza con tu dirección de correo
app.config['MAIL_PASSWORD'] = 'ptbl tjxh cyjs jxvc' # Reemplaza con tu contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = 'NutriBot <chatbot.nutricion.app@gmail.com>' # Remitente visible

mail = Mail(app)

# Crear directorios necesarios
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Base de datos completa de menús con calorías
MENUS = {
    "bajar": {
        "vegetariano": {
            "items": [
                "Desayuno: Smoothie de plátano, espinaca y leche vegetal (250 kcal)",
                "Almuerzo: Ensalada de quinoa, tomate y aguacate (400 kcal)",
                "Cena: Sopa de lentejas, zanahoria y cebolla (350 kcal)",
                "Snack: Frutas mixtas, nueces y yogur natural (200 kcal)"
            ],
            "total": 1200,
            "shopping_list": ["plátano", "espinaca", "leche vegetal", "quinoa", "tomate", "aguacate", "lentejas", "zanahoria", "cebolla", "frutas mixtas", "nueces", "yogur natural"],
            "supplements": ["Proteína vegetal (1 scoop/día)", "Omega-3 (1000 mg/día)"]
        },
        "vegano": {
            "items": [
                "Desayuno: Tostadas de aguacate, tomate y semillas de chía (300 kcal)",
                "Almuerzo: Buddha bowl de arroz integral, garbanzos y pepino (450 kcal)",
                "Cena: Curry de garbanzos, calabaza y espinaca (400 kcal)",
                "Snack: Hummus con zanahorias, apio y pan integral (250 kcal)"
            ],
            "total": 1400,
            "shopping_list": ["aguacate", "tomate", "semillas de chía", "arroz integral", "garbanzos", "pepino", "calabaza", "espinaca", "hummus", "zanahorias", "apio", "pan integral"],
            "supplements": ["Vitamina B12 (1000 mcg/día)", "Hierro (18 mg/día)"]
        },
        "tradicional": {
            "items": [
                "Desayuno: Huevos, pan integral y tomate (350 kcal)",
                "Almuerzo: Pechuga de pollo, arroz y ensalada de huevo con tomate (500 kcal)",
                "Cena: Merluza, patatas y brócoli (450 kcal)",
                "Snack: Queso, galletas y fruta (300 kcal)"
            ],
            "total": 1600,
            "shopping_list": ["huevos", "pan integral", "tomate", "pechuga de pollo", "arroz", "merluza", "patatas", "brócoli", "queso", "galletas", "fruta"],
            "supplements": ["Proteína de suero (1 scoop/día)", "Creatina (5 g/día)"]
        }
    },
    "mantener": {
        "vegetariano": {
            "items": [
                "Desayuno: Frutas, avena y nueces (350 kcal)",
                "Almuerzo: Wrap de hummus, pepino y zanahoria (450 kcal)",
                "Cena: Pasta con tomate, albahaca y aceitunas (500 kcal)",
                "Snack: Yogur natural, miel y semillas de chía (300 kcal)"
            ],
            "total": 1600,
            "shopping_list": ["frutas", "avena", "nueces", "hummus", "pepino", "zanahoria", "pasta", "tomate", "albahaca", "aceitunas", "yogur natural", "miel", "semillas de chía"],
            "supplements": ["Multivitamínico (1/día)", "Magnesio (200 mg/día)"]
        },
        "vegano": {
            "items": [
                "Desayuno: Avena con plátano, semillas de chía y leche de soja (400 kcal)",
                "Almuerzo: Falafel, arroz integral y ensalada de pepino y tomate (500 kcal)",
                "Cena: Tofu, espinaca y champiñones (450 kcal)",
                "Snack: Barritas energéticas, frutos secos y fruta fresca (350 kcal)"
            ],
            "total": 1700,
            "shopping_list": ["avena", "plátano", "semillas de chía", "leche de soja", "falafel", "arroz integral", "pepino", "tomate", "tofu", "espinaca", "champiñones", "barritas energéticas", "frutos secos", "fruta fresca"],
            "supplements": ["Vitamina D3 (2000 UI/día)", "Calcio (500 mg/día)"]
        },
        "tradicional": {
            "items": [
                "Desayuno: Tostadas, huevo y aguacate (450 kcal)",
                "Almuerzo: Pescado, arroz y ensalada de col (550 kcal)",
                "Cena: Carne de res, patatas y verduras al vapor (500 kcal)",
                "Snack: Queso, jamón y fruta (350 kcal)"
            ],
            "total": 1850,
            "shopping_list": ["tostadas", "huevo", "aguacate", "pescado", "arroz", "col", "carne de res", "patatas", "verduras", "queso", "jamón", "fruta"],
            "supplements": ["Omega-3 (1000 mg/día)", "Zinc (15 mg/día)"]
        }
    },
    "aumentar": {
        "vegetariano": {
            "items": [
                "Desayuno: Batido de mango, espinaca y leche de almendra (500 kcal)",
                "Almuerzo: Lentejas, arroz y ensalada de huevo con tomate (600 kcal)",
                "Cena: Tofu salteado, brócoli y arroz integral (550 kcal)",
                "Snack: Nueces, plátano y yogur vegano (400 kcal)"
            ],
            "total": 2050,
            "shopping_list": ["mango", "espinaca", "leche de almendra", "lentejas", "arroz", "huevo", "tomate", "tofu", "brócoli", "arroz integral", "nueces", "plátano", "yogur vegano"],
            "supplements": ["Gainer (1 servicio/día)", "BCAA (5 g/día)"]
        },
        "vegano": {
            "items": [
                "Desayuno: Cereal con semillas, frutos secos y leche de avena (550 kcal)",
                "Almuerzo: Seitan, arroz, calabaza y tomate (650 kcal)",
                "Cena: Hamburguesa de legumbres, ensalada de la huerta y pan integral (600 kcal)",
                "Snack: Frutos secos, fruta fresca y barritas naturales (450 kcal)"
            ],
            "total": 2250,
            "shopping_list": ["cereal", "semillas", "frutos secos", "leche de avena", "seitan", "arroz", "calabaza", "tomate", "hamburguesa de legumbres", "ensalada", "pan integral", "fruta fresca", "barritas naturales"],
            "supplements": ["Proteína de guisante (2 scoops/día)", "Creatina vegana (5 g/día)"]
        },
        "tradicional": {
            "items": [
                "Desayuno: Tortilla, pan tostado y tomate (550 kcal)",
                "Almuerzo: Pollo, arroz, y ensalada de huevo y tomate (700 kcal)",
                "Cena: Salmón, patatas y espárragos (600 kcal)",
                "Snack: Chips de patata, queso y fruta (500 kcal)"
            ],
            "total": 2350,
            "shopping_list": ["huevos", "pan tostado", "tomate", "pollo", "arroz", "salmón", "patatas", "espárragos", "chips de patata", "queso", "fruta"],
            "supplements": ["Proteína de suero (2 scoops/día)", "Glutamina (10 g/día)"]
        }
    }
}

# Rutinas de ejercicio completas
EJERCICIOS = {
    "bajar": {
        "sedentaria": [
            "🏃‍♂️ Caminata rápida 30 min/día",
            "🧘‍♀️ Yoga 20 min (flexibilidad)",
            "🚶‍♂️ Paseos cortos cada 2 horas"
        ],
        "moderada": [
            "🚴‍♂️ Ciclismo 45 min/día",
            "🏋️‍♀️ Pesas ligeras 3x12 repeticiones",
            "🏊‍♀️ Natación 30 min 3x/semana"
        ],
        "activa": [
            "🏃‍♀️ Running 5 km 4x/semana",
            "🥊 HIIT 20 min (quema grasa)",
            "💪 Entrenamiento en circuito"
        ]
    },
    "mantener": {
        "sedentaria": [
            "🚶‍♂️ Caminata 40 min/día",
            "🤸‍♀️ Estiramientos 15 min",
            "🧘‍♂️ Yoga básico 3x/semana"
        ],
        "moderada": [
            "🏸 Deporte recreativo 1h",
            "🧗‍♂️ Escalada 30 min",
            "🏓 Tenis de mesa 45 min"
        ],
        "activa": [
            "⚽ Fútbol 1h/día",
            "🏋️‍♂️ CrossFit 45 min",
            "🏀 Baloncesto 1h 3x/semana"
        ]
    },
    "aumentar": {
        "sedentaria": [
            "🏋️‍♂️ Pesas 4x12 (3x/semana)",
            "🍗 Aumentar proteínas en dieta",
            "🚴‍♀️ Bicicleta estática 30 min"
        ],
        "moderada": [
            "💪 Gym 5x/semana (peso libre)",
            "🥗 Dieta hipercalórica controlada",
            "🏊‍♂️ Natación intensiva 45 min"
        ],
        "activa": [
            "🏆 Entrenamiento intensivo 6x/semana",
            "🥤 Suplementos proteicos",
            "🤸‍♂️ Calistenia avanzada"
        ]
    }
}

# Videos de ejercicios y recetas
VIDEO_LINKS = {
    "ejercicios": {
        "sedentaria": "https://www.youtube.com/watch?v=your_sedentary_exercise_video_id", # Placeholder, replace with actual links
        "moderada": "https://www.youtube.com/watch?v=your_moderate_exercise_video_id",
        "activa": "https://www.youtube.com/watch?v=your_active_exercise_video_id"
    },
    "recetas": {
        "vegetariano": "https://www.youtube.com/watch?v=your_vegetarian_recipe_video_id",
        "vegano": "https://www.youtube.com/watch?v=your_vegan_recipe_video_id",
        "tradicional": "https://www.youtube.com/watch?v=your_traditional_recipe_video_id"
    }
}

# Sistema de recompensas
RECOMPENSAS = {
    3: "🎉 ¡Has completado 3 planes! Obtén un 10% de descuento en suplementos con código NUTRI10",
    5: "🏆 5 planes completados! Guía de nutrición gratis al finalizar",
    7: "💎 ¡7 planes! Sesión con nutricionista gratis"
}

# Database setup
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    cur = get_db_connection().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_tables():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            contador INTEGER DEFAULT 0,
            ultima_visita TEXT,
            recompensas_obtenidas TEXT DEFAULT ''
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            fecha TEXT,
            objetivo TEXT,
            dieta TEXT,
            menu_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Llamar a create_tables al inicio de la aplicación
with app.app_context():
    create_tables()

def save_to_history(user_name, objective, diet_type, plan_data):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO historial (usuario, fecha, objetivo, dieta, menu_data) VALUES (?, ?, ?, ?, ?)',
        (user_name, datetime.now().isoformat(), objective, diet_type, json.dumps(plan_data))
    )
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        # Get JSON data from the request
        data = request.get_json() 
        user_message = data.get('message', '').lower().strip()
        step = data.get('step', '')
        
        # Ensure session variables are set before accessing
        name = session.get('name')
        age = session.get('age')
        weight = session.get('weight')
        height = session.get('height')
        activity = session.get('activity')
        goal = session.get('goal')

        if user_message == 'reiniciar' or (step == 'menu_displayed' and ('reiniciar' in user_message or 'otro plan' in user_message)):
            session.clear()
            return jsonify({
                "response": "¡Conversación reiniciada! 👋 ¿Cómo te llamas?",
                "step": "get_name",
                "reset": True,
                "speak": True,
                "show_menu": False
            })

        if "hola" in user_message and not step:
            return jsonify({
                "response": "¡Hola! 👋 Soy NutriBot, tu asistente nutricional. ¿Cómo te llamas?",
                "step": "get_name",
                "speak": True,
                "show_menu": False
            })
        
        elif step == "get_name":
            if not user_message or len(user_message) < 2:
                return jsonify({
                    "response": "Por favor, ingresa un nombre válido (mínimo 2 caracteres). ¿Cómo te llamas?",
                    "step": "get_name",
                    "speak": True
                })
                
            session['name'] = user_message.capitalize()
            db = get_db_connection()
            db.execute(
                'INSERT OR IGNORE INTO usuarios (nombre, ultima_visita) VALUES (?, ?)',
                (session['name'], datetime.now().isoformat())
            )
            db.execute(
                'UPDATE usuarios SET ultima_visita = ? WHERE nombre = ?',
                (datetime.now().isoformat(), session['name'])
            )
            db.commit()
            db.close()
            return jsonify({
                "response": f"¡Gusto en conocerte, {session['name']}! ¿Cuántos años tienes?",
                "step": "get_age",
                "speak": True
            })
        
        elif step == "get_age":
            try:
                age = int(user_message)
                if age <= 0 or age > 120:
                    return jsonify({
                        "response": "Por favor ingresa una edad válida (1-120 años)", 
                        "step": "get_age",
                        "speak": True
                    })
                session['age'] = age
                return jsonify({
                    "response": "¿Cuál es tu peso en kg?",
                    "step": "get_weight",
                    "speak": True
                })
            except ValueError:
                return jsonify({
                    "response": "Por favor ingresa un número válido para la edad", 
                    "step": "get_age",
                    "speak": True
                })
        
        elif step == "get_weight":
            try:
                weight = float(user_message)
                if weight <= 0 or weight > 300:
                    return jsonify({
                        "response": "Por favor ingresa un peso válido (1-300 kg)", 
                        "step": "get_weight",
                        "speak": True
                    })
                session['weight'] = weight
                return jsonify({
                    "response": "¿Cuál es tu altura en cm?",
                    "step": "get_height",
                    "speak": True
                })
            except ValueError:
                return jsonify({
                    "response": "Por favor ingresa un número válido para el peso", 
                    "step": "get_height",
                    "speak": True
                })
        
        elif step == "get_height":
            try:
                height = float(user_message)
                if height <= 0 or height > 250:
                    return jsonify({
                        "response": "Por favor ingresa una altura válida (1-250 cm)", 
                        "step": "get_height",
                        "speak": True
                    })
                session['height'] = height
                return jsonify({
                    "response": "¿Tu actividad diaria es sedentaria, moderada o activa?",
                    "step": "get_activity",
                    "speak": True
                })
            except ValueError:
                return jsonify({
                    "response": "Por favor ingresa un número válido para la altura", 
                    "step": "get_height",
                    "speak": True
                })
        
        elif step == "get_activity":
            activity_input = user_message.lower()
            if activity_input not in ["sedentaria", "moderada", "activa"]:
                return jsonify({
                    "response": "Elige: sedentaria, moderada o activa",
                    "step": "get_activity",
                    "speak": True
                })
            
            session['activity'] = activity_input
            weight = session.get('weight', 0)
            height = session.get('height', 0)
            
            imc_msg = ""
            if weight > 0 and height > 0:
                height_m = height / 100
                imc = weight / (height_m ** 2)
                session['imc'] = f"{imc:.1f}" # Guardar IMC en sesión
                imc_msg = f" (Tu IMC es: {session['imc']})"
            
            return jsonify({
                "response": f"¿Quieres bajar, mantener o aumentar peso?{imc_msg}",
                "step": "get_goal",
                "speak": True
            })
        
        elif step == "get_goal" and user_message in ["bajar", "mantener", "aumentar"]:
            session['goal'] = user_message
            return jsonify({
                "response": "¿Prefieres menú vegetariano, vegano o tradicional?",
                "step": "get_diet",
                "speak": True
            })
        
        elif step == "get_diet" and user_message in ["vegetariano", "vegano", "tradicional"]:
            # Ensure all required session variables are present
            required_session_vars = ['name', 'age', 'weight', 'height', 'activity', 'goal']
            if not all(k in session for k in required_session_vars):
                session.clear()
                return jsonify({
                    "response": "¡Hubo un error con la sesión! Vamos a reiniciar la conversación. ¿Cómo te llamas?",
                    "step": "get_name",
                    "speak": True,
                    "reset": True
                })
                
            goal = session.get('goal')
            diet = user_message
            activity = session.get('activity', 'moderada') # Default to 'moderada' if not found

            # Obtener datos del menú
            menu_data = MENUS.get(goal, {}).get(diet, None)
            if not menu_data:
                return jsonify({
                    "response": "Lo siento, no tengo un plan para esa combinación de objetivo y dieta. ¿Puedes probar otra?",
                    "step": "get_diet",
                    "speak": True
                })

            ejercicios = EJERCICIOS.get(goal, {}).get(activity, [])
            supplements = menu_data.get('supplements', [])
            shopping_list = menu_data.get('shopping_list', [])
            user_name = session.get('name')


            # Guardar el plan completo en la sesión para PDF/Email
            full_plan_data = {
                "name": user_name,
                "objective": goal,
                "diet": diet,
                "activity": activity,
                "menu_items": menu_data['items'],
                "total_calories": menu_data['total'],
                "supplements": supplements,
                "shopping_list": shopping_list,
                "exercise_recommendations": ejercicios,
                "video_links_ejercicios": VIDEO_LINKS["ejercicios"].get(activity),
                "video_links_recetas": VIDEO_LINKS["recetas"].get(diet),
                "imc": session.get('imc', 'N/A'), # Use 'N/A' as default
                "reward": ""
            }
            session['last_plan'] = full_plan_data # Guardar el plan completo en la sesión

            # Actualizar contador y verificar recompensas
            db = get_db_connection()
            try:
                db.execute(
                    'UPDATE usuarios SET contador = contador + 1 WHERE nombre = ?',
                    (user_name,)
                )
                db.commit() # Commit after update

                user_data = db.execute(
                    'SELECT contador, recompensas_obtenidas FROM usuarios WHERE nombre = ?',
                    (user_name,)
                ).fetchone()
                
                contador = user_data['contador']
                recompensas_obtenidas = user_data['recompensas_obtenidas'].split(',') if user_data['recompensas_obtenidas'] else []
                
                # Verificar si hay nueva recompensa
                nueva_recompensa = ""
                if contador in RECOMPENSAS and str(contador) not in recompensas_obtenidas:
                    nueva_recompensa = RECOMPENSAS[contador]
                    recompensas_obtenidas.append(str(contador))
                    db.execute(
                        'UPDATE usuarios SET recompensas_obtenidas = ? WHERE nombre = ?',
                        (','.join(recompensas_obtenidas), user_name)
                    )
                    full_plan_data['reward'] = nueva_recompensa # Añadir la recompensa al plan guardado
                
                db.commit() # Commit again if recompensas_obtenidas was updated
            except sqlite3.Error as db_error:
                db.rollback() # Rollback on error
                app.logger.error(f"Error de base de datos al actualizar usuario/recompensa: {db_error}")
                # Decide how to handle: either re-raise or send an error message
                return jsonify({
                    "response": "⚠️ Error en la base de datos al guardar tu progreso. Intenta nuevamente.",
                    "step": "menu_displayed", # Keep current step
                    "speak": True,
                    "show_menu": False
                }), 500
            finally:
                db.close()
            
            # Guardar en historial de planes del usuario (para mostrar luego)
            # This should be inside the try block for DB operations
            save_to_history(user_name, goal, diet, full_plan_data)
            
            # Construir respuesta HTML
            response_html = f"""
            <div class='menu-container'>
                <h3>🍽️ Menú {diet.capitalize()} para {goal} peso</h3>
                <ul class='menu-items'>
                    {"".join(f"<li>{item}</li>" for item in menu_data['items'])}
                </ul>
                <p class='total-calories'>Total calorías: {menu_data['total']} kcal</p>
                
                <div class='supplements-section'>
                    <h4>💊 Suplementos recomendados:</h4>
                    <ul>
                        {"".join(f"<li>{sup}</li>" for sup in supplements)}
                    </ul>
                </div>
                
                <div class='shopping-list'>
                    <h4>🛒 Lista de compras:</h4>
                    <ul>
                        {"".join(f"<li>{item}</li>" for item in shopping_list)}
                    </ul>
                </div>
                
                <div class='exercise-routine'>
                    <h4>💪 Rutina de Ejercicios ({activity.capitalize()})</h4>
                    <ul>
                        {"".join(f"<li>{ej}</li>" for ej in ejercicios)}
                    </ul>
                </div>
                
                <div class='video-links'>
                    <a href='{VIDEO_LINKS["ejercicios"].get(activity, "#")}' target='_blank' rel='noopener noreferrer' class='video-link'>
                        <i class='fas fa-dumbbell'></i> Ver rutina completa en video
                    </a>
                    <a href='{VIDEO_LINKS["recetas"].get(diet, "#")}' target='_blank' rel='noopener noreferrer' class='video-link'>
                        <i class='fas fa-utensils'></i> Ver recetas recomendadas
                    </a>
                </div>
            </div>
            """
            
            # Añadir IMC si está disponible
            if 'imc' in session:
                imc_msg = f"<div class='imc-display'><strong>Tu IMC:</strong> {session['imc']} - "
                imc_val = float(session['imc'])
                if imc_val < 18.5:
                    imc_msg += "Bajo peso</div>"
                elif 18.5 <= imc_val < 25:
                    imc_msg += "Peso normal</div>"
                elif 25 <= imc_val < 30:
                    imc_msg += "Sobrepeso</div>"
                else:
                    imc_msg += "Obesidad</div>"
                response_html += imc_msg
            
            # Añadir recompensa si corresponde
            if nueva_recompensa:
                response_html += f"<div class='recompensa'>{nueva_recompensa}</div>"
            
            return jsonify({
                "response": response_html,
                "show_menu": True,
                "speak": False,
                "step": "menu_displayed",
                "full_plan_data": response_html # Send the HTML content of the plan
            })
        
        elif step == 'menu_displayed':
            return jsonify({
                "response": "¿Hay algo más en lo que pueda ayudarte con tu plan, o quieres generar otro?",
                "step": "menu_displayed",
                "speak": True,
                "show_menu": True # Keep buttons visible if user is asking about the plan
            })

        else:
            return jsonify({
                "response": "No entendí. Por favor, dime tu nombre para comenzar, o si ya empezaste, continúa con la información solicitada.",
                "step": "get_name",
                "speak": True,
                "show_menu": False
            })
    
    except Exception as e:
        app.logger.error(f"Error general en get_response: {str(e)}")
        # It's good practice to log the full traceback for debugging
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "response": "⚠️ Error en el servidor. Por favor intenta nuevamente.",
            "step": step,
            "speak": True,
            "show_menu": False # Hide menu buttons on server error
        }), 500

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    try:
        text = request.form['text']
        clean_text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        clean_text = re.sub(r'http\S+', '', clean_text)  # Remove URLs
        clean_text = re.sub(r'[\U0001F600-\U0001F6FF]', '', clean_text) # Remove emojis
        clean_text = clean_text.strip()

        if not clean_text:
            return jsonify({'audio_url': ''})

        tts = gTTS(text=clean_text, lang='es')
        filename = f"audio_{int(time.time())}.mp3"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        tts.save(filepath)
        return jsonify({'audio_url': url_for('static', filename=f'audios/{filename}')})
    except Exception as e:
        app.logger.error(f"Error generating TTS: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_calories')
def get_calories():
    # This route is likely deprecated with the new menu display
    calories = {
        "Manzana": 52, "Pollo": 165, "Arroz": 130, "Lentejas": 116, "Tofu": 76,
        "Aguacate": 160, "Plátano": 89, "Tomate": 18, "Quinoa": 120, "Brócoli": 55,
        "Pescado": 206, "Espinaca": 23, "Nueces": 654, "Yogur": 59, "Pan integral": 247,
        "Pasta": 131, "Zanahoria": 41, "Champiñones": 22, "Hummus": 166, "Queso": 402,
        "Avena": 389, "Chía": 486, "Semillas de girasol": 584
    }
    return jsonify(calories)

@app.route('/show_history')
def show_history():
    if 'name' not in session:
        return jsonify({"error": "No hay sesión activa"}), 401

    conn = get_db_connection()
    historial = conn.execute(
        'SELECT fecha, objetivo, dieta, menu_data FROM historial WHERE usuario = ? ORDER BY fecha DESC',
        (session['name'],)
    ).fetchall()
    conn.close()

    history_list = []
    for item in historial:
        plan_data = json.loads(item['menu_data']) if item['menu_data'] else {}
        history_list.append({
            "fecha": datetime.fromisoformat(item['fecha']).strftime("%d/%m/%Y %H:%M"),
            "objetivo": item['objetivo'].capitalize(),
            "dieta": item['dieta'].capitalize(),
            "total_calories": plan_data.get('total_calories', 'N/A')
        })

    return jsonify(history_list)

# --- NUEVAS RUTAS para PDF y Email ---

@app.route('/download_plan_pdf', methods=['POST'])
def download_plan_pdf():
    data = request.get_json()
    html_content = data.get('html_content', '')
    user_name = session.get('name', 'Usuario NutriBot')

    if not html_content:
        return jsonify({'message': 'No content provided for PDF generation'}), 400

    try:
        # Estilos para el PDF (puedes copiar de tu style.css o personalizar)
        css_for_pdf = CSS(string='''
            body { font-family: 'Poppins', sans-serif; margin: 20px; color: #333; line-height: 1.6; }
            .menu-container {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #eee;
                margin-bottom: 20px;
            }
            h2, h3 { color: #4CAF50; }
            h3 { border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 15px; }
            ul { list-style-type: none; padding-left: 0; }
            li { margin-bottom: 5px; }
            p { margin-bottom: 10px; }
            .total-calories { font-weight: bold; color: #FF9800; text-align: right; margin-top: 10px; }
            .supplements-section, .shopping-list, .exercise-routine {
                background-color: #E3F2FD;
                padding: 10px;
                border-radius: 8px;
                margin: 10px 0;
            }
            .supplements-section h4, .shopping-list h4, .exercise-routine h4 {
                color: #388E3C;
                margin-bottom: 8px;
            }
            .video-links { margin-top: 15px; }
            .video-link {
                background-color: #00BCD4;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                text-decoration: none;
                display: block; /* Para que cada link ocupe su propia línea en PDF */
                margin-bottom: 5px;
            }
            .imc-display {
                background-color: #E8F5E9;
                padding: 10px;
                border-radius: 6px;
                margin-top: 10px;
                font-size: 0.9em;
            }
            .recompensa {
                background-color: #FFF9C4;
                padding: 15px;
                border-radius: 8px;
                margin-top: 15px;
                border-left: 4px solid #FF9800;
            }
        ''')

        # Incluir un encabezado para el PDF
        full_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Plan Nutricional de NutriBot para {user_name}</title>
        </head>
        <body>
            <h1>Tu Plan Nutricional de NutriBot</h1>
            <p>Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <hr>
            {html_content}
            <hr>
            <p style="text-align: center; font-size: 0.8em; color: #777;">
                Gracias por usar NutriBot. ¡Esperamos que disfrutes tu plan!
            </p>
        </body>
        </html>
        """

        pdf_file = io.BytesIO()
        HTML(string=full_html).write_pdf(pdf_file, stylesheets=[css_for_pdf])
        pdf_file.seek(0)

        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='PlanNutricional_NutriBot.pdf'
        )
    except Exception as e:
        app.logger.error(f"Error al generar PDF: {e}")
        return jsonify({'message': f'Error al generar el PDF: {str(e)}'}), 500
    
@app.route('/send_plan_email', methods=['POST'])
def send_plan_email():
    try:
        data = request.get_json()
        recipient_email = data.get('email', '')
        html_content = data.get('html_content', '')
        user_name = session.get('name', 'Usuario NutriBot')

        if not recipient_email or not html_content:
            return jsonify({'success': False, 'message': 'Faltan datos'}), 400

        subject = f"Tu Plan Nutricional Personalizado de NutriBot para {user_name}"
        msg = Message(subject, recipients=[recipient_email])
        msg.html = html_content  # Conserva todo el diseño HTML

        mail.send(msg)
        return make_response(jsonify({'success': True}), 200)
    except Exception as e:
        app.logger.error(f"Error al enviar email: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
