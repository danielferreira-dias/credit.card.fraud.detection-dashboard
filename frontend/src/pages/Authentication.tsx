import { useEffect, useState } from "react";
import Login from "../components/Login";
import Register from "../components/Register";
import { useUser } from "../context/UserContext";
import { useLocation, useNavigate } from "react-router-dom";
import Loading from "../components/Loading";

export default function AuthenticationPage() {
  const [loginPage, setLoginPage] = useState(true);
  const { user, loading } = useUser();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (user) {
      navigate("/", { replace: true, state: { from: location } });
    }
  }, [user, loading, navigate, location]);
  if (loading) {
    return (
      <Loading />
    );
  }
  
  return (
    <div className="flex flex-col w-full text-white justify-center items-center border-[1px] bg-[#0F0F11] border-zinc-700 min-h-screen ">
      <div className="flex flex-col w-[50%] h-[80%] min-w-[400px] border-[1px] bg-[#0F0F11] border-zinc-700 shadow-xl shadow-zinc-900 rounded-xl min-h-[600px]">
        <div className="flex flex-row w-full h-16 bg-[#121214bb] rounded-t-xl  border-b-[1px] border-zinc-700" >
          <button
            className="text-white text-xl opacity-70 border-r-[1px] rounded-r-xl p-2 px-10 border-zinc-700"
            onClick={() => setLoginPage(true)}>
            <span>Login</span>
          </button>
          <button
            className="text-white text-xl opacity-70 border-r-[1px] rounded-r-xl p-2 px-10 border-zinc-700"
            onClick={() => setLoginPage(false)}>
            <span>Register</span>
          </button>
        </div>
        {loginPage ? <Login /> : <Register />}
      </div>
    </div>
  );
}
