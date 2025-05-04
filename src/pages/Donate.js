import React, { useState } from "react";
import "../styles/Donate.css";
import Navigation from "../components/Navigation";

function Home() {
    return (
      <div className="main">
          <Navigation />
        <h1 className="main-title" >Keynest</h1>
        <p className="main-subtitle" style={{ textAlign: "center", fontSize: "18px", marginBottom: "30px" }}>
          Запоминающиеся пароли. Безопасно. Просто.
        </p>
  
        <section className="donate">
          <h2>Поддержать проект</h2>
          <p>По сколько наш проект является бесплатным, вы можете поддержать его по ссылке: *появится позже*</p>
        </section>

        <footer className="footer">
        <p>© 2025 Keynest</p>
        <a href="https://github.com/mtferma/keynest" target="_blank" rel="noopener noreferrer">GitHub</a> | 
        <a href="https://t.me/keynest_support" target="_blank" rel="noopener noreferrer">Telegram Support</a> | 
        <a href="http://localhost:3000/donate" target="_blank" rel="noopener noreferrer">Donate</a>  
      </footer>

      </div>
    );
  }
  
  export default Home;