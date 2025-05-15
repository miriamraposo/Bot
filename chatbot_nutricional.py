import random

# Menús completos por objetivo y tipo de dieta
menus = {
    "Bajar de peso": {
        "Omnívoro": [
            {"desayuno": "Tostadas integrales con palta y huevo",
             "almuerzo": "Ensalada de pollo con vegetales",
             "cena": "Sopa de verduras y pescado al horno"},
            {"desayuno": "Yogur natural con frutas y avena",
             "almuerzo": "Pollo a la plancha con ensalada verde",
             "cena": "Puré de zapallo con pescado al vapor"},
            {"desayuno": "Huevos revueltos con espinaca",
             "almuerzo": "Wok de verduras con tiras de carne magra",
             "cena": "Sopa de tomate y ensalada mixta"}
        ],
        "Vegetariano": [
            {"desayuno": "Avena cocida con manzana y canela",
             "almuerzo": "Ensalada de lentejas con vegetales",
             "cena": "Sopa de zapallo y huevo duro"},
            {"desayuno": "Pan integral con palta y tomate",
             "almuerzo": "Tarta de espinaca y ricota light",
             "cena": "Vegetales al vapor con arroz integral"},
            {"desayuno": "Batido de frutas y chía",
             "almuerzo": "Hamburguesas de lentejas y ensalada",
             "cena": "Puré de zanahoria y calabacín"}
        ],
        "Vegano": [
            {"desayuno": "Smoothie de plátano y avena",
             "almuerzo": "Guiso de garbanzos con verduras",
             "cena": "Sopa de lentejas y pan integral"},
            {"desayuno": "Chía pudding con frutas",
             "almuerzo": "Wrap de hummus y vegetales",
             "cena": "Tofu grillado con ensalada"},
            {"desayuno": "Tostadas integrales con crema de almendras",
             "almuerzo": "Ensalada de quinoa y garbanzos",
             "cena": "Sopa de vegetales y arroz integral"}
        ]
    },

    "Mantener peso": {
        "Omnívoro": [
            {"desayuno": "Huevos a la copa con pan integral y frutas",
             "almuerzo": "Pechuga de pollo con arroz y brócoli",
             "cena": "Ensalada de atún con tomate y lechuga"},
            {"desayuno": "Yogur con granola y frutos rojos",
             "almuerzo": "Carne magra a la plancha con puré de batata",
             "cena": "Tortilla de verduras con ensalada verde"},
            {"desayuno": "Tostadas con queso bajo en grasa y tomate",
             "almuerzo": "Milanesa de pollo al horno con ensalada",
             "cena": "Sopa de verduras con pescado al vapor"}
        ],
        "Vegetariano": [
            {"desayuno": "Avena con leche y frutas frescas",
             "almuerzo": "Hamburguesas de soja con ensalada mixta",
             "cena": "Quiche de espinaca y ricota"},
            {"desayuno": "Pan integral con queso crema y mermelada light",
             "almuerzo": "Tarta de calabaza y zapallitos",
             "cena": "Ensalada de garbanzos con verduras"},
            {"desayuno": "Batido de plátano, espinaca y leche de almendra",
             "almuerzo": "Pastel de lentejas con ensalada",
             "cena": "Sopa de verduras con queso rallado"}
        ],
        "Vegano": [
            {"desayuno": "Smoothie bowl de frutas y semillas",
             "almuerzo": "Arroz integral con tofu y verduras salteadas",
             "cena": "Ensalada de quinoa con vegetales frescos"},
            {"desayuno": "Pan integral con mantequilla de maní y banana",
             "almuerzo": "Hamburguesa vegana con ensalada verde",
             "cena": "Crema de calabaza con pan integral"},
            {"desayuno": "Pudding de chía con leche de coco y frutas",
             "almuerzo": "Guiso de lentejas con verduras mixtas",
             "cena": "Tofu marinado con vegetales al horno"}
        ]
    },

    "Ganar masa muscular": {
        "Omnívoro": [
            {"desayuno": "Omelette de claras con espinaca y queso",
             "almuerzo": "Pechuga de pollo con arroz integral y brócoli",
             "cena": "Salmón al horno con ensalada de quinoa"},
            {"desayuno": "Batido de proteínas con avena y plátano",
             "almuerzo": "Carne magra con puré de papas y verduras",
             "cena": "Tortilla de huevo con vegetales"},
            {"desayuno": "Pan integral con mantequilla de maní y huevo duro",
             "almuerzo": "Pasta integral con pollo y salsa de tomate",
             "cena": "Ensalada de atún con legumbres"}
        ],
        "Vegetariano": [
            {"desayuno": "Tostadas con aguacate y huevo poché",
             "almuerzo": "Hamburguesa de garbanzos con arroz integral",
             "cena": "Quinoa con verduras y queso feta"},
            {"desayuno": "Yogur griego con nueces y miel",
             "almuerzo": "Lentejas estofadas con vegetales",
             "cena": "Tarta de espinaca con queso ricota"},
            {"desayuno": "Batido de proteína vegetal con frutas",
             "almuerzo": "Tofu grillado con arroz y brócoli",
             "cena": "Sopa de verduras con huevo duro"}
        ],
        "Vegano": [
            {"desayuno": "Smoothie de proteína vegetal con plátano y avena",
             "almuerzo": "Guiso de lentejas con arroz integral",
             "cena": "Tofu salteado con verduras y quinoa"},
            {"desayuno": "Pudding de chía con leche de almendra y frutas",
             "almuerzo": "Hamburguesa vegana con ensalada verde",
             "cena": "Sopa de calabaza con pan integral"},
            {"desayuno": "Pan integral con crema de almendras y plátano",
             "almuerzo": "Ensalada de garbanzos con vegetales mixtos",
             "cena": "Tofu al horno con puré de batata"}
        ]
    }
}

