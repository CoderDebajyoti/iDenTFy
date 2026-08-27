import { useState } from "react";

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();

    setError("");

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    /*
      For now this is frontend-only authentication.

      Later we will replace this with:
          FastAPI /login

      Example:
          const response = await loginUser(email, password);
    */

    onLogin({
      email: email,
    });
  };

  return (
    <div className="login-page">

      <div className="login-background-shape shape-one"></div>
      <div className="login-background-shape shape-two"></div>

      <div className="login-container">

        {/* Logo */}

        <div className="login-logo">
          <div className="logo-shield">
            🛡
          </div>

          <div className="login-brand">
            <span>i</span>Den<span>Fy</span>
          </div>
        </div>


        {/* Heading */}

        <div className="login-heading">

          <h1>
            Welcome Back
          </h1>

          <p>
            Sign in to continue to Identity Verification
          </p>

        </div>


        {/* Login Card */}

        <div className="login-card">

          <form onSubmit={handleSubmit}>

            {/* Email */}

            <div className="input-group">

              <label htmlFor="email">
                Email Address
              </label>

              <div className="input-wrapper">

                <span className="input-icon">
                  ✉
                </span>

                <input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                />

              </div>

            </div>


            {/* Password */}

            <div className="input-group">

              <div className="password-label">

                <label htmlFor="password">
                  Password
                </label>

                <button
                  type="button"
                  className="forgot-password"
                  onClick={() => {
                    alert("Password reset will be connected later.");
                  }}
                >
                  Forgot Password?
                </button>

              </div>


              <div className="input-wrapper">

                <span className="input-icon">
                  🔒
                </span>

                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(!showPassword)
                  }
                >
                  {showPassword ? "◉" : "○"}
                </button>

              </div>

            </div>


            {/* Remember Me */}

            <div className="login-options">

              <label className="remember-me">

                <input type="checkbox" />

                <span>
                  Remember me
                </span>

              </label>

            </div>


            {/* Error */}

            {error && (
              <div className="login-error">
                ⚠ {error}
              </div>
            )}


            {/* Login */}

            <button
              type="submit"
              className="login-button"
            >
              SIGN IN
            </button>

          </form>


          {/* Security */}

          <div className="login-security">

            <span>✓</span>

            <div>
              <strong>Secure Login</strong>

              <p>
                Your credentials are protected with
                secure encryption.
              </p>
            </div>

          </div>

        </div>


        {/* Footer */}

        <div className="login-footer">

          <span>
            © 2026 iDenFy
          </span>

          <span>
            •
          </span>

          <span>
            Secure Identity Verification
          </span>

        </div>

      </div>

    </div>
  );
}

export default Login;