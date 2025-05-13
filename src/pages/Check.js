import React, { useState } from "react";
import Navigation from "../components/Navigation";
import "../styles/Check.css";
import { API_URL } from '../config';
import Footer from "../components/Footer";

function Check() {
  const [password, setPassword] = useState("");
  const [result, setResult] = useState(null);

  const handleCheck = async () => {
    const response = await fetch(`${API_URL}/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });

  const data = await response.json();
  setResult(data);
};

  return (
    <div className="check-page">
      <Navigation />
      <h1>Keynest</h1>
      <p className="main-subtitle" style={{ textAlign: "center", fontSize: "18px", marginBottom: "30px" }}>
          Запоминающиеся пароли. Безопасно. Просто.
      </p>
      <div className="check-form">
        <input
          placeholder="Введите пароль"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <button onClick={handleCheck}>Проверить</button>
        <div className="tooltip-container">
          <span className="tooltip-icon">?</span>
            <div className="tooltip-text">
              Мы проверяем пароль по базе утечек, оцениваем его длину, наличие цифр, символов и шаблонов.
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="check-result">
          <p><strong>Сложность:</strong> {result.strength}</p>
          <p><strong>Время взлома:</strong> {result.time}</p>
          {result.suggestion && (
            <p className="suggestion">
              {result.suggestion}{" "} 
              <a href="/generate">Советуем Генератор</a> или{" "}
              <a href="#extension">расширение</a>.
            </p>
          )}
        </div>
      )}
      <Footer />
    </div>
  );
}

export default Check;
