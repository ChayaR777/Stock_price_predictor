import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">📈 Stock Predictor</div>
      <div className="navbar-links">
        <NavLink to="/" end className={({ isActive }) => isActive ? "nav-active" : ""}>Dashboard</NavLink>
        <NavLink to="/watchlist" className={({ isActive }) => isActive ? "nav-active" : ""}>Watchlist</NavLink>
        <NavLink to="/performance" className={({ isActive }) => isActive ? "nav-active" : ""}>Model Performance</NavLink>
        <NavLink to="/about" className={({ isActive }) => isActive ? "nav-active" : ""}>About</NavLink>

        {user ? (
          <>
            <span className="nav-user">{user.email}</span>
            <button className="nav-logout" onClick={handleLogout}>Log out</button>
          </>
        ) : (
          <>
            <NavLink to="/login" className={({ isActive }) => isActive ? "nav-active" : ""}>Log in</NavLink>
            <NavLink to="/signup" className={({ isActive }) => isActive ? "nav-active" : ""}>Sign up</NavLink>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
