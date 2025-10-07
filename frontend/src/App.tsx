import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Transactions from "./pages/Transactions";
import DashboardPage from "./pages/Dashboard";
import AgentPage from "./pages/Agent";
import AuthenticationPage from "./pages/Authentication";
import { UserProvider } from "./context/UserContext";
import { NotificationProvider } from "./context/NotificationContext";
import { NavbarProvider } from "./context/NavbarContext";
import { NotificationContainer } from "./components/Modal";

function App() {
  return (
    // UserProvider: Provides user context (user data, auth state) to ALL components in the app
    // This is NOT for route protection - it's for sharing user state globally
    <NotificationProvider>
      <UserProvider>
        <NavbarProvider>
          <Routes>
          <Route element={<Layout />}>
            {/* Protected Routes (wrapped by AuthRouter in Layout) */}
            <Route index element={<Transactions />} />          {/* / */}
            <Route path="dashboard" element={<DashboardPage />} /> {/* /dashboard */}
            <Route path="agent" element={<AgentPage />} />         {/* /agent */}

            {/* Public Route (bypasses AuthRouter in Layout) */}
            <Route path="auth" element={<AuthenticationPage />} /> {/* /auth */}

            {/* Fallback: redirect any unknown route to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
          </Routes>
          {/* Global notification container - persists across all routes */}
          <NotificationContainer />
        </NavbarProvider>
      </UserProvider>
    </NotificationProvider>
  );
}

export default App;
