from flask import Flask, request, jsonify, render_template
import requests
import logging
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract

app = Flask(__name__)

# Configurações da API do Gemini
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
API_KEY = os.getenv('GEMINI_API_KEY')
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 
# Configuração de upload de imagens
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a' # Append mode
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para processar imagem (OCR)
def process_image(file_path):
    try:
        # Process the image using OCR
        image = Image.open(file_path)
        image = image.convert('L') # Convert to grayscale
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logging.error(f"Error processing image: {e}", exc_info=True)
        raise

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        # Upload the image
        if 'imagem_log' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['imagem_log']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            text = process_image(file_path)
            return jsonify({'text': text})
        else:
            return jsonify({'error': 'File type not allowed'}), 400

    except Exception as e:
        logging.error(f"Error uploading image: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred while uploading the image.'}), 500

# Função para obter resposta da API do Gemini
def get_response_from_gemini(prompt):
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ],
        }
        response = requests.post(f"{API_ENDPOINT}?key={API_KEY}", headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logging.error(f"Error getting response from Gemini API: {e}", exc_info=True)
        raise

@app.route('/')
def index():
    return render_template('indexbeta.html')

@app.route('/analisar_log', methods=['POST'])
def analisar_log():
    try:
        # Check if 'imagem_log' is in request.files before accessing it
        if 'imagem_log' in request.files:
            imagem_log = request.files['imagem_log']
            if imagem_log and allowed_file(imagem_log.filename):
                filename = secure_filename(imagem_log.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagem_log.save(file_path)
                ocr_text = process_image(file_path)
            else:
                ocr_text = None 
        else:
            ocr_text = None

        tipo_log = request.form.get('tipo_log')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        gravidade = request.form.get('gravidade')
        conteudo_log = request.form.get('conteudo_log')
        fonte_dados = request.form.get('fonte_dados')

        # Construir prompt para o Gemini
        prompt = f"Analise o seguinte log:\n"
        prompt += f"Tipo de Log: {tipo_log}\n"
        prompt += f"Data de Início: {data_inicio}\n"
        prompt += f"Data de Fim: {data_fim}\n"
        prompt += f"Gravidade: {gravidade}\n"
        prompt += f"Fonte de Dados: {fonte_dados}\n" if fonte_dados else ""
        prompt += f"Conteúdo do Log:\n{conteudo_log}\n"
        prompt += f"Texto extraído da imagem (OCR): {ocr_text}\n" if ocr_text else ""
        prompt += "Identifique padrões, anomalias e forneça insights sobre possíveis problemas ou melhorias. Gere um relatorio com marcadores de tempo."

        # Obter resposta do Gemini
        gemini_response = get_response_from_gemini(prompt)

        # Processar a resposta do Gemini
        if 'candidates' in gemini_response and gemini_response['candidates']:
            analysis = gemini_response['candidates'][0]['content']['parts'][0]['text']
            logging.info("Log analyzed successfully")
            return jsonify({'success': True, 'analysis': analysis})
        else:
            logging.warning("No candidates found in Gemini API response")
            return jsonify({'success': False, 'error': 'No analysis available from Gemini API.'})

    except Exception as e:
        logging.error(f"Error analyzing log: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An error occurred while analyzing the log.'}), 500

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    app.run(host="0.0.0.0", debug=debug_mode, port=5000)