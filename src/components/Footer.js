import React from "react";
import "../styles/Footer.css"; // если нужно

function Footer() {
  return (
    <footer className="footer">
      <p>© 2025 Keynest</p>
      <a href="https://github.com/mtferma/keynest" target="_blank" rel="noopener noreferrer">GitHub</a> | 
      <a href="https://t.me/keynest_support" target="_blank" rel="noopener noreferrer">Telegram Support</a> | 
      <a href="/donate">Donate</a>
    </footer>
  );
}

export default Footer;
