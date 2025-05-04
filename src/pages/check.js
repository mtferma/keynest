import React, { useState } from "react";
import Navigation from "../components/Navigation";
import "../styles/check.css";

function Check() {
  const [password, setPassword] = useState("");
  const [result, setResult] = useState(null);

  const handleCheck = async () => {
    const response = await fetch(`${API_URL}/generate`, {
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
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button onClick={handleCheck}>Проверить</button>
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
      <footer className="footer">
        <p>© 2025 Keynest</p>
        <a href="https://github.com/mtferma/keynest" target="_blank" rel="noopener noreferrer">GitHub</a> | 
        <a href="https://t.me/keynest_support" target="_blank" rel="noopener noreferrer">Telegram Support</a> | 
        <a href="http://localhost:3000/donate" target="_blank" rel="noopener noreferrer">Donate</a>    
      </footer>
    </div>
  );
}

export default Check;
