import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Schemes from "./pages/Schemes";
import About from "./pages/About";
import Contact from "./pages/Contact";
import FAQ from "./pages/FAQ";
import Resources from "./pages/Resources";
import NotFound from "./pages/NotFound";
import Terms from "./pages/Terms";
import Privacy from "./pages/Privacy";
import Report_Mis from "./pages/Report_Mis";
import ChatbotPage from "./pages/ChatbotPage";
import SchemeDetails from './pages/SchemeDetails';

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
        <Route path="/terms" element={<Terms />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/report-misinformation" element={<Report_Mis />} />
        <Route path="/chatbot" element={<ChatbotPage />} />
        <Route path="/schemes/:id" element={<SchemeDetails />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;