import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Transactions from "./pages/Transactions";
import DashboardPage from "./pages/Dashboard";
import AgentPage from "./pages/Agent";
import AuthenticationPage from "./pages/Authentication";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Transactions />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="agent" element={<AgentPage />} />
        <Route path="auth" element={<AuthenticationPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
