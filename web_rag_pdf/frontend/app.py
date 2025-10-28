from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

BACKEND_API_URL = "http://localhost:8000/api"

@app.route('/')
def index():
    try:
        response = requests.get(f"{BACKEND_API_URL}/documents/")
        response.raise_for_status()
        documents = response.json()
    except requests.exceptions.RequestException as e:
        documents = []
        flash(f"Erro ao carregar documentos do backend: {e}", "error")

    session.setdefault('chat_history', {})
    return render_template('index.html', documents=documents)

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf_file' not in request.files:
        flash('Nenhum arquivo enviado!', 'error')
        return redirect(url_for('index'))

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        flash('Nenhum arquivo selecionado!', 'error')
        return redirect(url_for('index'))

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        try:
            files = {'file': (pdf_file.filename, pdf_file.read(), 'application/pdf')}
            response = requests.post(f"{BACKEND_API_URL}/upload-pdf/", files=files)
            response.raise_for_status()
            doc_info = response.json()
            flash(f'Documento "{doc_info["filename"]}" (ID: {doc_info["id"]}) enviado com sucesso!', 'success')
            return redirect(url_for('chat_document', doc_id=doc_info["id"]))
        except requests.exceptions.RequestException as e:
            flash(f"Erro ao enviar PDF: {e}", "error")
            return redirect(url_for('index'))
    else:
        flash('Formato de arquivo inválido. Por favor, envie um PDF.', 'error')
        return redirect(url_for('index'))

@app.route('/document/<int:doc_id>')
def chat_document(doc_id):
    try:
        response = requests.get(f"{BACKEND_API_URL}/documents/{doc_id}")
        response.raise_for_status()
        document = response.json()
    except requests.exceptions.RequestException as e:
        flash(f"Erro ao carregar documento: {e}", "error")
        return redirect(url_for('index'))

    chat_history = session.get('chat_history', {}).get(str(doc_id), [])
    return render_template('chat.html', document=document, chat_history=chat_history)

@app.route('/document/<int:doc_id>/ask', methods=['POST'])
def ask_document(doc_id):
    question = request.form.get('question')
    if not question:
        flash('Por favor, digite uma pergunta.', 'error')
        return redirect(url_for('chat_document', doc_id=doc_id))

    try:
        payload = {"document_id": doc_id, "question": question}
        response = requests.post(f"{BACKEND_API_URL}/ask-pdf/", json=payload)
        response.raise_for_status()
        chat_response = response.json()

        if 'chat_history' not in session:
            session['chat_history'] = {}
        
        if str(doc_id) not in session['chat_history']:
            session['chat_history'][str(doc_id)] = []
        
        session['chat_history'][str(doc_id)].append({
            'question': question,
            'answer': chat_response.get('answer', 'Nenhuma resposta fornecida.'),
            'source_chunks': chat_response.get('source_chunks', [])
        })
        session.modified = True

    except requests.exceptions.RequestException as e:
        flash(f"Erro ao perguntar ao documento: {e}", "error")

    return redirect(url_for('chat_document', doc_id=doc_id))

if __name__ == '__main__':
    app.run(debug=True, port=5001)