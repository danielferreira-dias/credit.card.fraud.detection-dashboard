import { Outlet, useLocation } from "react-router-dom";
import Navbar from "./Navbar";
import AuthRouter from "./AuthRouter";

export default function Layout() {
  const location = useLocation();
  const isAuthPage = location.pathname === "/auth";

  if (isAuthPage) {
    return (
      <div className="flex flex-row gap-x-4 m-auto min-h-[screen] max-h-[fit]">
        <Outlet />
      </div>
    );
  }

  return (
    <AuthRouter>
      <div className="flex flex-row gap-x-4 m-auto min-h-[screen] max-h-[fit]">
        <Navbar />
        <div className="w-full h-full">
          <div className="flex-1 rounded-xl min-h-screen max-h-[fit] flex">
            <Outlet />
          </div>
        </div>
      </div>
    </AuthRouter>
  );
}
