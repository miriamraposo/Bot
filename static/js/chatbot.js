document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const caloriesBtn = document.getElementById('show-calories');
    const showMenuBtn = document.getElementById('show-menu');
    const nutritionData = document.getElementById('nutrition-data');
    const resetBtn = document.getElementById('reset-btn');

    let currentStep = '';
    let userData = {};
    let recognition = null;

    // Iniciar chat
    initChat();

    // Eventos
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', e => e.key === 'Enter' && sendMessage());
    voiceBtn.addEventListener('click', toggleVoiceRecognition);
    caloriesBtn.addEventListener('click', showCalories);
    resetBtn.addEventListener('click', resetConversation);
    showMenuBtn.addEventListener('click', () => nutritionData.classList.toggle('oculto'));

    function initChat() {
        chatBox.innerHTML = '';
        currentStep = 'get_name';
        userData = {};
        addBotMessage("¡Hola! 👋 Soy NutriBot. ¿Cómo te llamas?");
    }

    function resetConversation() {
        sendMessageToServer('reiniciar');
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addUserMessage(message);
        userInput.value = '';
        sendMessageToServer(message);
    }

    function sendMessageToServer(message) {
        const formData = new FormData();
        formData.append('message', message);
        formData.append('step', currentStep);

        // Enviar datos adicionales
        for (const key in userData) {
            formData.append(key, userData[key]);
        }

        fetch('/get_response', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.reset) {
                initChat();
                return;
            }
            handleResponse(data);
        })
        .catch(error => {
            console.error('Error:', error);
            addBotMessage("⚠️ Error de conexión. Intenta nuevamente.");
        });
    }

    function handleResponse(data) {
        addBotMessage(data.response);
        
        // Actualizar paso actual
        if (data.step) currentStep = data.step;
        
        // Guardar datos del usuario
        if (data.name) userData.name = data.name;
        if (data.age) userData.age = data.age;
        if (data.weight) userData.weight = data.weight;
        if (data.height) userData.height = data.height;
        if (data.goal) userData.goal = data.goal;
        if (data.diet) userData.diet = data.diet;

        // Mostrar menú si está disponible
        if (data.show_menu) {
            document.getElementById('menu-display').innerHTML = data.response;
            nutritionData.classList.remove('oculto');
            showMenuBtn.classList.remove('oculto');
        }
    }

    function showCalories() {
        fetch('/get_calories')
            .then(response => response.json())
            .then(data => {
                let html = '';
                for (const [food, calories] of Object.entries(data)) {
                    html += `<tr><td>${food}</td><td>${calories} kcal</td></tr>`;
                }
                document.getElementById('calories-data').innerHTML = html;
                nutritionData.classList.remove('oculto');
            })
            .catch(error => {
                console.error('Error:', error);
                addBotMessage("⚠️ Error al cargar calorías");
            });
    }

    function toggleVoiceRecognition() {
        if (recognition && recognition.isListening) {
            stopVoiceRecognition();
            return;
        }
        startVoiceRecognition();
    }

    function startVoiceRecognition() {
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.continuous = false;
            recognition.interimResults = false;
            
            recognition.onstart = () => {
                voiceBtn.classList.add('recording');
                userInput.placeholder = "Escuchando...";
            };
            
            recognition.onresult = e => {
                const transcript = e.results[0][0].transcript;
                userInput.value = transcript;
                sendMessage();
            };
            
            recognition.onerror = e => {
                console.error('Error en reconocimiento de voz:', e.error);
                addBotMessage("No pude entenderte. ¿Podrías repetir?");
            };
            
            recognition.onend = () => {
                voiceBtn.classList.remove('recording');
                userInput.placeholder = "Escribe tu mensaje...";
            };
            
            recognition.isListening = true;
            recognition.start();
        } else {
            addBotMessage("Tu navegador no soporta reconocimiento de voz");
        }
    }

    function stopVoiceRecognition() {
        if (recognition) {
            recognition.stop();
            recognition.isListening = false;
            voiceBtn.classList.remove('recording');
            userInput.placeholder = "Escribe tu mensaje...";
        }
    }

    function addUserMessage(message) {
        const div = document.createElement('div');
        div.className = 'user-message';
        div.textContent = message;
        chatBox.appendChild(div);
        scrollToBottom();
    }

    function addBotMessage(message) {
        const div = document.createElement('div');
        div.className = 'bot-message';
        div.innerHTML = message;
        chatBox.appendChild(div);
        scrollToBottom();
        speak(message);
    }

    function speak(text) {
        fetch('/text_to_speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `text=${encodeURIComponent(text)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.audio_url) {
                const audio = new Audio(data.audio_url);
                audio.play().catch(e => console.error('Error al reproducir audio:', e));
            }
        })
        .catch(e => console.error('Error en voz:', e));
    }

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});





