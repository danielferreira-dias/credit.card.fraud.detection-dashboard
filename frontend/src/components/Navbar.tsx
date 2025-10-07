import { useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import { useUser } from "../context/UserContext"
import { useNavbar } from "../context/NavbarContext"
import { googleLogout } from "@react-oauth/google";
import { PanelLeft, PanelRight } from 'lucide-react';

function MobileButton({ isMobileOpen, setIsMobileOpen } : { isMobileOpen : boolean, setIsMobileOpen : (setIsMobileOpen:boolean) => void  }){
    return(
        <>
        {!isMobileOpen && (
            <button onClick={() => setIsMobileOpen(true)} className="hidden max-[500px]:flex fixed top-[2rem] left-4 z-50 w-10 h-10 rounded-full bg-[#0F0F11] border border-[#2A2A2A] shadow-lg shadow-zinc-800 items-center justify-center">
                <svg viewBox="0 0 24 24" className="w-5 h-5 text-zinc-300" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="9" />
                </svg>
            </button>
        )}
        </>
    )
}

export default function Navbar(){
    const { user, logout } = useUser();
    const { isCollapsed, toggleCollapsed } = useNavbar();

    const TransactionIcon = () => <img src="/transaction-svgrepo-com.svg" alt="Transactions" className="w-4 h-4" />;
    const DashboardIcon = () => <img src="/dashboard-svgrepo-com.svg" alt="Dashboard" className="w-4 h-4" />;
    const AgentIcon = () => <img src="/artificial-intelligence-svgrepo-com.svg" alt="Agent" className="w-4 h-4" />;
    const SettingsIcon = () => <img src="/settings-svgrepo-com.svg" alt="Transactions" className="w-4 h-4" />;
    const AboutIcon = () => <img src="/about-svgrepo-com.svg" alt="Dashboard" className="w-4 h-4" />;
    const LogoutIcon = () => <img src="/logout-svgrepo-com.svg" alt="Agent" className="w-4 h-4" />;

    const navBarElements : { element : string , path?: string, symbol : ReactNode }[] = [
        { element: "Transactions", path: "/", symbol: <TransactionIcon /> },
        { element: "Dashboard", path: "/dashboard", symbol: <DashboardIcon /> },
        { element: "Agent", path: "/agent", symbol: <AgentIcon /> },
    ]

    const navBarSettings : { element : string , path?: string,  symbol: ReactNode, onClick?: () => void}[] = [
        { element: "Personal", path: "/personal" , symbol: <SettingsIcon /> },
        { element: "About",  path: "/about" ,symbol: <AboutIcon /> },
        { element: "Logout", symbol: <LogoutIcon />, onClick: () => {
            googleLogout();
            logout();
        }},
    ]

    const [isMobileOpen, setIsMobileOpen] = useState(true)

    return (
        <>
        {/* Mobile open button (only under 500px when sidebar is closed) */}
        <MobileButton
            isMobileOpen={isMobileOpen}
            setIsMobileOpen={setIsMobileOpen}
        />

        <div
            className={`${isCollapsed ? "lg:w-20 " : "lg:w-[15%]"} } w-20 h-svh  top-0  max-[500px]:w-full max-[500px]:rounded-none max-[500px]:border-0  max-[500px]:fixed max-[500px]:z-50 ${!isMobileOpen ? "max-[500px]:hidden" : ""} h-[98vh] flex flex-col rounded-xl p-2 items-center sticky transition-all duration-300 ease-in-out relative`}
            style={{
                border: 'double 1px transparent',
                borderRadius: '0.75rem',
                backgroundImage: `
                    linear-gradient(#0a0a0a, #0a0a0a),
                    linear-gradient(225deg, rgba(75, 75, 75, 1) 0%, rgba(10, 10, 10, 1) 10%, rgba(10, 10, 10, 1) 85%, rgba(75, 75, 75, 1) 100%),
                    linear-gradient(200deg, rgba(177, 14, 14, 1) 0%, rgba(10, 10, 10, 1) 15%, rgba(10, 10, 10, 1) 85%, rgba(75, 75, 75, 1) 100%)
                `,
                backgroundOrigin: 'border-box',
                backgroundClip: 'padding-box, border-box, border-box'
            }}>

            {/* Mobile close button (only under 500px when sidebar is open at full width) */}
            <button onClick={() => setIsMobileOpen(false)} className="hidden max-[500px]:flex absolute top-[2rem] right-3 w-9 h-9 rounded-full bg-[#0F0F11] border border-[#2A2A2A] shadow-md shadow-zinc-800 items-center justify-center">
                <svg viewBox="0 0 24 24" className="w-5 h-5 text-zinc-300" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="9" />
                </svg>
            </button>

            <div className="w-[90%] h-fit  xs:flex flex-col justify-left items-center mt-2">
                <div className={`w-full h-fit flex flex-row justify-center border-b-[1px] rounded-md border-zinc-700 py-7 max-[500px]:justify-start ${isCollapsed ? "lg:justify-center" : "lg:justify-start"} gap-4 text-zinc-200 items-center`}>
                    <div className="w-10 h-10 rounded-full overflow-hidden">
                        <img src="/profile.png" className="w-full h-full object-cover " />
                    </div>
                    <div className={`hidden max-[500px]:flex ${isCollapsed ? "lg:hidden" : "lg:flex"} flex-col gap-y-0.5 text-sm`}>
                        <span className="font-semibold">{user?.name || "User"}</span>
                        <span className="text-xs">Analyst</span>
                    </div>
                </div>
            </div>

            <div className="w-[90%] h-fit flex flex-col justify-center text-zinc-300 gap-y-5 text-sm mt-6">
                <span className={`text-xs opacity-80 hidden max-[500px]:block ${isCollapsed ? "lg:hidden" : "lg:block"}`}>Features</span>
                <div className="flex flex-col gap-y-5">
                    {navBarElements.map(({ element, path, symbol }) => (
                        <Link key={element} to={path ?? "#"} className={`flex items-center justify-center max-[500px]:justify-start ${isCollapsed ? "lg:justify-center" : "lg:justify-start"} space-x-2`}>
                            <span className="w-4 h-4 inline-flex items-center justify-center">{symbol}</span>
                            <span className={`hidden max-[500px]:inline ${isCollapsed ? "lg:hidden" : "lg:inline"} transform transition duration-300 ease-in-out opacity-70 hover:opacity-100 hover:text-white`}>{element}</span>
                        </Link>
                    ))}
                </div>
            </div>

            <div className="w-[90%] h-fit flex border-t-[1px] rounded-md border-zinc-700 py-7 flex-col justify-center text-zinc-300 opacity-90 gap-y-5 text-sm mt-auto mb-2">
                <span className={`text-xs opacity-80 hidden max-[500px]:block ${isCollapsed ? "lg:hidden" : "lg:block"}`}>More</span>
                <div className="flex flex-col gap-y-5">
                    {navBarSettings.map(({ element, path, symbol, onClick }) => (
                        onClick ? (
                            <div
                                key={element}
                                onClick={onClick}
                                className={`flex items-center justify-center max-[500px]:justify-start ${isCollapsed ? "lg:justify-center" : "lg:justify-start"} space-x-2 cursor-pointer`}
                            >
                                <span className="w-4 h-4 inline-flex items-center justify-center">{symbol}</span>
                                <span className={`hidden max-[500px]:inline ${isCollapsed ? "lg:hidden" : "lg:inline"} transform transition duration-300 ease-in-out text-xs opacity-100 hover:text-zinc-300`}>
                                    {element}
                                </span>
                            </div>
                        ) : (
                            <Link key={element} to={path ?? "#"} className={`flex items-center justify-center max-[500px]:justify-start ${isCollapsed ? "lg:justify-center" : "lg:justify-start"} space-x-2`}>
                                <span className="w-4 h-4 inline-flex items-center justify-center">{symbol}</span>
                                <span className={`hidden max-[500px]:inline ${isCollapsed ? "lg:hidden" : "lg:inline"} transform transition duration-300 ease-in-out text-xs text-zinc-300 hover:text-white`}>
                                    {element}
                                </span>
                            </Link>
                        )
                    ))}
                </div>
            </div>
        </div>
        </>
    )
}