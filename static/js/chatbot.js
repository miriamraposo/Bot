document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const caloriesBtn = document.getElementById('show-calories');
    const historyBtn = document.getElementById('show-history');
    const resetBtn = document.getElementById('reset-btn');
    const testBtn = document.getElementById('test-btn');

    let currentStep = '';
    let recognition = null;
    let isRecording = false;

    document.body.addEventListener('click', () => {
        const unlock = new Audio();
        unlock.play().catch(() => {});
    }, { once: true });

    initChat();

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (userInput) userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
    if (voiceBtn) voiceBtn.addEventListener('click', toggleVoiceRecognition);
    if (caloriesBtn) caloriesBtn.addEventListener('click', showCalories);
    if (historyBtn) historyBtn.addEventListener('click', showHistory);
    if (resetBtn) resetBtn.addEventListener('click', resetConversation);
    if (testBtn) {
        testBtn.addEventListener('click', () => {
            console.log("🧪 Botón de test clickeado correctamente");
            addBotMessage("✅ ¡El botón de test funciona!", true);
        });
    }

    function initChat() {
        chatBox.innerHTML = '';
        currentStep = '';
        document.getElementById('nutrition-data').classList.add('oculto');
        addBotMessage("¡Hola! 👋 Soy NutriBot, tu asistente nutricional. ¿Cómo te llamas?", true);
        currentStep = 'get_name';
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
        .then(response => response.json())
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

    function resetConversation() {
        const formData = new FormData();
        formData.append('message', 'reiniciar');
        formData.append('step', '');
        fetch('/get_response', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.reset) {
                initChat();
            }
        })
        .catch(error => {
            console.error("Error al reiniciar:", error);
            addBotMessage("⚠️ Hubo un problema al reiniciar la conversación.", true);
        });
    }

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
            speak(
                    message
                    .replace(/<[^>]*>/g, '')       // elimina etiquetas HTML
                    .replace(/[\u{1F300}-\u{1FAFF}]/gu, '') // elimina emojis
                );
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
                audio.play().catch(e => console.warn("🔇 Error al reproducir:", e));
            }
        });
    }

    function scrollToBottom() {
        setTimeout(() => {
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 100);
    }

    function showLoading(show) {
        if (!sendBtn) return;
        sendBtn.innerHTML = show ? '<i class="fas fa-spinner fa-spin"></i>' : '<i class="fas fa-paper-plane"></i>';
        sendBtn.disabled = show;
    }

    // ✅ Reconocimiento de voz funcional
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

        recognition.onstart = function () {
            isRecording = true;
            voiceBtn.classList.add('recording');
            userInput.placeholder = "Escuchando...";
        };

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            sendMessage();
        };

        recognition.onerror = function (event) {
            console.error("Error de voz:", event.error);
            addBotMessage("No pude entenderte. ¿Podrías repetir?", true);
        };

        recognition.onend = function () {
            stopVoiceRecognition();
        };

        recognition.start();
    }

    function stopVoiceRecognition() {
        if (recognition) recognition.stop();
        isRecording = false;
        voiceBtn.classList.remove('recording');
        userInput.placeholder = "Escribe tu mensaje...";
    }
});