import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Transactions from "./pages/Transactions";
import DashboardPage from "./pages/Dashboard";
import AgentPage from "./pages/Agent";
import AuthenticationPage from "./pages/Authentication";
import { UserProvider } from "./context/UserContext";

function App() {
  return (
    // UserProvider: Provides user context (user data, auth state) to ALL components in the app
    // This is NOT for route protection - it's for sharing user state globally
    <UserProvider>
      <Routes>
        {/*
          Layout Component Flow:
          1. Layout renders for ALL routes (/, /dashboard, /agent, /auth)
          2. Layout checks if current path is "/auth"
          3. If "/auth": renders auth page without navbar (no protection needed)
          4. If NOT "/auth": wraps content with AuthRouter for protection
          5. AuthRouter checks if user is logged in:
             - If logged in: renders the requested page with navbar
             - If NOT logged in: redirects to "/auth"
          6. <Outlet /> renders the specific page component based on the route
        */}
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
    </UserProvider>
  );
}

export default App;
