document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const resetBtn = document.getElementById('reset-btn');
    const showCaloriesBtn = document.getElementById('show-calories');
    const showMenuBtn = document.getElementById('show-menu');
    const menuDisplay = document.getElementById('menu-display');
    const caloriesDisplay = document.getElementById('calories-display');
    const nutritionData = document.getElementById('nutrition-data');

    // Estado del chatbot
    let chatState = {
        goal: null,
        diet: null,
        menuShown: false
    };

    // Inicialización
    initChat();

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => e.key === 'Enter' && sendMessage());
    voiceBtn.addEventListener('click', startVoiceRecognition);
    resetBtn.addEventListener('click', resetConversation);
    showCaloriesBtn.addEventListener('click', showCaloriesTable);
    showMenuBtn.addEventListener('click', showCurrentMenu);

    // Funciones principales
    function initChat() {
        addBotMessage("¡Hola! 👋 Soy NutriBot. ¿Quieres bajar de peso o aumentar masa muscular?");
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addUserMessage(message);
        userInput.value = '';
        
        fetch('/get_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `message=${encodeURIComponent(message)}`
        })
        .then(response => response.json())
        .then(handleBotResponse);
    }

    function handleBotResponse(response) {
        addBotMessage(response.response);

        // Actualizar estado
        if (response.reset) {
            resetState();
        } else {
            if (response.goal) chatState.goal = response.goal;
            if (response.diet) chatState.diet = response.diet;
        }

        // Mostrar/ocultar elementos
        if (response.show_menu && chatState.goal && chatState.diet) {
            fetch('/get_full_menu', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    goal: chatState.goal,
                    diet: chatState.diet
                })
            })
            .then(response => response.json())
            .then(data => {
                menuDisplay.innerHTML = data.menu;
                caloriesDisplay.innerHTML = data.calories;
                showMenuBtn.classList.remove('oculto');
                nutritionData.classList.remove('oculto');
                chatState.menuShown = true;
            });
        }
    }

    function startVoiceRecognition() {
        if ('webkitSpeechRecognition' in window) {
            const recognition = new webkitSpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.interimResults = false;

            recognition.onstart = () => {
                voiceBtn.innerHTML = '🎤 Escuchando...';
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript;
                sendMessage();
            };

            recognition.onerror = () => {
                voiceBtn.innerHTML = '🎤';
                addBotMessage("No pude entenderte. ¿Podrías escribirlo?");
            };

            recognition.onend = () => {
                voiceBtn.innerHTML = '🎤';
            };

            recognition.start();
        } else {
            addBotMessage("Tu navegador no soporta reconocimiento de voz");
        }
    }

    function resetConversation() {
        resetState();
        addBotMessage("Conversación reiniciada. ¿Quieres bajar de peso o aumentar masa muscular?");
    }

    function resetState() {
        chatState = {
            goal: null,
            diet: null,
            menuShown: false
        };
        nutritionData.classList.add('oculto');
        showMenuBtn.classList.add('oculto');
    }

    function showCaloriesTable() {
        if (!chatState.menuShown) return;
        nutritionData.classList.remove('oculto');
    }

    function showCurrentMenu() {
        if (!chatState.menuShown) return;
        nutritionData.classList.remove('oculto');
    }

    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('user-message');
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        scrollChatToBottom();
    }

    function addBotMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('bot-message');
        messageElement.innerHTML = message;
        chatBox.appendChild(messageElement);
        scrollChatToBottom();
        speakMessage(message);
    }

    function speakMessage(message) {
        fetch('/text_to_speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `text=${encodeURIComponent(message)}`
        })
        .then(response => response.json())
        .then(data => {
            const audio = new Audio(data.audio_url);
            audio.play();
        });
    }

    function scrollChatToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});





