from flask import Flask, render_template, request, jsonify, url_for, session
from gtts import gTTS
import os
import time
import re
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_profesional_2024'
app.config['DATABASE'] = 'nutribot.db'
app.config['UPLOAD_FOLDER'] = 'static/audios'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora de sesión

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
            "suplementos": ["Proteína vegetal (1 scoop/día)", "Omega-3 (1000 mg/día)"]
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
            "suplementos": ["Vitamina B12 (1000 mcg/día)", "Hierro (18 mg/día)"]
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
            "suplementos": ["Proteína de suero (1 scoop/día)", "Creatina (5 g/día)"]
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
            "suplementos": ["Multivitamínico (1/día)", "Magnesio (200 mg/día)"]
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
            "suplementos": ["Vitamina D3 (2000 UI/día)", "Calcio (500 mg/día)"]
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
            "suplementos": ["Omega-3 (1000 mg/día)", "Zinc (15 mg/día)"]
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
            "suplementos": ["Gainer (1 servicio/día)", "BCAA (5 g/día)"]
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
            "suplementos": ["Proteína de guisante (2 scoops/día)", "Creatina vegana (5 g/día)"]
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
            "suplementos": ["Proteína de suero (2 scoops/día)", "Glutamina (10 g/día)"]
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

# Sistema de recompensas
RECOMPENSAS = {
    3: "🎉 ¡Has completado 3 planes! Obtén un 10% de descuento en suplementos con código NUTRI10",
    5: "🏆 5 planes completados! Guía de nutrición gratis al finalizar",
    7: "💎 ¡7 planes! Sesión con nutricionista gratis"
}

