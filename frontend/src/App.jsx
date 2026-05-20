import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Schemes from "./pages/Schemes";
import About from "./pages/About";
import Contact from "./pages/Contact";
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/schemes" element={<Schemes />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;