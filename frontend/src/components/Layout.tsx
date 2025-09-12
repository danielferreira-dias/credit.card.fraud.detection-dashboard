import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

export default function Layout() {

  return (
    <div className="flex flex-row gap-x-4 m-auto min-h-[screen] max-h-[fit]">
        <Navbar></Navbar>
        <div className="w-full h-full ">
          <div className="flex-1 rounded-xl min-h-screen max-h-[fit] flex">
              <Outlet></Outlet>
          </div>
        </div>
    </div>
  );
}
