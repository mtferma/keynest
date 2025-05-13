import React, { useState, useEffect } from "react";
import Navigation from "../components/Navigation";
import Footer from "../components/Footer";
import "../styles/History.css";

function HistoryPage() {
  const [passwordHistory, setPasswordHistory] = useState([]);
  const [visiblePasswords, setVisiblePasswords] = useState({});

  useEffect(() => {
    const storedHistory = JSON.parse(localStorage.getItem("passwordHistory") || "[]");
    setPasswordHistory(storedHistory);
  }, []);

  const togglePasswordVisibility = (index) => {
    setVisiblePasswords((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const clearHistory = () => {
    if (window.confirm("Вы уверены, что хотите очистить всю историю паролей?")) {
      localStorage.removeItem("passwordHistory");
      setPasswordHistory([]);
      setVisiblePasswords({});
    }
  };

  const groupedHistory = passwordHistory.reduce((acc, entry) => {
    const date = new Date(entry.timestamp).toLocaleDateString("ru-RU", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
    if (!acc[date]) acc[date] = [];
    acc[date].push(entry);
    return acc;
  }, {});

  return (
    <div className="history-page">
      <Navigation />
      <header className="header">
        <h1>Keynest</h1>
      </header>
      <p className="main-subtitle" style={{ textAlign: "center", fontSize: "18px", marginBottom: "30px" }}>
          Запоминающиеся пароли. Безопасно. Просто.
        </p>
      <div className="about-section">
        Все пароли сохраняются локально на вашем устройстве. Никто, кроме вас, не имеет к ним доступа.
        <button className="clear-button" onClick={clearHistory}>
          Очистить историю
        </button>
      </div>

      {Object.keys(groupedHistory).length === 0 ? (
        <div className="empty-message">История паролей пуста</div>
      ) : (
        Object.entries(groupedHistory).map(([date, entries]) => (
          <div key={date} className="date-section">
            <h2 className="date-title">{date}</h2>
            <div className="password-table">
              {entries.map((entry, index) => (
                <div key={index} className="password-row">
                  <div className="time">
                    {new Date(entry.timestamp).toLocaleTimeString("ru-RU", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </div>
                  <div className="password-container">
                    <span className="password">
                      {visiblePasswords[index] ? entry.password : "••••••••"}
                    </span>
                    <button
                      className="toggle-button"
                      onClick={() => togglePasswordVisibility(index)}
                    >
                      {visiblePasswords[index] ? "Скрыть" : "Показать"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))
      )}

      <Footer />
    </div>
  );
}

export default HistoryPage;