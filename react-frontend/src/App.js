import './App.css';
import './index.css';
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [code, setCode] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(''); // Novo estado para o erro

  const handleCodeChange = (event) => {
    setCode(event.target.value);
    setError(''); // Limpa erro ao alterar código
    setPrediction(null); // Limpa resultado anterior
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setError('');
      const response = await axios.post('http://localhost:5000/api/predict', { code });
      setPrediction(response.data.prediction[0]); // Assume que vem como lista
    } catch (error) {
      if (error.response && error.response.data?.error) {
        setError(error.response.data.error); // Exibe mensagem do Flask (ex: "Código vazio")
      } else {
        setError('Erro ao comunicar com o servidor.');
      }
      setPrediction(null);
    }
  };

  return (
    <div className="App">
      <h1>
        <img src="/java.webp" alt="Java" style={{ height: '50px', verticalAlign: 'middle', marginRight: '10px' }} />
        Preditor de Bugs em Código Java
      </h1>

      <form onSubmit={handleSubmit}>
        <textarea
          value={code}
          onChange={handleCodeChange}
          rows="20"
          cols="50"
          placeholder="Cole o seu código Java aqui"
        />
        <br />
        <button type="submit">Prever Bugs</button>
      </form>

      {/* Exibir erro se existir */}
      {error && <div className="error-message" style={{ color: 'red', marginTop: '10px' }}>{error}</div>}

      {/* Exibir previsão se não houver erro */}
      {prediction && (
        <div
          className={`prediction-result ${prediction === 'No_bugs' ? 'success' : 'error'}`}
          style={{ marginTop: '10px' }}
        >
          <strong>Resultado da Previsão: </strong>{prediction}
        </div>
      )}
    </div>
  );
}

export default App;
