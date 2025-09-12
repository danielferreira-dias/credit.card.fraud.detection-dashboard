import { useEffect, useState } from "react";

interface FilterElement  { 
    filterName : string, 
    filterValue : number 
}

type SortBy = "timestamp" | "amount" | "score";

interface TransactionFilters {
    date_from?: string;
    date_to?: string;
    amount_min?: number;
    amount_max?: number;
    currency?: string[];
    country?: string[];
    city?: string[];
    merchant?: string[];
    merchant_category?: string[];
    merchant_type?: string[];
    card_type?: string[];
    card_present?: (0 | 1)[];
    channel?: string[];
    device?: string[];
    device_fingerprint?: string | null;
    high_risk_merchant?: boolean | null;
    distance_from_home_min?: number;
    distance_from_home_max?: number;
    weekend_transaction?: boolean | null;
    hour_of_day?: number[];
    ip_address?: string | null;
    score_min?: number | null;
    score_max?: number | null;
    sort_by?: SortBy;
    sort_dir?: "asc" | "desc";
    page?: number;
    page_size?: number;
  }

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
        <div className="flex flex-col w-full mt-6 gap-y-4 items-center sm:items-start">
            <h2 className="text-xl font-semibold opacity-70 mt-6">Recent Transactions</h2>
            <div className="flex flex-row justify-between">
                <div className="flex sm:flex-row  items-center h-fit w-fit md:w-fit gap-y-4 border-zinc-800 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 rounded-xl border-[1px] flex-wrap">
                    { filterElements.map( (filter) => (
                        <button className="trasnform transition duration-100 ease-in flex h-fit flex-row flex-wrap w-full sm:w-fit gap-x-2 rounded-lg hover:bg-zinc-900 px-8 py-4">
                            <span className="text-sm opacity-90 h-fit ">{filter.filterName}</span>
                            <span className="text-sm opacity-55  h-fit">{formatValue(filter.filterValue)}</span>
                        </button>
                    ))}
                </div>

                <div className=""></div>

            </div>
        </div>
    )
}