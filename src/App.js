import React from "react";
import { HashRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Generate from "./pages/Generate";
import Donate from "./pages/Donate"
import Check from "./pages/check";

function App() {
  const API_URL = "https://keynest.onrender.com";
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/generate" element={<Generate />} />
        <Route path="/donate" element={<Donate />} />        
        <Route path="/check" element={<Check />} />
      </Routes>
    </Router>
  );
}

export default App;
