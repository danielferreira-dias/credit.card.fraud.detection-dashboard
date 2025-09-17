import { useState } from "react";
import Login from "../components/Login";
import Register from "../components/Register";

export default function AuthenticationPage() {
  const [loginPage, setLoginPage] = useState(false);

  return (
    <div className="flex flex-col w-full text-white justify-center items-center border-[1px] bg-[#0F0F11] border-zinc-700 min-h-screen ">
      <div className="flex flex-col w-[60%] h-[80%] min-w-[400px] border-[1px] bg-[#0F0F11] border-zinc-700 shadow-lg shadow-zinc-900 rounded-xl min-h-[600px]">
        <div className="flex flex-row w-full h-16 bg-[#121214bb] rounded-t-xl p-2 gap-x-12 px-10">
          <button
            className="text-white text-xl font-semibold opacity-70"
            onClick={() => setLoginPage(true)}>
            <span>Login</span>
          </button>
          <button
            className="text-white text-xl font-semibold  opacity-70"
            onClick={() => setLoginPage(false)}>
            <span>Register</span>
          </button>
        </div>
        {loginPage ? <Login /> : <Register />}
      </div>
    </div>
  );
}
