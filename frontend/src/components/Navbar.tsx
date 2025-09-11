import { useState, type ReactNode } from "react"

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

    return (
        <div className={`${isCollapsed ? "w-20" : "w-full sm:w-[10%] lg:w-[17.5%] "} h-screen bg-[#0F0F11] flex flex-col border-1 rounded-xl border-[#2A2A2A] p-2 shadow-lg shadow-zinc-800 items-center relative transition-all duration-300 ease-in-out`}>
            <button onClick={() => setIsCollapsed(v => !v)} className="hidden lg:flex transform transition duration-300 ease-in-out opacity-70 hover:shadow-2xl hover:shadow-zinc-800 w-10 h-10 bg-[#0F0F11] border rounded-full lg:absolute max-w-none top-1/2 -translate-y-1/2 -right-4 border-[#2A2A2A] shadow-r-lg items-center justify-center">
                <img src="/left-arrow-backup-2-svgrepo-com.svg" alt="Toggle sidebar" className={`w-3 h-3 transition-transform duration-300 ${isCollapsed ? "rotate-180" : ""}`} />
            </button>

            <div className="w-[90%] h-fit  xs:flex flex-col justify-left items-center mt-6">
                <div className={`w-full h-fit flex flex-row ${isCollapsed ? "justify-center" : "justify-left"} gap-4 text-zinc-200 items-center`}>
                    <div className="w-10 h-10 rounded-full overflow-hidden">
                        <img src="/profile.png" className="w-full h-full object-cover " />
                    </div>
                    {!isCollapsed && (
                        <div className="flex flex-col gap-y-0.5 text-sm">
                            <span className="font-semibold">{userInformation.userPosition}</span>
                            <span className="text-xs">{userInformation.userName}</span>
                        </div>
                    )}
                </div>
                <div className="w-full h-[0.04rem] bg-[#3E3E3E] opacity-90 mt-6"></div>
            </div>

            <div className="w-[90%] h-fit flex flex-col justify-center text-zinc-300 gap-y-5 text-sm mt-6">
                {!isCollapsed && <span className="text-xs opacity-80">Features</span>}
                <div className="flex flex-col gap-y-5">
                    {navBarElements.map(({ element, symbol }) => (
                        <div key={element} className={`flex items-center ${isCollapsed ? "justify-center" : ""} space-x-2`}>
                            <span className="w-4 h-4 inline-flex items-center justify-center">{symbol}</span>
                            {!isCollapsed && (
                                <button className="transform transition duration-300 ease-in-out opacity-70 hover:opacity-100 hover:text-white ">{element}</button>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            <div className="w-[90%] h-fit flex flex-col justify-center text-zinc-300 opacity-90 gap-y-5 text-sm mt-auto mb-6">
                <div className="w-full h-[0.04rem] bg-[#3E3E3E] opacity-90 mt-6"></div>
                {!isCollapsed && <span className="text-xs opacity-80">More</span>}
                <div className="flex flex-col gap-y-5">
                    {navBarSettings.map(({ element, symbol }) => (
                        <div key={element} className={`flex items-center ${isCollapsed ? "justify-center" : ""} space-x-2`}>
                            <span className="w-4 h-4 inline-flex items-center justify-center">{symbol}</span>
                            {!isCollapsed && (
                                <button className={`transform transition duration-300 ease-in-out text-xs ${element === "Logout" ? "text-red-400 opacity-100 hover:text-red-300" : "text-zinc-300 hover:text-white"}`}>
                                    {element}
                                </button>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            
        </div>        
    )
}