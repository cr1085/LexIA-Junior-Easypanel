document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingStatus = document.getElementById('loading-status');
    const fileInput = document.getElementById('file');
    const progressBar = document.getElementById('progress-bar');
    const progressPercentage = document.getElementById('progress-percentage');
    
    if (!uploadForm) return;

    let progressInterval;
    let statusInterval;

    const statuses = [
        "Iniciando extracción de texto...",
        "Analizando estructura del documento...",
        "Chunking semántico en proceso...",
        "Generando vectores de alta dimensión...",
        "Indexando en base de datos FAISS...",
        "Optimizando el índice para búsqueda...",
        "Finalizando proceso..."
    ];

    const startProgressSimulation = () => {
        let progress = 0;
        let statusIndex = 0;
        
        // Actualizar el texto de estado periódicamente
        loadingStatus.innerText = statuses[statusIndex];
        statusInterval = setInterval(() => {
            statusIndex = (statusIndex + 1) % statuses.length;
            loadingStatus.innerText = statuses[statusIndex];
        }, 2000);

        // Actualizar la barra de progreso de forma no lineal
        progressInterval = setInterval(() => {
            if (progress < 50) {
                progress += Math.random() * 5; // Avance rápido al inicio
            } else if (progress < 90) {
                progress += Math.random() * 1.5; // Avance lento en la parte media
            } else if (progress < 99) {
                progress += 0.1; // Avance muy lento al final
            }
            
            if (progress > 99) progress = 99; // No pasar del 99% hasta que termine

            progressBar.style.width = `${progress}%`;
            progressPercentage.innerText = `${Math.floor(progress)}%`;

        }, 300); // Intervalo de actualización
    };

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        if (fileInput.files.length === 0) {
            alert('Por favor, selecciona un archivo antes de continuar.');
            return;
        }

        loadingOverlay.style.display = 'flex';
        progressBar.style.width = '0%';
        progressPercentage.innerText = '0%';

        startProgressSimulation(); // Inicia la simulación

        const formData = new FormData(uploadForm);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                // Al terminar, forzamos el 100% y mostramos el mensaje final
                clearInterval(progressInterval);
                clearInterval(statusInterval);
                progressBar.style.width = '100%';
                progressPercentage.innerText = '100%';
                loadingStatus.innerText = "¡Proceso completado!";
                
                setTimeout(() => {
                    loadingOverlay.style.display = 'none';
                    alert(`Éxito: ${result.message}`);
                    uploadForm.reset();
                }, 1000); // Pequeña pausa para que el usuario vea el 100%

            } else {
                throw new Error(result.message || 'Ocurrió un error desconocido.');
            }

        } catch (error) {
            clearInterval(progressInterval);
            clearInterval(statusInterval);
            loadingOverlay.style.display = 'none';
            alert(`Error: ${error.message}`);
        }
    });
});