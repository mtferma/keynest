import React, { useState } from "react";
import Navigation from "../components/Navigation";
import Footer from "../components/Footer";
import { API_URL } from "../config";
import "../styles/Generate.css";

function GeneratePage() {
  const [seed, setSeed] = useState("");
  const [syllableCount, setSyllableCount] = useState(5);
  const [includeNumbers, setIncludeNumbers] = useState(false);
  const [includeSymbols, setIncludeSymbols] = useState(false);
  const [password, setPassword] = useState("");
  const [associations, setAssociations] = useState([]);
  const [showAssociations, setShowAssociations] = useState(false);
  const [copyMessage, setCopyMessage] = useState("");

  const marks = [2, 3, 4, 5, 6];

  const handleSliderChange = (e) => {
    setSyllableCount(parseFloat(e.target.value));
  };

  const snapSlider = () => {
    setSyllableCount(Math.round(syllableCount));
  };

  const handleCheckboxToggle = (setter) => () => {
    setter((prev) => !prev);
  };

  const generatePassword = async () => {
    const response = await fetch(`${API_URL}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        syllables: syllableCount,
        numbers: includeNumbers,
        symbols: includeSymbols,
        seed: seed.trim(),
      }),
    });

    const data = await response.json();
    setPassword(data.password);
    setAssociations(data.associations || []);

    const newEntry = {
      password: data.password,
      timestamp: new Date().toISOString(),
    };
    const storedHistory = JSON.parse(localStorage.getItem("passwordHistory") || "[]");
    storedHistory.push(newEntry);
    localStorage.setItem("passwordHistory", JSON.stringify(storedHistory));
  };

  const copyToClipboard = () => {
    if (password) {
      navigator.clipboard.writeText(password).then(() => {
        setCopyMessage("Пароль скопирован!");
        setTimeout(() => setCopyMessage(""), 2000);
      });
    }
  };

  return (
    <div className="generate-page">
      <Navigation />
      <header className="header">
        <h1>Keynest</h1>
        <p className="main-subtitle" style={{ textAlign: "center", fontSize: "18px", marginBottom: "30px" }}>
          Запоминающиеся пароли. Безопасно. Просто.
        </p>
      </header>

      <div className="about-section">
        Keynest создаёт запоминающиеся пароли из слогов. Выбирай длину, добавляй цифры и символы — получай надёжный пароль.
      </div>

      <div className="password-display-container">
        <div className="password-display">{password || " "}</div>
        <button className="copy-button" onClick={copyToClipboard}>
          <img src="/copyIcon.png" alt="copy icon" />
        </button>
      </div>
      {copyMessage && <div className="copy-message">{copyMessage}</div>}

      {associations.length > 0 && (
        <div>
          <div className="associations-toggle" onClick={() => setShowAssociations(!showAssociations)}>
            <p className="associations-title">Ассоциации {showAssociations ? "▲" : "▼"}</p>
          </div>
          <div className={`associations-box ${showAssociations ? "open" : "closed"}`}>
            <ul>
              {associations.map((assoc, index) => (
                <li key={index}>{assoc}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="slider-section">
        <p>Количество слогов</p>
        <div className="slider-container">
          <input
            type="range"
            min="2"
            max="6"
            step="0.01"
            value={syllableCount}
            onChange={handleSliderChange}
            onMouseUp={snapSlider}
            onTouchEnd={snapSlider}
            className="slider"
            style={{ "--value": syllableCount }}
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
      </div>

      <div className="checkbox-container" onClick={handleCheckboxToggle(setIncludeNumbers)}>
        <input type="checkbox" checked={includeNumbers} onChange={() => {}} />
        <label>Добавить цифры</label>
      </div>

      <div className="checkbox-container" onClick={handleCheckboxToggle(setIncludeSymbols)}>
        <input type="checkbox" checked={includeSymbols} onChange={() => {}} />
        <label>Добавить символы</label>
      </div>

      <div className="seed-container">
        <label htmlFor="seed-input">Seed (необязательно):</label>
        <div className="tooltip-container">
          <span className="tooltip-icon">?</span>
          <div className="tooltip-text">
            Личный код (до 3 букв, только буквы). Добавляется в начало пароля и делает его уникальным. Используйте только буквы, без цифр и символов.
          </div>
        </div>
        <input
          id="seed-input"
          type="text"
          value={seed}
          onChange={(e) => setSeed(e.target.value)}
          className="seed-input"
        />
      </div>

      <button className="generate-button" onClick={generatePassword}>
        ГЕНЕРИРОВАТЬ
      </button>

      <Footer />
    </div>
  );
}

export default GeneratePage;