import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Schemes from "./pages/Schemes";
import About from "./pages/About";
import Contact from "./pages/Contact";
import FAQ from "./pages/FAQ";
import Resources from "./pages/Resources";
import NotFound from "./pages/NotFound";

import './index.css';
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/schemes" element={<Schemes />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/faq" element={<FAQ />} />
        <Route path="/resources" element={<Resources />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;