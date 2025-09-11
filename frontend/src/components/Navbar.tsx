import type { ReactNode } from "react"

export default function Navbar(){
    const TransactionIcon = () => <svg width="16" height="16" fill="currentColor"><circle cx="8" cy="8" r="6" /></svg>;
    const AnalyticsIcon = () => <svg width="16" height="16" fill="currentColor"><rect width="12" height="8" /></svg>;
    const AgentIcon = () => <svg width="16" height="16" fill="currentColor"><polygon points="4,4 12,4 8,12" /></svg>;

    const navBarElements: { element : string , symbol : ReactNode }[] = [
        { element: "Transactions", symbol: <TransactionIcon /> },
        { element: "Analytics", symbol: <AnalyticsIcon /> },
        { element: "Agent", symbol: <AgentIcon /> },
    ]

    return (
        <div className="h-screen w-[12.5%] bg-[#0F0F11] flex flex-col border-1 rounded-xl border-[#2A2A2A]">

            /** User's information */
        </div>        
    )
}