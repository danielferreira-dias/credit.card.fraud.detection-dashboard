import { useEffect, useState } from "react";
import StatsCard from "../components/StatsCard";
import TransactionList from "../components/TransactionsList";
import StatsLoadingCard from "../components/StatsLoadingCard";

type StatInfo = {
    id: number; 
    typeStat: string;
    statValue: number;
    cardColour: string;
  };

export default function TransactionPage(){
    const [stats, setStats] = useState<StatInfo[]>([
        { id: 1, typeStat: "Number of Transactions", statValue: 0, cardColour: "card-1" },
        { id: 2, typeStat: "Valid Transactions", statValue: 0, cardColour: "card-2" },
        { id: 3, typeStat: "Fraudulent Transactions", statValue: 0, cardColour: "card-3" },
        { id: 4, typeStat: "Fraudulent Detection Percentage", statValue: 0, cardColour: "card-4" },
    ]);

    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            
            // Check cache first
            const cachedData = sessionStorage.getItem(`transactions_count`);    
            const cacheTime = sessionStorage.getItem(`transactions_count_timestamp`);

            if (cachedData && cacheTime) {
                const age = Date.now() - parseInt(cacheTime);
                if (age < 2 * 60 * 1000) { // 2 minutes cache
                    const parsedData = JSON.parse(cachedData);
                    const cachedStats = [
                        { id: 1, typeStat: "Number of Transactions", statValue: parsedData.data.total_transactions, cardColour: "card-1" },
                        { id: 2, typeStat: "Valid Transactions", statValue: (parsedData.data.total_transactions - parsedData.data.fraud_transactions), cardColour: "card-2" },
                        { id: 3, typeStat: "Fraudulent Transactions", statValue: parsedData.data.fraud_transactions, cardColour: "card-3" },
                        { id: 4, typeStat: "Fraudulent Detection Percentage", statValue: parseFloat(((parsedData.data.fraud_transactions/parsedData.data.total_transactions) * 100).toFixed(2)), cardColour: "card-4" },
                    ];
                    setStats(cachedStats);
                    setLoading(false);
                    return;
                }
            }

            try {
                const res = await fetch("http://localhost:80/transactions/count");
                if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`);
                const data = await res.json();

                // Cache the data
                sessionStorage.setItem(`transactions_count`,JSON.stringify(data));
                sessionStorage.setItem(`transactions_count_timestamp`,Date.now().toString());

                const updatedStats = [
                    { id: 1, typeStat: "Number of Transactions", statValue: data.data.total_transactions, cardColour: "card-1" },
                    { id: 2, typeStat: "Valid Transactions", statValue: (data.data.total_transactions - data.data.fraud_transactions), cardColour: "card-2" },
                    { id: 3, typeStat: "Fraudulent Transactions", statValue: data.data.fraud_transactions, cardColour: "card-3" },
                    { id: 4, typeStat: "Fraudulent Detection Percentage", statValue: parseFloat(((data.data.fraud_transactions/data.data.total_transactions) * 100).toFixed(2)), cardColour: "card-4" },
                ];

                setStats(updatedStats);
                setLoading(false);
            } catch (err) {
                console.error("Failed to fetch transaction stats", err);
                setLoading(false);
            }
        };
            fetchData();
        }, []);
    

    return (
        <div className="flex flex-col h-full w-full text-white p-4 gap-y-1 flex-1 rounded-xl  border-[1px] bg-[#0F0F11] border-zinc-700 min-h-screen max-h-[fit]">
            <h2 className="text-2xl font-semibold opacity-90 mt-4">Transactions Analytics</h2>
            <h3 className="text-sm opacity-70">Monitor your transactions in real-time</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 w-full gap-4 items-center mt-6">
                {loading ? (
                    stats.map((stat) => (
                        <StatsLoadingCard key={stat.id} colour={stat.cardColour} />
                    ))
                ) : (
                    stats.map((stat) => (
                        <StatsCard
                            key={stat.id}
                            typeStat={stat.typeStat}
                            statValue={stat.statValue}
                            colour={stat.cardColour}
                        />
                    ))
                )}
               
            </div>
            <TransactionList />
        </div>
    )
}