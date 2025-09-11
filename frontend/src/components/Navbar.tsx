import { useState, type ReactNode } from "react"

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
    
    const TransactionIcon = () => <img src="/transaction-svgrepo-com.svg" alt="Transactions" className="w-4 h-4" />;
    const DashboardIcon = () => <img src="/dashboard-svgrepo-com.svg" alt="Dashboard" className="w-4 h-4" />;
    const AgentIcon = () => <img src="/artificial-intelligence-svgrepo-com.svg" alt="Agent" className="w-4 h-4" />;
    const SettingsIcon = () => <img src="/settings-svgrepo-com.svg" alt="Transactions" className="w-4 h-4" />;
    const AboutIcon = () => <img src="/about-svgrepo-com.svg" alt="Dashboard" className="w-4 h-4" />;
    const LogoutIcon = () => <img src="/logout-svgrepo-com.svg" alt="Agent" className="w-4 h-4" />;

    const navBarElements : { element : string , symbol : ReactNode }[] = [
        { element: "Transactions", symbol: <TransactionIcon /> },
        { element: "Dashboard", symbol: <DashboardIcon /> },
        { element: "Agent", symbol: <AgentIcon /> },
    ]

    const navBarSettings : { element : string , symbol: ReactNode}[] = [
        { element: "Settings", symbol: <SettingsIcon /> },
        { element: "About", symbol: <AboutIcon /> },
        { element: "Logout", symbol: <LogoutIcon /> },
    ]

    const userInformation : { userName: string, userPosition: string, userProfile: string } = {
        userName : "Daniel Dias",
        userPosition : "Software Engineer",
        userProfile : "/profile.png"
    }

    const [isCollapsed, setIsCollapsed] = useState(false)
    const [isMobileOpen, setIsMobileOpen] = useState(true)

    return (
        <>
        {/* Mobile open button (only under 500px when sidebar is closed) */}
        <MobileButton
            isMobileOpen={isMobileOpen}
            setIsMobileOpen={setIsMobileOpen}
        />

        <div className={`${isCollapsed ? "lg:w-20" : "lg:w-[17.5%]"} w-20 max-[500px]:w-full ${!isMobileOpen ? "max-[500px]:hidden" : ""} min-h-screen max-h-[fit] bg-[#0F0F11] flex flex-col border-1 rounded-xl border-[#2A2A2A] p-2 shadow-lg shadow-zinc-800 items-center relative transition-all duration-300 ease-in-out`}>
            <button onClick={() => setIsCollapsed(v => !v)} className="hidden lg:flex transform transition duration-300 ease-in-out opacity-70 hover:shadow-2xl hover:shadow-zinc-800 w-10 h-10 bg-[#0F0F11] border rounded-full lg:absolute max-w-none top-1/2 -translate-y-1/2 -right-4 border-[#2A2A2A] shadow-r-lg items-center justify-center">
                <img src="/left-arrow-backup-2-svgrepo-com.svg" alt="Toggle sidebar" className={`w-3 h-3 transition-transform duration-300 ${isCollapsed ? "rotate-180" : ""}`} />
            </button>
            {/* Mobile close button (only under 500px when sidebar is open at full width) */}
            <button onClick={() => setIsMobileOpen(false)} className="hidden max-[500px]:flex absolute top-[2rem] right-3 w-9 h-9 rounded-full bg-[#0F0F11] border border-[#2A2A2A] shadow-md shadow-zinc-800 items-center justify-center">
                <svg viewBox="0 0 24 24" className="w-5 h-5 text-zinc-300" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="9" />
                </svg>
            </button>

            <div className="w-[90%] h-fit  xs:flex flex-col justify-left items-center mt-6">
                <div className={`w-full h-fit flex flex-row justify-center max-[500px]:justify-start ${isCollapsed ? "lg:justify-center" : "lg:justify-start"} gap-4 text-zinc-200 items-center`}>
                    <div className="w-10 h-10 rounded-full overflow-hidden">
                        <img src="/profile.png" className="w-full h-full object-cover " />
                    </div>
                    <div className={`hidden max-[500px]:flex ${isCollapsed ? "lg:hidden" : "lg:flex"} flex-col gap-y-0.5 text-sm`}>
                        <span className="font-semibold">{userInformation.userPosition}</span>
                        <span className="text-xs">{userInformation.userName}</span>
                    </div>
                </div>
                <div className="w-full h-[0.04rem] bg-[#3E3E3E] opacity-90 mt-6"></div>
            </div>

            <div className="w-[90%] h-fit flex flex-col justify-center text-zinc-300 gap-y-5 text-sm mt-6">
                <span className={`text-xs opacity-80 hidden max-[500px]:block ${isCollapsed ? "lg:hidden" : "lg:block"}`}>Features</span>
                <div className="flex flex-col gap-y-5">
                    {navBarElements.map(({ element, symbol }) => (
                        <div key={element} className={`flex items-center justify-center max-[500px]:justify-start ${isCollapsed ? "lg:justify-center" : "lg:justify-start"} space-x-2`}>
                            <span className="w-4 h-4 inline-flex items-center justify-center">{symbol}</span>
                            <button className={`hidden max-[500px]:inline ${isCollapsed ? "lg:hidden" : "lg:inline"} transform transition duration-300 ease-in-out opacity-70 hover:opacity-100 hover:text-white `}>{element}</button>
                        </div>
                    ))}
                </div>
            </div>

            <div className="w-[90%] h-fit flex flex-col justify-center text-zinc-300 opacity-90 gap-y-5 text-sm mt-auto mb-6">
                <div className="w-full h-[0.04rem] bg-[#3E3E3E] opacity-90 mt-6"></div>
                <span className={`text-xs opacity-80 hidden max-[500px]:block ${isCollapsed ? "lg:hidden" : "lg:block"}`}>More</span>
                <div className="flex flex-col gap-y-5">
                    {navBarSettings.map(({ element, symbol }) => (
                        <div key={element} className={`flex items-center justify-center max-[500px]:justify-start ${isCollapsed ? "lg:justify-center" : "lg:justify-start"} space-x-2`}>
                            <span className="w-4 h-4 inline-flex items-center justify-center">{symbol}</span>
                            <button className={`hidden max-[500px]:inline ${isCollapsed ? "lg:hidden" : "lg:inline"} transform transition duration-300 ease-in-out text-xs ${element === "Logout" ? "text-red-400 opacity-100 hover:text-red-300" : "text-zinc-300 hover:text-white"}`}>
                                {element}
                            </button>
                        </div>
                    ))}
                </div>
            </div>

        </div>
        </>
    )
}