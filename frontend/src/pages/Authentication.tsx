import { useEffect, useState } from "react";
import Register from "../components/Register";
import { useUser } from "../context/UserContext";
import { useLocation, useNavigate } from "react-router-dom";
import Loading from "../components/Loading";

export default function AuthenticationPage() {
  const { user, loading } = useUser();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (user) {
      navigate("/", { replace: true, state: { from: location } });
    }
  }, [user, loading, navigate, location]);
  
  return (
    loading ? <Loading /> : <div className="flex flex-col w-full h-[80%] text-white justify-center items-center border-[1px] bg-zinc-950 border-zinc-700 min-h-screen ">
      <div className="flex flex-col w-full h-[80%] min-w-[400px] border-[1px] bg-zinc-950 border-zinc-700 shadow-xl shadow-zinc-900 rounded-xl min-h-[600px]">
        <Register />
      </div>
    </div>
  );
}
