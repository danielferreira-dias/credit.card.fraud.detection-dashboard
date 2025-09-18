import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Transactions from "./pages/Transactions";
import DashboardPage from "./pages/Dashboard";
import AgentPage from "./pages/Agent";
import AuthenticationPage from "./pages/Authentication";
import { UserProvider } from "./context/UserContext";

function App() {
  return (
    <UserProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Transactions />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="agent" element={<AgentPage />} />
          <Route path="auth" element={<AuthenticationPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </UserProvider>
  );
}

export default App;
