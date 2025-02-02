## Ferramenta de Análise Inteligente de Logs com Gemini e OCR
# Descrição
Esta ferramenta utiliza o poder da API Gemini do Google e do Tesseract OCR para analisar logs de diferentes tipos (aplicativo, sistema, segurança, etc.). A ferramenta extrai informações de logs (em texto ou imagem) e gera um relatório detalhado com insights, padrões e anomalias identificados, auxiliando na detecção de problemas e sugestões de melhorias de segurança.

# Funcionalidades
Análise de logs de texto e imagens.
Extração de dados de logs via OCR.
Identificação de padrões e anomalias.
Geração de relatórios detalhados com insights e sugestões de melhorias.
Interface web intuitiva para interação com o usuário.
# Requisitos
Linguagem de Programação: Python 3.7 ou superior
Bibliotecas:
Flask
requests
Pillow (PIL)
pytesseract
google-cloud-aiplatform
API Key:
Uma chave de API válida para o Gemini.
Tesseract OCR:
Instalação do Tesseract OCR no sistema.
Configurar a variável de ambiente PATH para incluir o diretório de instalação do Tesseract OCR.
# Instalação
Clonar o repositório do GitHub.
Criar um ambiente virtual Python.
Instalar as dependências do projeto usando o requirements.txt.
Configurar a variável de ambiente GEMINI_API_KEY com a sua chave de API.
Executar o script Python app.py.
# Uso
Acesse a interface web em http://localhost:5000.
Preencha o formulário com os dados do log, incluindo a opção de carregar uma imagem.
Clique em "Analisar Log".
O resultado da análise, gerado pela API Gemini, será exibido na página.


## Limitações
A precisão da análise depende da qualidade da imagem do log e da capacidade do Tesseract OCR em extrair o texto corretamente.
O modelo Gemini pode ter dificuldades em analisar logs com formatos complexos (Ajuste os dados antes do envio) ou não estruturados.
# Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests para melhorar a ferramenta.

Licença
MIT License

Contato
Ricardo B Meneses - rbmeneses@gmail.com
