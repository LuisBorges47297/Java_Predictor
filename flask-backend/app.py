from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
from feature_extraction import extract_unchecked_exceptions  # importa o código de extração de features

app = Flask(__name__)
CORS(app)  # Para aceitar chamadas do React


# Carrega o modelo treinado
model = joblib.load("models/modelo_random_forest.pkl") 
scaler = joblib.load("models/scaler.pkl")

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json()  # Lê os dados recebidos no body da requisição
    code = data.get("code", "")

    if not code.strip():
        return jsonify({"error": "Código vazio"}), 400

    # Extração das features
    features = extract_unchecked_exceptions(code)

    # Organiza as features para a previsão
    X = [[
        features["num_null_pointer"],
        features["num_array_index_out_of_bounds"],
        features["num_string_index_out_of_bounds"],
        features["num_arithmetic_exceptions"],
        features["num_class_cast_exceptions"],
        features["num_number_format_exceptions"],
        features["num_concurrent_modification_exceptions"]
    ]]
    
     # Faz a previsão
    X_scaled = scaler.transform(X)
    prediction = model.predict(X_scaled)
    
    # Converte o array numpy para um tipo serializável (lista)
    prediction_serializable = prediction.tolist()  # Converte para lista
    
    return jsonify({"prediction": prediction_serializable})

if __name__ == "__main__":
    app.run(debug=True)