# Database setup
def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                contador INTEGER DEFAULT 0,
                ultima_visita TEXT,
                recompensas_obtenidas TEXT DEFAULT ''
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                fecha TEXT,
                objetivo TEXT,
                dieta TEXT,
                menu TEXT,
                lista_compra TEXT,
                suplementos TEXT,
                ejercicios TEXT
            )
        ''')
        db.commit()

@app.route('/')
def home():
    init_db()
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
                "reset": True,
                "speak": True
            })

        if "hola" in user_message and not step:
            return jsonify({
                "response": "¡Hola! 👋 Soy NutriBot, tu asistente nutricional. ¿Cómo te llamas?",
                "step": "get_name",
                "speak": True
            })
        
        elif step == "get_name":
            if not user_message or len(user_message) < 2:
                return jsonify({
                    "response": "Por favor, ingresa un nombre válido (mínimo 2 caracteres). ¿Cómo te llamas?",
                    "step": "get_name",
                    "speak": True
                })
                
            session['name'] = user_message
            db = get_db()
            db.execute(
                'INSERT OR IGNORE INTO usuarios (nombre, ultima_visita) VALUES (?, ?)',
                (user_message, datetime.now().isoformat())
            )
            db.execute(
                'UPDATE usuarios SET ultima_visita = ? WHERE nombre = ?',
                (datetime.now().isoformat(), user_message)
            )
            db.commit()
            return jsonify({
                "response": f"¡Gusto en conocerte, {user_message.capitalize()}! ¿Cuántos años tienes?",
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
                    "step": "get_weight",
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
            activity = user_message.lower()
            if activity not in ["sedentaria", "moderada", "activa"]:
                return jsonify({
                    "response": "Elige: sedentaria, moderada o activa", 
                    "step": "get_activity",
                    "speak": True
                })
            
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
                "speak": True
            })
        
        elif user_message in ["bajar", "mantener", "aumentar"]:
            session['goal'] = user_message
            return jsonify({
                "response": "¿Prefieres menú vegetariano, vegano o tradicional?",
                "step": "get_diet",
                "speak": True
            })
        
        elif user_message in ["vegetariano", "vegano", "tradicional"]:
            if 'goal' not in session or 'activity' not in session:
                session.clear()
                return jsonify({
                    "response": "¡Hubo un error! Vamos a reiniciar la conversación. ¿Cómo te llamas?",
                    "step": "get_name",
                    "speak": True
                })
                
            goal = session.get('goal')
            diet = user_message
            activity = session.get('activity', 'moderada')
            
            # Actualizar contador y verificar recompensas
            db = get_db()
            db.execute(
                'UPDATE usuarios SET contador = contador + 1 WHERE nombre = ?',
                (session['name'],)
            )
            
            user_data = db.execute(
                'SELECT contador, recompensas_obtenidas FROM usuarios WHERE nombre = ?',
                (session['name'],)
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
                    (','.join(recompensas_obtenidas), session['name'])
                )
            
            # Obtener datos del menú
            menu_data = MENUS[goal][diet]
            ejercicios = EJERCICIOS[goal][activity]
            suplementos = menu_data['suplementos']
            
            # Guardar en historial
            db.execute(
                '''INSERT INTO historial (
                    usuario, fecha, objetivo, dieta, menu, lista_compra, suplementos, ejercicios
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    session['name'],
                    datetime.now().isoformat(),
                    goal,
                    diet,
                    str(menu_data['items']),
                    str(menu_data['shopping_list']),
                    str(suplementos),
                    str(ejercicios)
                )
            )
            db.commit()
            
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
                        {"".join(f"<li>{sup}</li>" for sup in suplementos)}
                    </ul>
                </div>
                
                <div class='shopping-list'>
                    <h4>🛒 Lista de compras:</h4>
                    <ul>
                        {"".join(f"<li>{item}</li>" for item in menu_data['shopping_list'])}
                    </ul>
                </div>
                
                <div class='exercise-routine'>
                    <h4>💪 Rutina de Ejercicios ({activity.capitalize()})</h4>
                    <ul>
                        {"".join(f"<li>{ej}</li>" for ej in ejercicios)}
                    </ul>
                </div>
                
                <div class='video-links'>
                    <a href='{VIDEO_LINKS["ejercicios"][activity]}' target='_blank' rel='noopener noreferrer' class='video-link'>
                        <i class='fas fa-dumbbell'></i> Ver rutina completa en video
                    </a>
                    <a href='{VIDEO_LINKS["recetas"][diet]}' target='_blank' rel='noopener noreferrer' class='video-link'>
                        <i class='fas fa-utensils'></i> Ver recetas recomendadas
                    </a>
                </div>
            </div>
            """
            
            # Añadir IMC si está disponible
            weight = session.get('weight', 0)
            height = session.get('height', 0)
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
                response_html += imc_msg
            
            # Añadir recompensa si corresponde
            if nueva_recompensa:
                response_html += f"<div class='recompensa'>{nueva_recompensa}</div>"
            
            return jsonify({
                "response": response_html,
                "show_menu": True,
                "diet": diet,
                "contador": contador,
                "recompensa": nueva_recompensa,
                "speak": False
            })
        
        else:
            return jsonify({
                "response": "No entendí. ¿Podrías repetir o decir 'reiniciar'?",
                "step": step,
                "speak": True
            })
    
    except Exception as e:
        app.logger.error(f"Error en get_response: {str(e)}")
        return jsonify({
            "response": "⚠️ Error en el servidor. Por favor intenta nuevamente.",
            "step": step,
            "speak": True
        }), 500

@app.route('/get_calories')
def get_calories():
    calories = {
        "Manzana": 52, "Pollo": 165, "Arroz": 130, "Lentejas": 116, "Tofu": 76,
        "Aguacate": 160, "Plátano": 89, "Tomate": 18, "Quinoa": 120, "Brócoli": 55,
        "Pescado": 206, "Espinaca": 23, "Nueces": 654, "Yogur": 59, "Pan integral": 247,
        "Pasta": 131, "Zanahoria": 41, "Champiñones": 22, "Hummus": 166, "Queso": 402,
        "Avena": 389, "Chía": 486, "Semillas de girasol": 584
    }
    return jsonify(calories)

@app.route('/get_history')
def get_history():
    if 'name' not in session:
        return jsonify({"error": "No hay sesión activa"}), 401
    
    db = get_db()
    historial = db.execute(
        'SELECT fecha, objetivo, dieta FROM historial WHERE usuario = ? ORDER BY fecha DESC',
        (session['name'],)
    ).fetchall()
    
    history_list = []
    for item in historial:
        history_list.append({
            "fecha": datetime.fromisoformat(item['fecha']).strftime("%d/%m/%Y %H:%M"),
            "objetivo": item['objetivo'].capitalize(),
            "dieta": item['dieta'].capitalize()
        })
    
    return jsonify(history_list)

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    try:
        text = request.form['text']
        clean_text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        clean_text = re.sub(r'http\S+', '', clean_text)  # Remove URLs
        clean_text = re.sub(r'[\U0001F600-\U0001F6FF]', '', clean_text)  # Remove emojis
        clean_text = clean_text.strip()
        
        if not clean_text:
            return jsonify({'audio_url': ''})
        
        tts = gTTS(text=clean_text, lang='es')
        filename = f"audio_{int(time.time())}.mp3"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        tts.save(filepath)
        
        return jsonify({'audio_url': url_for('static', filename=f'audios/{filename}')})
    
    except Exception as e:
        app.logger.error(f"Error en text_to_speech: {str(e)}")
        return jsonify({'audio_url': ''}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)