// document.addEventListener('DOMContentLoaded', () => {
//     const chatContainer = document.getElementById('chat-container');
//     if (!chatContainer) {
//         return;
//     }

//     const sendBtn = document.getElementById('send-btn');
//     const userInput = document.getElementById('user-input');
//     const chatBox = document.getElementById('chat-box');

//     const sendMessage = async () => {
//         const question = userInput.value.trim();
//         if (!question) return;

//         addMessage(question, 'user');
//         userInput.value = '';

//         const thinkingMessage = addMessage('Pensando...', 'assistant', true);

//         try {
//             const response = await fetch('/ask', {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({ question: question })
//             });

//             if (!response.ok) {
//                 throw new Error('Error en la respuesta del servidor.');
//             }

//             const data = await response.json();
            
//             // Eliminamos el mensaje de "Pensando..."
//             chatBox.removeChild(thinkingMessage);

//             // --- INICIO DE LA MEJORA ---
//             // Si el servidor nos envió un contexto, lo mostramos.
//             if (data.context) {
//                 addContextBlock(data.context);
//             }
//             // --- FIN DE LA MEJORA ---

//             // Mostramos la respuesta final de la IA
//             addMessage(data.response, 'assistant');

//         } catch (error) {
//             console.error('Error:', error);
//             thinkingMessage.innerText = 'Lo siento, hubo un error al contactar al asistente.';
//         }
//     };

//     const addMessage = (text, sender, isThinking = false) => {
//         const messageElement = document.createElement('div');
//         messageElement.classList.add('message', `${sender}-message`);
//         messageElement.innerText = text;
//         if (isThinking) {
//             messageElement.classList.add('thinking');
//         }
//         chatBox.appendChild(messageElement);
//         chatBox.scrollTop = chatBox.scrollHeight;
//         return messageElement;
//     };

//     // --- INICIO DE LA NUEVA FUNCIÓN ---
//     // Esta función crea el bloque visual para el contexto.
//     const addContextBlock = (contextText) => {
//         const contextElement = document.createElement('div');
//         contextElement.classList.add('context-block');
        
//         const title = document.createElement('h4');
//         title.innerText = 'Fuente de la Información (Contexto del Documento)';
        
//         const content = document.createElement('p');
//         // Limpiamos el texto para que sea más legible
//         const cleanContext = contextText.replace(/Fuente:.*?::/, '').trim();
//         content.innerText = cleanContext;

//         contextElement.appendChild(title);
//         contextElement.appendChild(content);
//         chatBox.appendChild(contextElement);
//     };
//     // --- FIN DE LA NUEVA FUNCIÓN ---

//     sendBtn.addEventListener('click', sendMessage);
//     userInput.addEventListener('keypress', (e) => {
//         if (e.key === 'Enter') {
//             sendMessage();
//         }
//     });
// });

// =============================================================

// document.addEventListener('DOMContentLoaded', () => {
//     const chatContainer = document.getElementById('chat-container');
//     if (!chatContainer) {
//         return;
//     }

//     const sendBtn = document.getElementById('send-btn');
//     const userInput = document.getElementById('user-input');
//     const chatBox = document.getElementById('chat-box');

//     const sendMessage = async () => {
//         const question = userInput.value.trim();
//         if (!question) return;

//         addMessage(question, 'user');
//         userInput.value = '';
//         userInput.disabled = true;
//         sendBtn.disabled = true;

//         const thinkingMessage = addMessage('LexIA está consultando la Biblioteca Jurídica...', 'assistant', true);

//         try {
//             // La ruta /ask ahora apunta a la nueva lógica en assistant/routes.py
//             const response = await fetch('/ask', {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({ question: question })
//             });

//             // Eliminamos el mensaje de "Pensando..."
//             chatBox.removeChild(thinkingMessage);

//             if (!response.ok) {
//                 const errorData = await response.json();
//                 throw new Error(errorData.answer || 'Error en la respuesta del servidor.');
//             }

//             const data = await response.json();
            
//             // Mostramos la respuesta final de la IA junto con sus fuentes
//             addMessage(data.answer, 'assistant', false, data.sources);

//         } catch (error) {
//             console.error('Error:', error);
//             // Si hubo un error, lo mostramos en el chat
//             addMessage(`Lo siento, hubo un error: ${error.message}`, 'assistant');
//         } finally {
//             userInput.disabled = false;
//             sendBtn.disabled = false;
//             userInput.focus();
//         }
//     };

//     // --- FUNCIÓN 'addMessage' MEJORADA ---
//     const addMessage = (text, sender, isThinking = false, sources = []) => {
//         const messageElement = document.createElement('div');
//         messageElement.classList.add('message', `${sender}-message`);
        
//         // Convertimos saltos de línea del texto de la IA a <br>
//         const formattedText = text.replace(/\n/g, '<br>');
//         messageElement.innerHTML = `<p>${formattedText}</p>`;
        
//         if (isThinking) {
//             messageElement.classList.add('thinking');
//         }

//         // Si la respuesta tiene fuentes, las añadimos en un bloque separado
//         if (sources && sources.length > 0) {
//             const sourcesDiv = document.createElement('div');
//             sourcesDiv.classList.add('sources-block');
//             let sourcesHTML = '<strong>Fuentes Consultadas en la Biblioteca:</strong><ul>';
//             sources.forEach(source => {
//                 sourcesHTML += `<li>${source}</li>`;
//             });
//             sourcesHTML += '</ul>';
//             messageElement.innerHTML += sourcesHTML;
//         }

