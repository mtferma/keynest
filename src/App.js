import React from "react";
import { HashRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Generate from "./pages/Generate";
import Donate from "./pages/Donate";
import Check from "./pages/Check";
import History from "./pages/History";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/generate" element={<Generate />} />
        <Route path="/donate" element={<Donate />} />
        <Route path="/check" element={<Check />} />
        <Route path="/history" element={<History />} />
      </Routes>
    </Router>
  );
}

export default App;