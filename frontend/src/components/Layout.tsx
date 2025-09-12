import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

export default function Layout() {
  return (
    <div className="flex flex-row gap-x-4 m-auto min-h-[screen] max-h-[fit]">
        <Navbar></Navbar>
        <div className="w-full h-full ">
          <div className="flex-1 rounded-xl  border-[1px] bg-[#0F0F11] border-zinc-700 min-h-screen max-h-[fit] flex">
              <Outlet></Outlet>
          </div>
        </div>
    </div>
  );
}
