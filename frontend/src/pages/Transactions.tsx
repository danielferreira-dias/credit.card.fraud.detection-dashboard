import StatsCard from "../components/StatsCard";

export default function TransactionPage(){
    const currentStat : string = "Transações Fraudulentas"
    const currentValue : number = 1247

    return (
        <div className="flex flex-col h-full w-full text-white items-center p-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 w-full gap-4 items-center">
                <StatsCard typeStat={currentStat} statValue={currentValue} />
                <StatsCard typeStat={currentStat} statValue={currentValue} />
                <StatsCard typeStat={currentStat} statValue={currentValue} />
                <StatsCard typeStat={currentStat} statValue={currentValue} />
            </div>
        </div>
    )
}