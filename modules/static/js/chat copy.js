// Espera a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    // Solo ejecuta el script si estamos en una página con el chat
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) {
        return;
    }

    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    // Función para enviar el mensaje
    const sendMessage = async () => {
        const question = userInput.value.trim();
        if (!question) return; // No enviar mensajes vacíos

        // Añadir el mensaje del usuario a la caja de chat
        addMessage(question, 'user');
        userInput.value = '';

        // Crear un placeholder para la respuesta del asistente
        const thinkingMessage = addMessage('Pensando...', 'assistant', true);

        try {
            // Llamar a la API de Flask
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor.');
            }

            const data = await response.json();
            
            // Actualizar el placeholder con la respuesta real
            thinkingMessage.innerText = data.response;

        } catch (error) {
            console.error('Error:', error);
            thinkingMessage.innerText = 'Lo siento, hubo un error al contactar al asistente.';
        }
    };

    // Función para añadir un mensaje al chat
    const addMessage = (text, sender, isThinking = false) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.innerText = text;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
        return messageElement; // Devuelve el elemento para poder modificarlo
    };

    // Event listeners para el botón y la tecla Enter
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});