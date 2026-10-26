import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import StockDetail from "./pages/StockDetail";
import Watchlist from "./pages/Watchlist";
import About from "./pages/About";
import ModelPerformance from "./pages/ModelPerformance";
import AuthPage from "./pages/AuthPage";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/stock/:ticker" element={<StockDetail />} />
          <Route path="/watchlist" element={<Watchlist />} />
          <Route path="/performance" element={<ModelPerformance />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<AuthPage mode="login" />} />
          <Route path="/signup" element={<AuthPage mode="signup" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
