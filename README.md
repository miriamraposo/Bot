# 🥗 NutriBot - Asistente Nutricional Inteligente

**NutriBot** es un chatbot desarrollado con Flask que actúa como asistente virtual para ayudar a los usuarios a alcanzar sus objetivos nutricionales y de actividad física de forma personalizada. A través de una conversación guiada, NutriBot genera menús, rutinas de ejercicios, listas de compras, suplementos recomendados y hasta recompensa a los usuarios por su constancia.

---

## 🧠 Funcionalidades principales

- 🗣️ Interfaz conversacional paso a paso
- 🔢 Cálculo de IMC y clasificación nutricional
- 🥕 Generación de menús personalizados según objetivo y tipo de dieta:
  - Vegetariana
  - Vegana
  - Tradicional
- 🏋️‍♀️ Recomendación de ejercicios según nivel de actividad
- 📺 Acceso a rutinas en video y recetas saludables
- 📦 Lista de compras automática
- 💊 Suplementación sugerida
- 🏅 Sistema de recompensas por seguimiento del plan
- 🔊 Conversión de texto a voz con `gTTS`
- 🧾 Registro histórico de planes realizados

---

## 🚀 Tecnologías utilizadas

- **Python 3**
- **Flask**
- **SQLite**
- **gTTS (Google Text-to-Speech)**
- **HTML + JavaScript**
- **Bootstrap + FontAwesome**

---

## 📁 Estructura del proyecto

```
nutribot/
├── app.py                  # Lógica principal del chatbot (Flask)
├── nutribot.db             # Base de datos SQLite (usuarios e historial)
├── templates/
│   └── index.html          # Interfaz web principal
├── static/
│   └── audios/             # Carpeta de salida para audios generados
│   └── css/             
│       └── style.css       # Hoja de estilos aplicados
│   └── imagenes/           # Carpeta de salida para imagenes utilizadas
│   └── js/                 
│       └── chatbot.js      # Script con la estructura funcional del chatbot
└── README.md               # Este archivo
```

---

## ⚙️ Cómo ejecutar el proyecto

1. **Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/nutribot.git
cd nutribot
```

2. **Instalar dependencias**

Asegúrate de tener un entorno virtual activado (opcional pero recomendado), luego ejecutá:

```bash
pip install -r requirements.txt
```

O bien, instalalas manualmente:

```bash
pip install Flask Flask-Mail gTTS WeasyPrint
```

3. **Iniciar la aplicación**

```bash
python app.py
```

4. **Acceder desde el navegador**

```
http://localhost:5000
```

---

## 🗃️ Estructura de la base de datos

### Tabla: `usuarios`
- `id`: INT, clave primaria
- `nombre`: TEXT, único
- `contador`: INT, número de planes realizados
- `ultima_visita`: TEXT (ISO format)
- `recompensas_obtenidas`: TEXT (IDs separados por coma)

### Tabla: `historial`
- `id`: INT, clave primaria
- `usuario`: TEXT
- `fecha`: TEXT
- `objetivo`: TEXT (`bajar`, `mantener`, `aumentar`)
- `dieta`: TEXT (`vegetariano`, `vegano`, `tradicional`)
- `menu`: TEXT
- `lista_compra`: TEXT
- `suplementos`: TEXT
- `ejercicios`: TEXT

---

## 🏆 Sistema de recompensas

| Planes completados | Recompensa                                  |
|--------------------|---------------------------------------------|
| 3                  | 🎉 10% descuento en suplementos (NUTRI10)   |
| 5                  | 🏆 Guía de nutrición gratuita               |
| 7                  | 💎 Sesión gratuita con nutricionista        |

---

## 🔊 Funcionalidad de texto a voz

La función `/text_to_speech` convierte respuestas en audio usando `gTTS`. El texto se limpia de HTML, URLs y emojis antes de convertirlo. Los archivos de audio se guardan en `static/audios/` y se reproducen en la interfaz.

---

## 💡 Posibles mejoras futuras

- Autenticación de usuarios y perfiles personalizados
- Integración con API externas de recetas y nutrición
- Exportación de historial en PDF
- Interfaz móvil (PWA)
- Dashboard para profesionales de la salud

---

## 👩‍💻 Autoras y autores

¡Conocé a quienes hicieron posible NutriBot!


| Foto | Nombre | Rol en el proyecto | Bio | Redes |
|------|--------|--------------------|-----|-------|
| ![Maru](static/imagenes/maru.jpg) | **Mary Luz Caleño** | Arquitectura y lógica inicial | Dio el primer paso con el esqueleto del chatbot. Sentó las bases de la inteligencia conversacional y organizó la estructura general del proyecto. | [LinkedIn](https://linkedin.com/in/maryluz) |
| ![Natalia](static/images/natalia.jpg) | **Natalia Liscio** | Funcionalidades avanzadas y diseño UX/UI | Le dio alma y estilo a NutriBot. Incorporó nuevas funciones, cuidó cada detalle del diseño y convirtió la experiencia en algo visualmente nutritivo. | [LinkedIn](https://linkedin.com/in/natalialiscio) |
| ![Micaela](static/imagenes/micaela.jpg) | **Micaela Vera** | Comunicación y presentación | Fue la voz del equipo. Encargada de transmitir el valor del proyecto a través de una presentación clara, creativa y efectiva. | [Instagram](https://instagram.com/micaela.vera) |
| ![Nahuel](static/imagenes/nahuel.jpg) | **Nahuel Genoese** | Soporte técnico y testing | Colaboró en la validación del chatbot y brindó apoyo para asegurar que todo funcionara sin errores. | [GitHub](https://github.com/nahuelg) |
| ![Miriam](static/imagenes/miriam.jpg) | **Miriam Raposo** | Revisión y control de calidad | Supervisó la documentación final y se encargó de los detalles que hacen a un proyecto bien cerrado. | [LinkedIn](https://linkedin.com/in/miriamraposo) |


> Las imágenes de perfil deben guardarse en `static/imagenes/` y tener nombres en minúsculas, sin espacios.


¡Gracias por usar NutriBot! 🌱 Tu viaje saludable empieza con una conversación 🗨️💚


---

## 📦 requirements.txt sugerido

```txt
Flask
Flask-Mail
gTTS
WeasyPrint
```
