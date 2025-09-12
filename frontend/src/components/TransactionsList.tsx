import { useEffect, useState } from "react";

interface FilterElement  { filterName : string, filterValue : number }

function formatValue(value: number): string {
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
    return `${value}`;
  }

export default function TransactionList(){
    const [filterElements, setFilterElements] = useState<FilterElement[]>([]);

    useEffect(() => {
        // Simulando fetch
        const fetchFilters = async () => {
          // Simulando dados vindos da API
          const dataFromAPI = [
            { filterName: "All", filterValue: 2000000 },
            { filterName: "Normal", filterValue: 1000000 },
            { filterName: "Suspicious", filterValue: 700000 },
            { filterName: "Fraudulent", filterValue: 900000 },
          ];
          setFilterElements(dataFromAPI);
        };
    
        fetchFilters();
      }, []);

    return (
        <div className="flex flex-col w-full mt-6 gap-y-4">
            <h2 className="text-xl font-semibold opacity-70 mt-6">Recent Transactions</h2>
            <div className="flex flex-col md:flex-row h-fit pt-4 pb-4 px-6 py-6 w-full gap-x-6 gap-y-2 rounded-xl border-[1px] border-amber-400 flex-wrap">
                { filterElements.map( (filter) => (
                    <div className="flex flex-row flex-wrap gap-x-2">
                        <span className="text-sm opacity-90 ">{filter.filterName}</span>
                        <span className="text-sm opacity-55 ">{formatValue(filter.filterValue)}</span>
                    </div>
                ))}
            </div>
        </div>
    )
}