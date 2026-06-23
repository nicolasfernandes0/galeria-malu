import io
import os
import traceback
from flask import Flask, jsonify, send_file, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

app = Flask(__name__, template_folder='.')

# CONFIGURAÇÕES DO GOOGLE (Versão de Leitura com Conta de Serviço)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'credenciais.json'
FOLDER_ID = '1au7OjN-qA-ftx-V1lBKmurMF4Kb7heQw' # ID corrigido sem o ?hl=pt-br

def get_drive_service():
    # Carrega as credenciais do arquivo JSON do robô
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

# ROTA 1: Abre a página principal do sistema
@app.route('/')
def index():
    return render_template('index.html')

# ROTA 2: API que lista as fotos da pasta
@app.route('/api/fotos', methods=['GET'])
def listar_fotos():
    try:
        service = get_drive_service()
        query = f"'{FOLDER_ID}' in parents and mimeType contains 'image/' and trashed = false"
        
        results = service.files().list(
            q=query, fields="files(id, name, mimeType)").execute()
        items = results.get('files', [])
        
        return jsonify({"status": "sucesso", "dados": items})
        
    except Exception as e:
        print("\n" + "="*40)
        print("🚨 ERRO AO CONECTAR COM O GOOGLE DRIVE 🚨")
        traceback.print_exc() 
        print("="*40 + "\n")
        return jsonify({"status": "erro", "mensagem": repr(e)})

# ROTA 3: API Proxy que baixa a imagem do Drive e envia para o HTML
@app.route('/api/foto/<file_id>', methods=['GET'])
def obter_foto(file_id):
    try:
        service = get_drive_service()
        request = service.files().get_media(fileId=file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        return send_file(fh, mimetype='image/jpeg')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)