import { useEffect } from "react";
import type { ReactNode } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useUser } from "../context/UserContext";

interface AuthRouterProps {
  children: ReactNode;
}

export default function AuthRouter({ children }: AuthRouterProps) {
  // const navigate = useNavigate();
  // const location = useLocation();
  // const { user, loading } = useUser();

  // useEffect(() => {
  //   if (!loading && !user) {
  //     navigate("/auth", { replace: true, state: { from: location } });
  //   }
  // }, [user, loading, navigate, location]);

  // if (loading) {
  //   return <div>Loading...</div>;
  // }

  // if (!user) {
  //   return null;
  // }

  // Bypass authentication - allow access to all routes
  return <>{children}</>;
}