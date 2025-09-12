import StatsCard from "../components/StatsCard";
import TransactionList from "../components/TransactionsList";

type StatInfo = {
    id: number; 
    typeStat: string;
    statValue: number;
    cardColour: string;
  };

export default function TransactionPage(){
    const stats: StatInfo[] = [
        { id: 1, typeStat: "Number of Transactions", statValue: 1247, cardColour: "card-1" },
        { id: 2, typeStat: "Valid Transactions", statValue: 876, cardColour: "card-2" },
        { id: 3, typeStat: "Fraudulent Transactions", statValue: 342, cardColour: "card-3"},
        { id: 4, typeStat: "Fraudulent Detection Percentage", statValue: 56, cardColour: "card-4" },
    ];

    return (
        <div className="flex flex-col h-full w-full text-white p-3 gap-y-1">
            <h2 className="text-2xl font-semibold opacity-90 mt-4">Transactions Analytics</h2>
            <h3 className="text-sm opacity-70">Monitor your transactions in real-time</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 w-full gap-4 items-center mt-6">
                { stats.map ((stat) => (
                    <StatsCard 
                        key={stat.id}
                        typeStat={stat.typeStat}
                        statValue={stat.statValue}
                        colour={stat.cardColour}
                    />
                ))}
            </div>
            <TransactionList />
        </div>
    )
}