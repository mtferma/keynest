import React from "react";
import { NavLink } from "react-router-dom";
import "../styles/Navigation.css";

function Navigation() {
  return (
    <nav className="navbar">
      <NavLink to="/" className="nav-link" end>
        Главная
      </NavLink>
      <NavLink to="/generate" className="nav-link">
        Генератор
      </NavLink>
      <NavLink to="/check" className="nav-link">
        Проверка
      </NavLink>
      <NavLink to="/history" className="nav-link">
        История
      </NavLink>
    </nav>
  );
}

export default Navigation;