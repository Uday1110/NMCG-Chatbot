# main.py

import random
import json
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import NeuralNet  # Adjust the import path as needed
from nltk_utils import bag_of_words, tokenize, stem  # Adjust the import path as needed

app = Flask(__name__)
CORS(app)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"

def chat(user_input, model):
    sentence = tokenize(user_input)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    else:
        return "As of now I can not answer it."
    return "As of now I can not answer it."

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        data = request.json
        message = data.get('message')

        if not message:
            return jsonify({"error": "Message not provided"})

        response = chat(message, model)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
