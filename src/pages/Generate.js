import React, { useState } from "react";
import "../styles/Generate.css";
import Navigation from "../components/Navigation";

function App() {
  const [value, setValue] = useState(5);
  const [includeNumbers, setIncludeNumbers] = useState(false);
  const [includeSymbols, setIncludeSymbols] = useState(false);
  const [password, setPassword] = useState("");
  const [associations, setAssociations] = useState([]);
  const [showAssociations, setShowAssociations] = useState(false);

  const marks = [2, 3, 4, 5, 6];

  const handleChange = (e) => {
    setValue(parseFloat(e.target.value));
  };

  const handleMouseUp = () => {
    const snapped = Math.round(value);
    setValue(snapped);
  };

  const generatePassword = async () => {
    try {
      // Запрос на сервер для генерации пароля
      const response = await fetch("http://localhost:5000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          syllables: value,
          numbers: includeNumbers,
          symbols: includeSymbols,
        }),
      });
  
      const data = await response.json();
  
      setPassword(data.password);
      setAssociations(data.associations || []);
    } catch (error) {
      console.error("Ошибка генерации:", error);
    }
  };
  

  const copyToClipboard = () => {
    if (password) {
      navigator.clipboard.writeText(password);
      alert("Пароль скопирован!");
    }
  };

  return (
    <div className="App">
          <Navigation />

      <h1>Keynest</h1>
      <p className="home-subtitle" style={{ textAlign: "center", fontSize: "18px", marginBottom: "30px" }}>
        Запоминающиеся пароли. Безопасно. Просто.
      </p>
      <div className="about-section">
        Keynest создаёт запоминающиеся пароли из слогов. Выбирай длину, добавляй цифры и символы — получай надёжный пароль.
      </div>

      <div className="password-display-container">
        <div className="password-display">{password || " "}</div>
        <button className="copy-button" onClick={copyToClipboard}>
          <img src="/copyIcon.png" alt="copy icon" />
        </button>
      </div>
      {associations.length > 0 && (
  <div>
    <div
      className="associations-toggle"
      onClick={() => setShowAssociations(!showAssociations)}
    >
      <p style={{ fontWeight: 700, fontSize: 20, cursor: "pointer" }}>
        Ассоциации {showAssociations ? "▲" : "▼"}
      </p>
    </div>

    <div
      className={`associations-box ${showAssociations ? "open" : "closed"}`}
    >
      <ul>
        {associations.map((assoc, index) => (
          <li key={index}>{assoc}</li>
        ))}
      </ul>
    </div>
  </div>
)}


      <p>Количество слогов</p>
      <div className="slider-container">
        <input
          type="range"
          min="2"
          max="6"
          step="0.01"
          value={value}
          onChange={handleChange}
          onMouseUp={handleMouseUp}
          onTouchEnd={handleMouseUp}
          className="slider"
          style={{ '--value': value }}
        />

        <div className="marks">
          {marks.map((mark) => (
            <div key={mark} className="mark">
              <div className="dot" />
              <span>{mark}</span>
            </div>
          ))}
        </div>
      </div>

      <div
        className="checkbox-container"
        onClick={() => setIncludeNumbers(!includeNumbers)}
      >
        <input
          type="checkbox"
          checked={includeNumbers}
          onChange={() => setIncludeNumbers(!includeNumbers)}
        />
        <label>Добавить цифры</label>
      </div>

      <div
        className="checkbox-container"
        onClick={() => setIncludeSymbols(!includeSymbols)}
      >
        <input
          type="checkbox"
          checked={includeSymbols}
          onChange={() => setIncludeSymbols(!includeSymbols)}
        />
        <label>Добавить символы</label>
      </div>

      <button className="generate-button" onClick={generatePassword}>
        ГЕНЕРИРОВАТЬ
      </button>
      <footer className="footer">
        <p>© 2025 Keynest</p>
        <a href="https://github.com/mtferma/keynest" target="_blank" rel="noopener noreferrer">GitHub</a> | 
        <a href="https://t.me/keynest_support" target="_blank" rel="noopener noreferrer">Telegram Support</a> | 
        <a href="http://localhost:3000/donate" target="_blank" rel="noopener noreferrer">Donate</a>    
      </footer>
    </div>
  );
}

export default App;
