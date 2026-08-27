import { useState } from "react";
import Login from "./pages/Login";
import Home from "./pages/Home";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = (user) => {
    console.log("Logged in user:", user);

    setIsAuthenticated(true);
  };

  if (!isAuthenticated) {
    return (
      <Login onLogin={handleLogin} />
    );
  }

  return <Home />;
}

export default App;