# Snacks y consejos saludables
snacks_saludables = [
    "Una manzana o banana",
    "Un puñado de frutos secos",
    "Yogur natural con semillas",
    "Galletas de avena caseras",
    "Palitos de zanahoria o apio"
]

consejos_diarios = [
    "Tomá al menos 2 litros de agua al día.",
    "Evitá las bebidas azucaradas.",
    "Dormí al menos 7 horas.",
    "Comé sin distracciones (pantallas o celular).",
    "Incorporá verduras en cada comida."
]

# Función para mostrar opciones y recibir respuesta válida
def obtener_respuesta_opciones(pregunta, opciones):
    print("\n" + pregunta)
    for i, opcion in enumerate(opciones, 1):
        print(f"{i}. {opcion}")
    while True:
        eleccion = input("Elige una opción (número): ")
        if eleccion.isdigit() and 1 <= int(eleccion) <= len(opciones):
            return opciones[int(eleccion) - 1]
        else:
            print("Opción inválida. Intenta nuevamente.")

# Función para mostrar menú con selección aleatoria y recomendaciones
def mostrar_menu(objetivo, dieta):
    print("\n🍽️ Aquí tienes tu menú personalizado para hoy:")
    menu_elegido = random.choice(menus[objetivo][dieta])
    for comida, receta in menu_elegido.items():
        print(f"{comida.capitalize()}: {receta}")

    snack = random.choice(snacks_saludables)
    consejo = random.choice(consejos_diarios)
    print(f"\n🥪 Snack sugerido: {snack}")
    print(f"💡 Consejo saludable: {consejo}")

def chatbot_nutricional():
    print("🧠 Bienvenido/a al Chatbot Nutricional Personalizado 🥦")

    objetivo = obtener_respuesta_opciones(
        "¿Cuál es tu objetivo?",
        ["Bajar de peso", "Mantener peso", "Ganar masa muscular"]
    )

    condicion = obtener_respuesta_opciones(
        "¿Tienes alguna condición médica?",
        ["Ninguna", "Diabetes", "Hipertensión", "Otra"]
    )

    dieta = obtener_respuesta_opciones(
        "¿Qué tipo de alimentación prefieres?",
        ["Omnívoro", "Vegetariano", "Vegano"]
    )

    actividad = obtener_respuesta_opciones(
        "¿Cuál es tu nivel de actividad física?",
        ["Sedentario", "Moderado", "Intenso"]
    )

    recordatorios = obtener_respuesta_opciones(
        "¿Deseas recibir recordatorios diarios de hidratación y consejos?",
        ["Sí", "No"]
    )

    print("\n✅ Resumen personalizado:")
    print(f"- Objetivo: {objetivo}")
    print(f"- Condición médica: {condicion}")
    print(f"- Dieta: {dieta}")
    print(f"- Nivel de actividad: {actividad}")
    print(f"- Recordatorios: {recordatorios}")

    mostrar_menu(objetivo, dieta)

    if recordatorios == "Sí":
        print("\n¡Recuerda hidratarte y seguir hábitos saludables!")

if __name__ == "__main__":
    chatbot_nutricional()
