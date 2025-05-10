import React, { useState } from "react";
import "../styles/Donate.css";
import Footer from "../components/Footer";
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
        <Footer />
      </div>
    );
  }
  
  export default Home;