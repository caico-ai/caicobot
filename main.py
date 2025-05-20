
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)  # Enable CORS

# Pegando a chave da OpenAI de variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    message = data['message']

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é CaicoBot, assistente da Caico.ai. Especialista em automações de marketing, vendas e atendimento. Atenda com clareza, seja objetivo e capture leads quando possível."},
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        chat_response = response.choices[0].message['content'].strip()
        return jsonify({'response': chat_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)

