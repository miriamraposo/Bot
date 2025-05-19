document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const caloriesBtn = document.getElementById('show-calories');
    const historyBtn = document.getElementById('show-history');
    const resetBtn = document.getElementById('reset-btn');

    // Variables de estado
    let currentStep = '';
    let recognition = null;
    let isRecording = false;

    // Inicialización
    initChat();

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
    voiceBtn.addEventListener('click', toggleVoiceRecognition);
    caloriesBtn.addEventListener('click', showCalories);
    historyBtn.addEventListener('click', showHistory);
    resetBtn.addEventListener('click', resetConversation);

    // Funciones principales
    function initChat() {
        chatBox.innerHTML = '';
        currentStep = '';
        document.getElementById('nutrition-data').classList.add('oculto');
        addBotMessage("¡Hola! 👋 Soy NutriBot, tu asistente nutricional. ¿Cómo te llamas?", true);
        currentStep = 'get_name'; // Establecer el paso inicial explícitamente
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addUserMessage(message);
        userInput.value = '';
        processMessage(message);
    }

    function processMessage(message) {
        showLoading(true);
        
        const formData = new FormData();
        formData.append('message', message);
        formData.append('step', currentStep);

        fetch('/get_response', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) throw new Error('Error en la respuesta del servidor');
            return response.json();
        })
        .then(data => {
            if (data.error) {
                addBotMessage(data.error, true);
                return;
            }
            
            if (data.reset) {
                initChat();
                return;
            }
            
            currentStep = data.step || currentStep;
            addBotMessage(data.response, data.speak);
            
            if (data.show_menu) {
                document.getElementById('menu-display').innerHTML = data.response;
                document.getElementById('nutrition-data').classList.remove('oculto');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addBotMessage("⚠️ Error al procesar tu mensaje. Por favor intenta nuevamente.", true);
        })
        .finally(() => showLoading(false));
    }

    // Sistema de Voz
    function toggleVoiceRecognition() {
        if (isRecording) {
            stopVoiceRecognition();
        } else {
            startVoiceRecognition();
        }
    }

    function startVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window)) {
            addBotMessage("Tu navegador no soporta reconocimiento de voz", true);
            return;
        }

        recognition = new webkitSpeechRecognition();
        recognition.lang = 'es-ES';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = function() {
            isRecording = true;
            voiceBtn.classList.add('recording');
            userInput.placeholder = "Escuchando...";
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            sendMessage();
        };

        recognition.onerror = function(event) {
            console.error('Error de voz:', event.error);
            addBotMessage("No pude entenderte. ¿Podrías repetir?", true);
        };

        recognition.onend = function() {
            stopVoiceRecognition();
        };

        recognition.start();
    }

    function stopVoiceRecognition() {
        if (recognition) {
            recognition.stop();
        }
        isRecording = false;
        voiceBtn.classList.remove('recording');
        userInput.placeholder = "Escribe tu mensaje...";
    }

    // Funciones de UI
    function addUserMessage(message) {
        const div = document.createElement('div');
        div.className = 'user-message';
        div.textContent = message;
        chatBox.appendChild(div);
        scrollToBottom();
    }

    function addBotMessage(message, shouldSpeak = false) {
        const div = document.createElement('div');
        div.className = 'bot-message';
        div.innerHTML = message;
        chatBox.appendChild(div);
        scrollToBottom();
        
        if (shouldSpeak) {
            speak(message.replace(/<[^>]*>/g, ''));
        }
    }

    function speak(text) {
        if (!text.trim()) return;
        
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
                audio.play().catch(e => console.log("Error al reproducir:", e));
            }
        });
    }

    // Funciones de datos
    function showCalories() {
        showLoading(true);
        
        fetch('/get_calories')
        .then(response => response.json())
        .then(data => {
            let html = '';
            for (const [food, calories] of Object.entries(data)) {
                html += `<tr><td>${food}</td><td>${calories}</td></tr>`;
            }
            document.getElementById('calories-data').innerHTML = html;
            document.getElementById('nutrition-data').classList.remove('oculto');
            scrollToBottom();
        })
        .catch(error => {
            console.error('Error:', error);
            addBotMessage("⚠️ Error al cargar calorías", true);
        })
        .finally(() => showLoading(false));
    }

    function showHistory() {
        addBotMessage("🔍 Esta funcionalidad estará disponible en la próxima actualización", true);
    }

    // Utilidades
    function scrollToBottom() {
        setTimeout(() => {
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 100);
    }

    function showLoading(show) {
        if (show) {
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            sendBtn.disabled = true;
        } else {
            sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            sendBtn.disabled = false;
        }
    }

    function resetConversation() {
        fetch('/get_response', {
            method: 'POST',
            body: new FormData()
        })
        .then(() => initChat());
    }
});




