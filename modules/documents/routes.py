# from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app # <-- 1. IMPORTAR current_app
# from flask_login import login_required
# import os
# from werkzeug.utils import secure_filename
# # Quitamos la importación directa de RAGProcessor

# documents_bp = Blueprint('documents', __name__)
# # rag_processor = RAGProcessor() # <-- 2. BORRAR ESTA LÍNEA

# UPLOAD_FOLDER = 'instance/uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # En modules/documents/routes.py

# @documents_bp.route('/upload', methods=['GET', 'POST'])
# @login_required
# def upload_file():
#     if request.method == 'POST':
#         # 1. Verificar si la parte 'file' está en la solicitud
#         if 'file' not in request.files:
#             flash('No se encontró la parte del archivo', 'error')
#             return redirect(request.url)
        
#         # 2. Obtener el objeto del archivo (esta es la línea que probablemente faltaba)
#         file = request.files['file']
        
#         # 3. Verificar si el usuario no seleccionó ningún archivo
#         if file.filename == '':
#             flash('No se seleccionó ningún archivo', 'error')
#             return redirect(request.url)
            
#         # 4. Ahora sí, procesar el archivo porque la variable 'file' ya existe
#         if file and file.filename.endswith('.pdf'):
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(UPLOAD_FOLDER, filename)
#             file.save(filepath)
            
#             try:
#                 current_app.rag_processor.process_document(filepath, filename)
#                 flash(f'¡Archivo "{filename}" cargado y procesado exitosamente!', 'success')
#             except Exception as e:
#                 flash(f'Error al procesar el archivo: {e}', 'error')

#             return redirect(url_for('documents.upload_file'))
#         else:
#             flash('Por favor, sube un archivo con formato .pdf', 'error')
#             return redirect(request.url)

#     return render_template('upload.html')


from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
import os
from werkzeug.utils import secure_filename

documents_bp = Blueprint('documents', __name__)
UPLOAD_FOLDER = 'instance/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@documents_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No se encontró la parte del archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No se seleccionó ningún archivo'}), 400
            
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                # El procesamiento RAG que puede tardar
                current_app.rag_processor.process_document(filepath, filename)
                message = f'¡Archivo "{filename}" cargado y procesado exitosamente!'
                return jsonify({'status': 'success', 'message': message}), 200
            except Exception as e:
                # Capturamos cualquier error durante el procesamiento
                print(f"ERROR DURANTE EL PROCESAMIENTO RAG: {e}")
                message = f'Error al procesar el archivo: {str(e)}'
                return jsonify({'status': 'error', 'message': message}), 500
        else:
            return jsonify({'status': 'error', 'message': 'Formato de archivo no válido. Por favor, sube un PDF.'}), 400

    # La petición GET simplemente muestra la página
    return render_template('upload.html')