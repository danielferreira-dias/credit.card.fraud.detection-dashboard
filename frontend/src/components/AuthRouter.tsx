import { useEffect } from "react";
import type { ReactNode } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { isUserLoggedIn } from "../utils/auth";

interface AuthRouterProps {
  children: ReactNode;
}

export default function AuthRouter({ children }: AuthRouterProps) {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const checkAuth = () => {
      if (!isUserLoggedIn()) {
        navigate("/auth", { replace: true, state: { from: location } });
      }
    };

    checkAuth();
  }, [navigate, location]);

  if (!isUserLoggedIn()) {
    return null;
  }

  return <>{children}</>;
}