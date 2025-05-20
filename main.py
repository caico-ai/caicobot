# chatbot-caico.py - Assistants API Integration

from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Configurações
openai.api_key = os.environ.get("OPENAI_API_KEY")
assistant_id = os.environ.get("OPENAI_ASSISTANT_ID")

# Inicializa cache de thread_id por sessão
thread_ids = {}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    mensagem = data['message']
    session_id = data.get("session_id", "default")

    try:
        # Cria uma thread nova por sessão (se não existir)
        if session_id not in thread_ids:
            thread = openai.beta.threads.create()
            thread_ids[session_id] = thread.id

        thread_id = thread_ids[session_id]

        # Adiciona a mensagem do usuário
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=mensagem
        )

        # Executa o Assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # Aguarda a execução finalizar
        while True:
            status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if status.status == "completed":
                break
            elif status.status == "failed":
                return jsonify({"error": "Failed to complete run."}), 500

        # Busca a resposta
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                resposta = msg.content[0].text.value
                return jsonify({'response': resposta})

        return jsonify({'response': 'Sem resposta.'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
