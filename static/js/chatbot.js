document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const caloriesBtn = document.getElementById('show-calories');
    const showMenuBtn = document.getElementById('show-menu');
    const videoOptionsBtn = document.getElementById('video-options');
    const nutritionData = document.getElementById('nutrition-data');
    const resetBtn = document.getElementById('reset-btn');
    const exerciseVideoBtn = document.getElementById('exercise-video');
    const recipeVideoBtn = document.getElementById('recipe-video');
    const videoModal = document.getElementById('video-modal');
    const closeModal = document.querySelector('.close-modal');
    const menuDisplay = document.getElementById('menu-display');
    const caloriesData = document.getElementById('calories-data');

    // Variables de estado
    let currentStep = '';
    let userData = {};
    let recognition = null;
    let videoLinks = {
        exercise: '',
        recipe: ''
    };

    // Inicialización
    initChat();

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', handleKeyPress);
    voiceBtn.addEventListener('click', toggleVoiceRecognition);
    caloriesBtn.addEventListener('click', showCalories);
    resetBtn.addEventListener('click', resetConversation);
    showMenuBtn.addEventListener('click', toggleNutritionData);
    videoOptionsBtn.addEventListener('click', showVideoModal);
    closeModal.addEventListener('click', hideVideoModal);
    exerciseVideoBtn.addEventListener('click', showExerciseVideo);
    recipeVideoBtn.addEventListener('click', showRecipeVideo);
    window.addEventListener('click', handleOutsideClick);

    // Funciones principales
    function initChat() {
        chatBox.innerHTML = '';
        currentStep = 'get_name';
        userData = {};
        videoLinks = { exercise: '', recipe: '' };
        addBotMessage("¡Hola! 👋 Soy NutriBot, tu asistente nutricional inteligente. ¿Cómo te llamas?");
        hideElement(videoOptionsBtn);
        hideElement(nutritionData);
        hideElement(showMenuBtn);
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addUserMessage(message);
        userInput.value = '';
        sendMessageToServer(message);
    }

    function handleKeyPress(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    }

    function sendMessageToServer(message) {
        showLoading(true);
        
        const formData = new FormData();
        formData.append('message', message);
        formData.append('step', currentStep);

        // Agregar datos del usuario al FormData
        Object.keys(userData).forEach(key => {
            formData.append(key, userData[key]);
        });

        fetch('/get_response', {
            method: 'POST',
            body: formData
        })
        .then(handleResponse)
        .catch(handleError)
        .finally(() => showLoading(false));
    }

    function handleResponse(response) {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json().then(data => {
            if (data.reset) {
                initChat();
                return;
            }
            
            // Mostrar respuesta del bot
            addBotMessage(data.response);
            
            // Actualizar paso actual
            if (data.step) currentStep = data.step;
            
            // Guardar datos del usuario
            updateUserData(data);
            
            // Manejar datos específicos de la respuesta
            if (data.show_menu) {
                showMenuBtn.classList.remove('oculto');
                videoOptionsBtn.classList.remove('oculto');
                videoLinks = {
                    exercise: data.exercise_video || '',
                    recipe: data.recipe_video || ''
                };
                
                if (data.reward) {
                    showReward(data.reward);
                }
            }
            
            if (data.nutrition_table) {
                menuDisplay.innerHTML = data.nutrition_table;
            }
        });
    }

    function updateUserData(data) {
        const fields = ['name', 'age', 'weight', 'height', 'goal', 'diet', 'activity'];
        fields.forEach(field => {
            if (data[field]) userData[field] = data[field];
        });
    }

    function showReward(message) {
        const rewardDiv = document.createElement('div');
        rewardDiv.className = 'reward-message';
        rewardDiv.innerHTML = message;
        chatBox.appendChild(rewardDiv);
        scrollToBottom();
        speak(message);
    }

    function showCalories() {
        showLoading(true);
        
        fetch('/get_calories')
            .then(response => response.json())
            .then(data => {
                let html = '';
                for (const [food, calories] of Object.entries(data)) {
                    html += `<tr><td>${food}</td><td>${calories} kcal</td></tr>`;
                }
                caloriesData.innerHTML = html;
                nutritionData.classList.remove('oculto');
                scrollToBottom();
            })
            .catch(handleError)
            .finally(() => showLoading(false));
    }

    function toggleNutritionData() {
        nutritionData.classList.toggle('oculto');
        if (!nutritionData.classList.contains('oculto')) {
            scrollToBottom();
        }
    }

    // Funciones de voz
    function toggleVoiceRecognition() {
        if (recognition && recognition.isListening) {
            stopVoiceRecognition();
            return;
        }
        startVoiceRecognition();
    }

    function startVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window)) {
            addBotMessage("Tu navegador no soporta reconocimiento de voz. Prueba con Chrome o Edge.");
            return;
        }

        recognition = new webkitSpeechRecognition();
        recognition.lang = 'es-ES';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onstart = () => {
            voiceBtn.classList.add('recording');
            userInput.placeholder = "Escuchando...";
            userInput.disabled = true;
        };
        
        recognition.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            userInput.value = transcript;
            sendMessage();
        };
        
        recognition.onerror = (e) => {
            console.error('Error en reconocimiento de voz:', e.error);
            addBotMessage("No pude entenderte. ¿Podrías repetir o escribir tu mensaje?");
        };
        
        recognition.onend = () => {
            stopVoiceRecognition();
        };
        
        recognition.isListening = true;
        recognition.start();
    }

    function stopVoiceRecognition() {
        if (recognition) {
            recognition.stop();
            recognition.isListening = false;
            voiceBtn.classList.remove('recording');
            userInput.placeholder = "Escribe tu mensaje...";
            userInput.disabled = false;
        }
    }

    // Funciones de video
    function showVideoModal() {
        videoModal.classList.remove('oculto');
    }

    function hideVideoModal() {
        videoModal.classList.add('oculto');
    }

    function showExerciseVideo() {
        if (videoLinks.exercise) {
            window.open(videoLinks.exercise, '_blank');
        } else {
            addBotMessage("No tengo un video de ejercicios disponible para tu perfil.");
        }
        hideVideoModal();
    }

    function showRecipeVideo() {
        if (videoLinks.recipe) {
            window.open(videoLinks.recipe, '_blank');
        } else {
            addBotMessage("No tengo un video de recetas disponible para tu dieta.");
        }
        hideVideoModal();
    }

    function handleOutsideClick(e) {
        if (e.target === videoModal) {
            hideVideoModal();
        }
    }

    // Funciones de UI
    function addUserMessage(message) {
        const div = document.createElement('div');
        div.className = 'user-message new-element';
        div.textContent = message;
        chatBox.appendChild(div);
        scrollToBottom();
    }

    function addBotMessage(message) {
        const div = document.createElement('div');
        div.className = 'bot-message new-element';
        
        // Procesar mensaje para mejorar visualización
        const processedMessage = processMessage(message);
        div.innerHTML = processedMessage;
        
        chatBox.appendChild(div);
        scrollToBottom();
        speak(cleanTextForSpeech(message));
    }

    function processMessage(message) {
        // Convertir URLs en enlaces clickeables
        return message
            .replace(/<a href='(.*?)' target='_blank'>(.*?)<\/a>/g, 
                '<a href="$1" target="_blank" class="video-link">$2 <i class="fas fa-external-link-alt"></i></a>')
            .replace(/\n/g, '<br>');
    }

    function cleanTextForSpeech(text) {
        // Eliminar HTML y emojis para el TTS
        return text
            .replace(/<[^>]*>?/gm, '')
            .replace(/[\u{1F600}-\u{1F6FF}]/gu, '')
            .trim();
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
                audio.play().catch(e => console.error('Error al reproducir audio:', e));
            }
        })
        .catch(e => console.error('Error en texto a voz:', e));
    }

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

    function hideElement(element) {
        element.classList.add('oculto');
    }

    function handleError(error) {
        console.error('Error:', error);
        addBotMessage("⚠️ Ocurrió un error. Por favor intenta nuevamente.");
    }

    function resetConversation() {
        sendMessageToServer('reiniciar');
    }
});




