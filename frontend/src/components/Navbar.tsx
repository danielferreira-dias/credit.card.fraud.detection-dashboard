import type { ReactNode } from "react"

export default function Navbar(){
    
    const TransactionIcon = () => <img src="../../public/transaction-svgrepo-com.svg" alt="Transactions" className="w-4 h-4" />;
    const DashboardIcon = () => <img src="../../public/dashboard-svgrepo-com.svg" alt="Dashboard" className="w-4 h-4" />;
    const AgentIcon = () => <img src="../../public/artificial-intelligence-svgrepo-com.svg" alt="Agent" className="w-4 h-4" />;
    const SettingsIcon = () => <img src="../../public/settings-svgrepo-com.svg" alt="Transactions" className="w-4 h-4" />;
    const AboutIcon = () => <img src="../../public/about-svgrepo-com.svg" alt="Dashboard" className="w-4 h-4" />;
    const LogoutIcon = () => <img src="../../public/logout-svgrepo-com.svg" alt="Agent" className="w-4 h-4" />;

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
        userProfile : "../../public/profile.png"
    }

    return (
        <div className="h-screen w-[15%] bg-[#0F0F11] flex flex-col border-1 rounded-xl border-[#2A2A2A] p-2 shadow-lg shadow-zinc-800 items-center">

            <div className="w-10 h-10 bg-transparent border-1 rounded-full absolute right-0 border-[#2A2A2A] shadow-lg shadow-zinc-800">
                <img src="../../public/left-arrow-backup-2-svgrepo-com.svg" alt="Agent" className="w-10 h-10 p-3" />;    
            </div>

            /* User's information */
            <div className="w-[90%] h-fit flex flex-col justify-left items-center">
                <div className="w-full h-fit flex flex-row justify-left gap-4 text-zinc-300">
                    <div className="w-10 h-10 rounded-full overflow-hidden">
                        <img src="" className="w-full h-full object-cover bg-white" />
                    </div>
                    <div className="flex flex-col gap-y-0.5 text-sm">
                        <span className="font-semibold">{userInformation.userPosition}</span>
                        <span className="text-xs">{userInformation.userName}</span>
                    </div>
                </div>
                <div className="w-full h-[0.04rem] bg-[#3E3E3E] opacity-90 mt-6"></div>
            </div>

            <div className="w-[90%] h-fit flex flex-col justify-center text-zinc-300 opacity-90 gap-y-5 text-sm mt-6">
                <span className="text-xs opacity-80">Features</span>
                <div className="flex flex-col gap-y-5">
                    {navBarElements.map(({ element, symbol }) => (
                        <div key={element} className="flex items-center space-x-2">
                        <span className="w-4 h-4 inline-flex items-center justify-center">{symbol}</span>
                        <span>{element}</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="w-[90%] h-fit flex flex-col justify-center text-zinc-300 opacity-90 gap-y-5 text-sm mt-auto mb-6">
                <div className="w-full h-[0.04rem] bg-[#3E3E3E] opacity-90 mt-6"></div>
                <span className="text-xs opacity-80">More</span>
                <div className="flex flex-col gap-y-5">
                    {navBarSettings.map(({ element, symbol }) => (
                        <div key={element} className="flex items-center space-x-2">
                        <span className="w-4 h-4 inline-flex items-center justify-center">{symbol}</span>
                        <span>{element}</span>
                        </div>
                    ))}
                </div>
            </div>

            
        </div>        
    )
}