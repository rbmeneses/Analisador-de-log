from flask import Flask, request, jsonify, render_template
import requests
import logging
from datetime import datetime
import os

app = Flask(__name__)

# Configurações básicas
ANYTHING_LLM_URL = "http://localhost:3001/api/v1/workspace/logs/chat"
AUTH_TOKEN = "Y0S7Z8X-5P84THA-G7EQBD1-ZTFN6CT"

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'
)

def get_response_from_anything_llm(prompt):
    """Função para obter resposta da API AnythingLLM"""
    try:
        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "message": prompt,
            "mode": "chat",
            "sessionId": datetime.now().strftime("%Y%m%d%H%M%S")
        }

        response = requests.post(ANYTHING_LLM_URL, json=data, headers=headers)
        response.raise_for_status()
        return response.json().get("textResponse", "Não foi possível obter uma análise.")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na API AnythingLLM: {str(e)}")
        return "Erro ao conectar com o serviço de análise."
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        return "Ocorreu um erro durante a análise."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analisar_log', methods=['POST'])
def analisar_log():
    try:
        data = request.json
        
        # Validação básica dos dados
        required_fields = ['tipo_log', 'data_inicio', 'data_fim', 'gravidade', 'conteudo_log']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Dados incompletos"}), 400

        if not data['conteudo_log'].strip():
            return jsonify({"error": "Conteúdo do log está vazio"}), 400

        # Capturar fonte de dados opcional
        fonte_dados = data.get('fonte_dados', None)

        # Criar prompt para análise
        prompt = f"""Análise do log:
        Tipo: {data['tipo_log']}
        Período: {data['data_inicio']} a {data['data_fim']}
        Gravidade: {data['gravidade']}
        {"Fonte de Dados: " + fonte_dados if fonte_dados else ""}
        
        Log:
        {data['conteudo_log']}
        
        Por favor, forneça:
        1. Resumo dos eventos principais
        2. Possíveis problemas identificados
        3. Recomendações
        """

        # Obter análise
        analysis = get_response_from_anything_llm(prompt)
        
        return jsonify({
            "success": True,
            "message": "Análise concluída com sucesso!",
            "analysis": analysis
        })

    except Exception as e:
        logging.error(f"Erro no endpoint analisar_log: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Erro ao processar a análise"
        }), 500

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    app.run(debug=debug_mode, port=5000)
