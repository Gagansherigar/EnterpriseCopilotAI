import { useNavigate } from "react-router-dom";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing">
      {/* Navbar */}
      <div className="nav">
        <h2>Enterprise AI Copilot</h2>
        <button onClick={() => navigate("/app")}>Open App</button>
      </div>

      {/* Hero */}
      <div className="hero">
        <h1>AI Copilot for Enterprise Teams</h1>
        <p>
          Query company knowledge, access databases, and automate workflows —
          all in one intelligent system.
        </p>

        <div className="buttons">
          <button onClick={() => navigate("/app")}>
            Get Started
          </button>
          <button className="secondary">
            Learn More
          </button>
        </div>
      </div>

      {/* Features */}
      <div className="features">
        <div className="card">
          <h3>RAG Knowledge</h3>
          <p>Ask questions from company documents instantly.</p>
        </div>

        <div className="card">
          <h3>SQL Intelligence</h3>
          <p>Query business data using natural language.</p>
        </div>

        <div className="card">
          <h3>Multi-Tenant</h3>
          <p>Secure, isolated data per company.</p>
        </div>

        <div className="card">
          <h3>Human Escalation</h3>
          <p>Fallback to support when AI is unsure.</p>
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        <p>© 2026 Enterprise AI Copilot</p>
      </div>
    </div>
  );
}