//         chatBox.appendChild(messageElement);
//         chatBox.scrollTop = chatBox.scrollHeight;
//         return messageElement;
//     };

//     sendBtn.addEventListener('click', sendMessage);
//     userInput.addEventListener('keypress', (e) => {
//         if (e.key === 'Enter') {
//             sendMessage();
//         }
//     });
// });

// =======================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Verificamos que los elementos existan antes de continuar
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    if (!chatBox || !userInput || !sendBtn) {
        console.error("No se encontraron los elementos del chat en el DOM.");
        return;
    }

    // Guardamos el código SVG del avatar en una constante para reutilizarlo
    const avatarSVG = `<svg class="lexia-avatar-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" stroke="#333" stroke-width="1.5"/><path d="M12 16C13.4353 16 15.1187 15.2025 16 14.5C16.8813 13.7975 17 13.3333 17 12C17 10 16 9.5 16 9.5C16 9.5 15.5 10.5 12 10.5C8.5 10.5 8 9.5 8 9.5C8 9.5 7 10 7 12C7 13.3333 7.11875 13.7975 8 14.5C8.88125 15.2025 10.5647 16 12 16Z" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

    /**
     * Añade un mensaje al cuadro de chat.
     * @param {string} text - El contenido del mensaje.
     * @param {string} sender - 'user' o 'ai'.
     * @param {boolean} isThinking - Si es un mensaje de "pensando...".
     * @param {string[]} sources - Un array con las fuentes de la respuesta.
     * @returns {HTMLElement} El elemento del mensaje que se ha añadido.
     */
    const addMessage = (text, sender, isThinking = false, sources = []) => {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('message', `${sender}-message`);

        if (sender === 'ai') {
            // Estructura para los mensajes de la IA (con avatar)
            const avatarDiv = document.createElement('div');
            avatarDiv.classList.add('avatar');
            avatarDiv.innerHTML = avatarSVG;
            messageWrapper.appendChild(avatarDiv);

            const messageContentDiv = document.createElement('div');
            messageContentDiv.classList.add('message-content');
            
            const formattedText = text.replace(/\n/g, '<br>');
            messageContentDiv.innerHTML = `<p>${formattedText}</p>`;
            
            if (isThinking) {
                messageContentDiv.classList.add('thinking');
            }

            if (sources && sources.length > 0) {
                const sourcesDiv = document.createElement('div');
                sourcesDiv.classList.add('sources-block');
                let sourcesHTML = '<strong>Fuentes Consultadas:</strong><ul>';
                sources.forEach(source => {
                    sourcesHTML += `<li>${source}</li>`;
                });
                sourcesHTML += '</ul>';
                messageContentDiv.innerHTML += sourcesHTML;
            }
            
            messageWrapper.appendChild(messageContentDiv);
        } else {
            // Estructura simple para los mensajes del usuario
            const messageContentDiv = document.createElement('div');
            messageContentDiv.classList.add('message-content');
            messageContentDiv.innerHTML = `<p>${text}</p>`;
            messageWrapper.appendChild(messageContentDiv);
        }

        chatBox.appendChild(messageWrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
        return messageWrapper;
    };

    /**
     * Maneja el envío de un mensaje al backend y la recepción de la respuesta.
     */
    const handleSendMessage = async () => {
        const question = userInput.value.trim();
        if (!question) return;

        addMessage(question, 'user');
        userInput.value = '';
        userInput.disabled = true;
        sendBtn.disabled = true;

        const thinkingMessage = addMessage('LexIA está consultando...', 'ai', true);

        try {
            // --- ¡LA CORRECCIÓN MÁS IMPORTANTE ESTÁ AQUÍ! ---
            // La ruta es '/ask', sin '/api'. Esto debe coincidir con tu `routes.py`.
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });

            // Eliminamos el mensaje de "Pensando..." para reemplazarlo por la respuesta final
            chatBox.removeChild(thinkingMessage);

            // Si la respuesta no es OK (ej. error 500, 404), lanzamos un error
            if (!response.ok) {
                // Intentamos leer el error como JSON, si falla, es porque es un error HTML (como 404)
                try {
                    const errorData = await response.json();
                    throw new Error(errorData.answer || 'Ocurrió un error en el servidor.');
                } catch (e) {
                    throw new Error(`Error del servidor (código: ${response.status}). Revisa la consola de Flask.`);
                }
            }

            const data = await response.json();
            addMessage(data.answer, 'ai', false, data.sources);

        } catch (error) {
            console.error('Error en fetch:', error);
            
            // Nos aseguramos de que no queden mensajes de "pensando" si algo falla
            const existingThinkingMessage = chatBox.querySelector('.thinking');
            if (existingThinkingMessage) {
                chatBox.removeChild(existingThinkingMessage.parentElement);
            }
            
            addMessage(`Lo siento, ha ocurrido un error: ${error.message}`, 'ai');
        } finally {
            // Pase lo que pase, volvemos a habilitar el input
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    };

    // --- Event Listeners ---
    sendBtn.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });
});