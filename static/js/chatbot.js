document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    // const caloriesBtn = document.getElementById('show-calories'); // Eliminado si no se usa más el botón externo
    const historyBtn = document.getElementById('show-history');
    const resetBtn = document.getElementById('reset-btn');
    // const testBtn = document.getElementById('test-btn'); // Eliminado si no se usa más el botón de test

    // Nuevos elementos para los botones de acción post-menú
    const actionButtonsAfterMenu = document.getElementById('action-buttons-after-menu');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const sendEmailBtn = document.getElementById('send-email-btn');

    let currentStep = '';
    let recognition = null; // Para el reconocimiento de voz
    let isRecording = false; // Estado del reconocimiento de voz
    let lastGeneratedPlanHtml = '';

    // Pequeño truco para permitir la reproducción automática de audio en algunos navegadores
    document.body.addEventListener('click', () => {
        const unlock = new Audio();
        unlock.play().catch(() => {});
    }, { once: true });

    // Inicializar el chat al cargar la página
    initChat();

    // Event Listeners para los botones y el input
    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (userInput) userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
    if (voiceBtn) voiceBtn.addEventListener('click', toggleVoiceRecognition);
    // if (caloriesBtn) caloriesBtn.addEventListener('click', showCalories); // Event listener para el botón de calorías (si se mantiene)
    if (historyBtn) historyBtn.addEventListener('click', showHistory);
    if (resetBtn) resetBtn.addEventListener('click', resetConversation);
    
    // --- Nuevos Event Listeners para los botones de acción ---
    if (downloadPdfBtn) downloadPdfBtn.addEventListener('click', downloadPlanAsPdf);
    //if (sendEmailBtn) sendEmailBtn.addEventListener('click', sendPlanByEmail);

    // Función para inicializar o reiniciar el chat
    function initChat() {
        chatBox.innerHTML = '';
        currentStep = '';
        // Ocultar los botones de acción al inicio/reiniciar el chat
        if (actionButtonsAfterMenu) {
            actionButtonsAfterMenu.classList.add('oculto');
        }
        addBotMessage("¡Hola! 👋 Soy NutriBot, tu asistente nutricional. ¿Cómo te llamas?", true);
        currentStep = 'get_name';
    }

    // Función para reiniciar la conversación completamente
   function resetConversation() {
    fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: 'reiniciar', step: 'menu_displayed' }) // ✅ Fix completo
    })
    .then(response => response.json())
    .then(data => {
        if (data.reset) {
            initChat(); // Reinicia la interfaz
        } else {
            addBotMessage("No se pudo reiniciar la conversación.", true);
        }
    })
    .catch(error => {
        console.error('Error al reiniciar:', error);
        addBotMessage("⚠️ Error al reiniciar la conversación.", true);
    });
}


    // Función para enviar el mensaje del usuario al backend
    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addUserMessage(message);
            userInput.value = '';
            processMessage(message);
        }
    }

    // Función para añadir mensajes del usuario al chatbox
    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'user-message');
        messageDiv.textContent = message;
        chatBox.appendChild(messageDiv);
        scrollToBottom();
    }

    // Función para añadir mensajes del bot al chatbox y, opcionalmente, reproducir audio
    function addBotMessage(message, speak = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot-message');
        messageDiv.innerHTML = message; // Usar innerHTML para el contenido HTML del menú
        chatBox.appendChild(messageDiv);
        scrollToBottom();

        if (speak) {
            // Limpiar el HTML y emojis antes de enviar a text_to_speech
            const cleanText = message
                .replace(/<[^>]*>/g, '')       // Eliminar etiquetas HTML
                .replace(/http\S+/g, '')       // Eliminar URLs
                .replace(/[\u{1F000}-\u{1FFFF}]/gu, ''); // Eliminar emojis ampliado
            
            if (!cleanText.trim()) return; // No enviar texto vacío

            fetch('/text_to_speech', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `text=${encodeURIComponent(cleanText)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.audio_url) {
                    const audio = new Audio(data.audio_url);
                    audio.play().catch(e => console.error("Error al reproducir audio:", e));
                }
            })
            .catch(error => console.error("Error al obtener audio:", error));
        }
    }

    // Función para procesar el mensaje y obtener la respuesta del backend
function processMessage(message) {
    showLoading(true);

    // --- CAMBIO 1: Asegúrate de enviar JSON si app.py lo espera ---
    // Si tu app.py espera JSON (como en el ejemplo de app.py que tengo de referencia),
    // cambia esto para enviar un objeto JSON en lugar de FormData.
    // Si ya te funciona con FormData y Flask lo parsea bien, puedes omitir este cambio
    // pero es una buena práctica para enviar JSON.
    const requestBody = {
        message: message,
        step: currentStep
        // Si necesitas enviar chatHistory, añádelo aquí también
        // history: chatHistory // Descomentar si usas chatHistory en el frontend y lo envías
    };

    fetch('/get_response', {
        method: 'POST',
        // Si usas JSON, asegúrate de añadir el Content-Type header
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody) // Envía el objeto JSON
        // Si quieres seguir usando FormData: body: formData (y quita headers y JSON.stringify)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addBotMessage(data.error, true);
            if (actionButtonsAfterMenu) {
                actionButtonsAfterMenu.classList.add('oculto');
            }
            return;
        }
        if (data.reset) {
            initChat();
            return;
        }
        currentStep = data.step || currentStep;

        // --- CAMBIO 2: Guardar el full_plan_data aquí ---
        if (data.full_plan_data) {
            lastGeneratedPlanHtml = data.full_plan_data; // <--- Guarda el HTML del plan aquí
            console.log("Plan HTML guardado:", lastGeneratedPlanHtml.substring(0, 100) + "..."); // Para depuración
        } else {
            lastGeneratedPlanHtml = ''; // Limpiar si no hay plan en la respuesta actual
        }

        // Siempre añadir la respuesta al chatbox
        addBotMessage(data.response, data.speak);

        // Mostrar los botones de acción si el backend indica que es un menú
        if (data.show_menu && actionButtonsAfterMenu) {
            actionButtonsAfterMenu.classList.remove('oculto');
        } else if (!data.show_menu && actionButtonsAfterMenu) {
            // Ocultar los botones si no es un mensaje de menú
            actionButtonsAfterMenu.classList.add('oculto');
        }

        // Si tienes reproducción de audio, asegúrate de que se active aquí
        if (data.audio_filename) {
            playAudio(data.audio_filename);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addBotMessage("⚠️ Error al procesar tu mensaje. Por favor intenta nuevamente.", true);
        if (actionButtonsAfterMenu) {
            actionButtonsAfterMenu.classList.add('oculto');
        }
    })
    .finally(() => showLoading(false));
}

    // Función para mostrar/ocultar el indicador de carga y deshabilitar/habilitar inputs/botones
    function showLoading(isLoading) {
        if (!sendBtn) return; // Asegurarse de que los elementos existan

        // Deshabilitar/Habilitar input y botón de enviar
        userInput.disabled = isLoading;
        sendBtn.disabled = isLoading;
        voiceBtn.disabled = isLoading;

        // Actualizar el texto del placeholder
        userInput.placeholder = isLoading ? "Pensando..." : "Escribe tu mensaje...";

        // Cambiar icono del botón de enviar
        sendBtn.innerHTML = isLoading ? '<i class="fas fa-spinner fa-spin"></i>' : 'Enviar';

        // Deshabilitar/Habilitar los botones de acción
        if (downloadPdfBtn) downloadPdfBtn.disabled = isLoading;
        if (sendEmailBtn) sendEmailBtn.disabled = isLoading;
        if (resetBtn) resetBtn.disabled = isLoading;
        if (historyBtn) historyBtn.disabled = isLoading;
    }

    // Función para desplazar el chatbox hacia abajo
    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // --- Funcionalidad de Reconocimiento de Voz ---
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
            sendMessage(); // Enviar el mensaje una vez reconocido
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

    // --- Funcionalidad para mostrar historial ---
    function showHistory() {
        showLoading(true);
        addBotMessage("Cargando tu historial de planes...", true); // Mensaje inicial
        fetch('/show_history')
            .then(response => {
                if (!response.ok) {
                    // Si la respuesta no es OK, intentar leer como JSON para obtener el mensaje de error del backend
                    return response.json().then(err => Promise.reject(err));
                }
                return response.json();
            })
            .then(data => {
                if (data.length > 0) {
                    let historyHtml = "<h3>📚 Tu Historial de Planes:</h3><ul>";
                    data.forEach(item => {
                        historyHtml += `<li><strong>Fecha:</strong> ${item.fecha}, <strong>Objetivo:</strong> ${item.objetivo}, <strong>Dieta:</strong> ${item.dieta}`;
                        // ACCESO CORRECTO A LAS CALORÍAS DESDE EL OBJETO 'item'
                        // Aseguramos que item.total_calories exista y no sea 'N/A' antes de mostrarlo
                        if (item.total_calories && item.total_calories !== 'N/A') {
                            historyHtml += `, <strong>Calorías:</strong> ${item.total_calories} kcal`;
                        }
                        historyHtml += `</li>`;
                    });
                    historyHtml += "</ul>";
                    addBotMessage(historyHtml, false); // No lo leemos completo
                } else {
                    addBotMessage("No tienes historial de planes aún. ¡Genera tu primer plan!", true);
                }
            })
            .catch(error => {
                console.error('Error al cargar historial:', error);
                const errorMessage = error.message ? error.message : "Error desconocido al cargar el historial.";
                addBotMessage(`⚠️ Error al cargar tu historial: ${errorMessage}`, true);
            })
            .finally(() => showLoading(false));
    }

    // --- Funciones para PDF y Email ---
    function downloadPlanAsPdf() {
        showLoading(true);
        // Obtener el contenido HTML del último mensaje del bot (que debe ser el plan)
        const chatMessages = chatBox.getElementsByClassName('bot-message');
        if (chatMessages.length === 0) {
            addBotMessage("No hay un plan nutricional para descargar.", true);
            showLoading(false);
            return;
        }
        const lastBotMessage = chatMessages[chatMessages.length - 1];
        const planHtml = lastBotMessage.innerHTML; // Esto contendrá todo el HTML del plan

        fetch('/download_plan_pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ html_content: planHtml })
        })
        .then(response => {
            if (response.ok) {
                return response.blob(); // Recibir el PDF como un blob
            } else {
                // Si la respuesta no es OK, intentar leer como JSON para obtener el mensaje de error del backend
                return response.json().then(err => Promise.reject(err));
            }
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'PlanNutricional_NutriBot.pdf'; // Nombre del archivo
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            addBotMessage("¡Tu plan nutricional ha sido descargado! 🎉", true);
            showFinalActionButtons();
        })
        .catch(error => {
            console.error('Error al descargar PDF:', error);
            const errorMessage = error.message ? error.message : "Error desconocido al generar el PDF.";
            addBotMessage(`⚠️ Error al generar el PDF: ${errorMessage}`, true);
        })
        .finally(() => showLoading(false));
    }

// chatbot.js (dentro de sendEmailBtn.addEventListener)


sendEmailBtn.addEventListener('click', function () {
    if (!lastGeneratedPlanHtml) {
        addBotMessage("⚠️ No hay un plan nutricional para enviar. Por favor, genera uno primero.", true);
        return;
    }

    // Crear input dinámicamente
    const emailInputDiv = document.createElement('div');
    emailInputDiv.innerHTML = `
        <input type="email" id="email-input" placeholder="Ingresa tu email" class="input-email" />
        <button id="confirm-email-btn" class="btn-confirmar">
            <i class="fas fa-paper-plane"></i> Confirmar
        </button>
    `;
    chatBox.appendChild(emailInputDiv);
    scrollToBottom();

    const emailInput = emailInputDiv.querySelector('#email-input');
    const confirmEmailBtn = emailInputDiv.querySelector('#confirm-email-btn');

    confirmEmailBtn.addEventListener('click', function () {
        const email = emailInput.value.trim();
        if (!email) {
            addBotMessage("Por favor, introduce una dirección de correo válida.", true);
            return;
        }

        showLoading(true);

        

fetch('/send_plan_email', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email: email, html_content: lastGeneratedPlanHtml })
})
.then(async response => {
    let data = null;

    try {
        const contentType = response.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
            data = await response.json();
        }
    } catch (err) {
        console.warn("Error al parsear JSON:", err);
    }

    if (response.ok && data && data.success) {
        addBotMessage(`✅ El plan ha sido enviado a 📧 ${email}!`, true);
        showFinalActionButtons();
    } else {
        const errorMsg = (data && data.message) || "Error desconocido al enviar el correo.";
        addBotMessage(`⚠️ ${errorMsg}`, true);
    }

    emailInputDiv.remove();
})
.catch(error => {
    console.error('Error al enviar email:', error);
    addBotMessage("⚠️ Error desconocido al enviar el correo (fallo de red o backend).", true);
    emailInputDiv.remove();
})
.finally(() => showLoading(false));



    });
});
function showFinalActionButtons() {
    addBotMessage("¿Qué deseas hacer a continuación?", true);
    showDynamicButtons([
        { text: "Finalizar", value: "finalizar", handler: handleFinalAction },
        { text: "Nueva Consulta", value: "nueva_consulta", handler: handleFinalAction }
    ]);
}

function handleFinalAction(action) {
    addUserMessage(action === "finalizar" ? "Finalizar" : "Nueva Consulta");
    hideDynamicButtons();
    actionButtonsAfterMenu.classList.add('oculto');

    if (action === "finalizar") {
        addBotMessage("¡Gracias por usar NutriBot! Espero haberte sido útil 💚", true);
    } else {
        resetConversation(); // Volvés al inicio del flujo
    }
}
function showDynamicButtons(buttons) {
    const container = document.getElementById('button-container');
    container.innerHTML = '';
    buttons.forEach(btn => {
        const buttonEl = document.createElement('button');
        buttonEl.classList.add('btn-primary');
        buttonEl.textContent = btn.text;
        buttonEl.addEventListener('click', () => btn.handler(btn.value));
        container.appendChild(buttonEl);
    });
}

function hideDynamicButtons() {
    const container = document.getElementById('button-container');
    container.innerHTML = '';
}

;})



