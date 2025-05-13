import React from "react";
import { Link } from "react-router-dom";
import Navigation from "../components/Navigation";
import Footer from "../components/Footer";
import "../styles/Home.css";

function HomePage() {
  return (
    <div className="home">
      <Navigation />
      <header className="home-header">
        <h1 className="home-title">Keynest</h1>
        <p className="main-subtitle" style={{ textAlign: "center", fontSize: "18px", marginBottom: "30px" }}>
          Запоминающиеся пароли. Безопасно. Просто.
        </p>
      </header>

      <section className="home-section">
        <h2>О проекте</h2>
        <p>
          Keynest — это генератор надёжных, но легко запоминающихся паролей. Вместо случайного набора символов мы используем читаемые слоги, к которым можно добавить цифры и символы по желанию. Это идеальный баланс между удобством и безопасностью. Забудь про сложные R#1p@oL7, которые невозможно запомнить и ввести без копипаста.
        </p>
      </section>

      <section className="home-section">
        <h2>Попробуй</h2>
        <div className="home-buttons">
          <Link to="/generate" className="home-button">Сгенерировать пароль</Link>
          <Link to="/check" className="home-button">Проверить сложность пароля</Link>
        </div>
      </section>

      <section className="home-section">
        <h2>Расширение для браузера</h2>
        <p>
          Установи расширение Keynest для Chrome. Оно автоматически предложит надёжный пароль при регистрации на сайтах. Все пароли хранятся локально в твоём браузере — никаких внешних серверов, никакого риска утечки данных.
        </p>
      </section>

      <section className="home-section">
        <h2>Надёжно и безопасно</h2>
        <p>
          Мы не сохраняем ни один из сгенерированных или проверяемых паролей. Всё происходит локально — в твоём браузере или через наше расширение. Генерация паролей использует открытый API, а исходный код проекта доступен на GitHub — ты можешь лично убедиться в прозрачности и безопасности. Keynest — это твой контроль над безопасностью.        </p>
      </section>

      <Footer />
    </div>
  );
}

export default HomePage;
