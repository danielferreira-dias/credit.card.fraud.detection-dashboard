import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

export default function Layout() {
  return (
    <div className="flex flex-row p-2 gap-x-4 m-auto min-h-screen max-h-[fit] ">
        <Navbar></Navbar>
        <div className="flex-1 rounded-xl mr-3 border-[1px] bg-[#0F0F11] border-zinc-700 min-h-screen max-h-[fit] flex">
            <Outlet></Outlet>
        </div>
    </div>
  );
}
