import { useAuth } from "../../context/AuthContext";

function DashboardPage({ onNavigate }) {
  const { user, logout } = useAuth();

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "2rem", background: "#f5f7fb" }}>
      <div style={{ maxWidth: "480px", width: "100%", padding: "2rem", borderRadius: "16px", background: "white", boxShadow: "0 12px 36px rgba(15, 23, 42, 0.08)" }}>
        <h1 style={{ marginBottom: "0.5rem" }}>Dashboard</h1>
        <p style={{ marginBottom: "1.5rem", color: "#475569" }}>
          You are signed in as <strong>{user?.email}</strong>.
        </p>

        <button
          onClick={() => {
            logout();
            onNavigate("login");
          }}
          className="btn btn-primary"
          style={{ width: "100%" }}
        >
          Log out
        </button>
      </div>
    </div>
  );
}

export default DashboardPage;