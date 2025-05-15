from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

app = Flask(__name__)
app.secret_key = "clave_secreta"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Lógica del chatbot
def procesar_input(user_input):
    datos = session.get("datos", {})
    respuesta = ""

    if "alimentacion" not in datos:
        opciones = {"1": "Omnívoro", "2": "Vegetariano", "3": "Vegano", "4": "Otro"}
        if user_input in opciones:
            datos["alimentacion"] = opciones[user_input]
            respuesta = "¿Cuál es tu objetivo?\n1. Bajar de peso\n2. Mantener peso\n3. Ganar masa muscular 💪"
        else:
            respuesta = "¿Cuál es tu tipo de alimentación?\n1. Omnívoro 🍗\n2. Vegetariano 🥗\n3. Vegano 🌱\n4. Otro 🍽️"
    elif "objetivo" not in datos:
        objetivos = {"1": "Bajar de peso", "2": "Mantener peso", "3": "Ganar masa muscular"}
        if user_input in objetivos:
            datos["objetivo"] = objetivos[user_input]
            respuesta = "¿Sos una persona activa o sedentaria?\n1. Activa 🏃\n2. Sedentaria 🛋️"
        else:
            respuesta = "¿Cuál es tu objetivo?\n1. Bajar de peso\n2. Mantener peso\n3. Ganar masa muscular 💪"
    elif "actividad" not in datos:
        actividad = {"1": "Activa", "2": "Sedentaria"}
        if user_input in actividad:
            datos["actividad"] = actividad[user_input]
            respuesta = "¿Querés recibir recomendaciones de menú? (Sí o No)"
        else:
            respuesta = "¿Sos una persona activa o sedentaria?\n1. Activa 🏃\n2. Sedentaria 🛋️"
    elif "recomendar" not in datos:
        if user_input.lower() in ["sí", "si"]:
            datos["recomendar"] = "Sí"
            respuesta = generar_menu(datos)
        elif user_input.lower() == "no":
            datos["recomendar"] = "No"
            respuesta = "¡Perfecto! Podés consultarme cuando quieras 💬"
        else:
            respuesta = "¿Querés recibir recomendaciones de menú? (Sí o No)"
    else:
        respuesta = "Si querés volver a empezar, hacé clic en 'Reiniciar conversación 🔄'"

    session["datos"] = datos
    return respuesta


def generar_menu(datos):
    tipo = datos.get("alimentacion", "Omnívoro")
    objetivo = datos.get("objetivo", "Mantener peso")
    actividad = datos.get("actividad", "Activa")

    menu = f"🍽️ Menú recomendado para vos ({tipo}, {objetivo}, {actividad}):\n\n"

    if tipo == "Omnívoro":
        if objetivo == "Bajar de peso":
            menu += "🥣 Desayuno: Yogur descremado con granola y frutas 🍓\n"
            menu += "🥗 Almuerzo: Ensalada con pollo a la plancha y arroz integral 🍚\n"
            menu += "🍎 Merienda: Licuado de frutas con avena 🥤\n"
            menu += "🍽️ Cena: Sopa de verduras + pescado grillado con puré de calabaza 🐟"
        elif objetivo == "Ganar masa muscular":
            menu += "🍳 Desayuno: Omelette con espinaca y queso + 2 tostadas 🥚\n"
            menu += "🥩 Almuerzo: Carne magra con arroz integral y ensalada 🥗\n"
            menu += "🍌 Merienda: Batido de banana con leche y nueces 🥜\n"
            menu += "🍝 Cena: Pasta integral con atún + vegetales al vapor 🥦"
        else:
            menu += "🍞 Desayuno: Tostadas integrales con palta y huevo 🍳\n"
            menu += "🍗 Almuerzo: Pollo al horno con puré mixto y ensalada 🥬\n"
            menu += "🍉 Merienda: Fruta fresca y yogur natural 🍎\n"
            menu += "🍽️ Cena: Omelette con vegetales + arroz integral 🍚"

    elif tipo == "Vegetariano":
        menu += "🍞 Desayuno: Pan integral con mermelada natural y frutas 🍊\n"
        menu += "🥙 Almuerzo: Tarta de vegetales con ensalada completa 🥬\n"
        menu += "🥛 Merienda: Yogur con cereales y semillas 🌻\n"
        menu += "🍛 Cena: Guiso de lentejas con arroz y verduras 🥕"

    elif tipo == "Vegano":
        menu += "🍌 Desayuno: Porridge de avena con banana y chia 🌾\n"
        menu += "🥗 Almuerzo: Ensalada de quinoa, garbanzos y vegetales 🥒\n"
        menu += "🍎 Merienda: Frutas frescas y frutos secos 🥜\n"
        menu += "🍝 Cena: Pasta integral con salsa de tomate natural y tofu 🍅"

    else:
        menu += "📝 Por favor especificá más detalles para poder darte un menú adecuado."

    menu += "\n\n🔍 Si querés ver una tabla de calorías, presioná el botón correspondiente al final 💡"
    return menu

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_input = request.form["user_input"]
    respuesta = procesar_input(user_input)
    return jsonify({"message": respuesta})

@app.route("/reiniciar", methods=["POST"])
def reiniciar():
    session.pop("datos", None)
    return jsonify({"message": "✅ Conversación reiniciada. ¡Hola! Soy 🤖 Nutribot, tu asistente nutricional.\n¿Cuál es tu tipo de alimentación?\n1. Omnívoro 🍗\n2. Vegetariano 🥗\n3. Vegano 🌱\n4. Otro 🍽️"})

if __name__ == "__main__":
    app.run(debug=True)










