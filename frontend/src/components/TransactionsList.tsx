import { useEffect, useState } from "react";
import List from "./List";
import type { Transaction } from "../types/transactions";

interface FilterElement  { 
    filterName : string, 
    filterValue : number 
}

function formatValue(value: number): string {
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
    return `${value}`;
  }

interface TransactionListProps {
    totalTransactions: number;
    itemsPerPage: number;
}

export default function TransactionList({ totalTransactions, itemsPerPage }: TransactionListProps){
    const [filterElements, setFilterElements] = useState<FilterElement[]>([]);
    const [searchQuery, setSearchQuery] = useState<string>("");
    const [dataTransactions, setDataTransactions] = useState<Transaction[]>([]);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [totalPages, setTotalPages] = useState<number>(Math.ceil(totalTransactions / itemsPerPage));
    const [loadingPage, setLoadingPage] = useState(true);
    const limit = itemsPerPage;

    // Update totalPages when props change
    useEffect(() => {
        setTotalPages(Math.ceil(totalTransactions / itemsPerPage));
    }, [totalTransactions, itemsPerPage]);

    useEffect(() => {
        const fetchFilters = async () => {
            // Check cache first
            const cachedData = sessionStorage.getItem(`transactions_page_${currentPage}`);    
            const cacheTime = sessionStorage.getItem(`transactions_timestamp_${currentPage}`);

            if (cachedData && cacheTime) {
                const age = Date.now() - parseInt(cacheTime);
                if (age < 2 * 60 * 1000) { // 2 minutes cache
                const parsedCachedData = JSON.parse(cachedData);
                setDataTransactions(parsedCachedData);
                console.log("cachedData -> ", parsedCachedData)

                // Process the cached data to create filter elements with counts
                const allTransactions = parsedCachedData.length;
                const nonFraudTransactions : number = parsedCachedData.filter((t: any) => t.is_fraud === false).length;
                const fraudTransactions : number = parsedCachedData.filter((t: any) => t.is_fraud === true).length;
                const suspiciousTransactions : number = parsedCachedData.filter((t: any) => t.fraud_probability > 0.3 && t.fraud_probability < 0.8).length;

                const filterData = [
                    { filterName: "All", filterValue: allTransactions },
                    { filterName: "Normal", filterValue: nonFraudTransactions },
                    { filterName: "Suspicious", filterValue: suspiciousTransactions },
                    { filterName: "Fraudulent", filterValue: fraudTransactions },
                ];
                setFilterElements(filterData);

                setLoadingPage(false);
                return;
                }
            }
            try {
                const skip = (currentPage - 1) * limit;
                const res = await fetch(`http://localhost:80/transactions/?include_predictions=true&limit=${limit}&skip=${skip}`);
                if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`);
                const data = await res.json();
                setDataTransactions(data);
                
                // Cache the data
                sessionStorage.setItem(`transactions_page_${currentPage}`,JSON.stringify(data));
                sessionStorage.setItem(`transactions_timestamp_${currentPage}`,Date.now().toString());

                // Process the data to create filter elements with counts
                const allTransactions = data.length;
                const nonFraudTransactions : number = data.filter((t: any) => t.is_fraud === false).length;
                const suspiciousTransactions : number = data.filter((t: any) => t.fraud_probability > 0.3 && t.fraud_probability < 0.8).length;
                const fraudTransactions : number = data.filter((t: any) => t.is_fraud === true).length;

                const filterData = [
                    { filterName: "All", filterValue: allTransactions },
                    { filterName: "Normal", filterValue: nonFraudTransactions },
                    { filterName: "Suspicious", filterValue: suspiciousTransactions },
                    { filterName: "Fraudulent", filterValue: fraudTransactions },
                ];
                setFilterElements(filterData);
            } catch (error) {
                console.error('Failed to fetch transactions:', error);
                setFilterElements([]);
            } finally {
                setLoadingPage(false);
            }
            };
            fetchFilters();
        }, [currentPage]);

    return (
        <div className="flex flex-col w-full h-full mt-6 gap-y-4 items-center sm:items-start">
            <h2 className="text-xl font-semibold opacity-70 mt-6">Recent Transactions</h2>
            <div className="flex flex-row justify-between items-stretch w-full gap-x-4">
                <div className="flex sm:flex-row  items-center h-full w-fit md:w-fit gap-y-4 border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 rounded-xl border-[1px] flex-wrap">
                    { filterElements.map( (filter) => (
                        <button className="trasnform transition duration-100 ease-in flex h-fit flex-row flex-wrap w-full sm:w-fit gap-x-2 rounded-lg hover:bg-zinc-900 px-8 py-4">
                            <span className="text-sm opacity-90 h-fit ">{filter.filterName}</span>
                            <span className="text-sm opacity-55  h-fit">{formatValue(filter.filterValue)}</span>
                        </button>
                    ))}
                </div>
                
                <div className="relative border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 h-fit xl:h-full rounded-xl border-[1px] items-center">
                    <div className="absolute inset-y-0 left-0 pl-3 flex h-full items-center pointer-events-none">
                        <svg className="h-4 w-4 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>
                    <input
                        type="text"
                        placeholder="Search Transactions"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className=" h-full rounded-xl pl-10 pr-4 py-3 text-sm text-white focus:ring-black border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)]   flex-1"
                    />
                </div>
            </div>
             {/* Pagination Controls */}
            {totalPages > 1 && (
                <div className="flex justify-start items-center gap-x-4 mt-4 w-full">
                    <button
                        onClick={() => setCurrentPage(1)}
                        disabled={currentPage === 1}
                        className="transform transition duration-100 ease-in flex items-center justify-center w-8 h-8 rounded-lg border border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 hover:bg-zinc-900 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent text-sm font-medium"
                    >
                        {"<<"}
                    </button>
                    <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="transform transition duration-100 ease-in flex items-center justify-center w-8 h-8 rounded-lg border border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 hover:bg-zinc-900 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent text-sm font-medium"
                    >
                        {"<"}
                    </button>
                    <div className="flex items-center justify-center px-4 py-2 rounded-lg border border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 bg-zinc-900 text-sm font-medium min-w-[60px]">
                        {currentPage}
                    </div>
                    <button
                        onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                        disabled={currentPage === totalPages}
                        className="transform transition duration-100 ease-in flex items-center justify-center w-8 h-8 rounded-lg border border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 hover:bg-zinc-900 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent text-sm font-medium"
                    >
                        {">"}
                    </button>
                    <button
                        onClick={() => setCurrentPage(totalPages)}
                        disabled={currentPage === totalPages}
                        className="transform transition duration-100 ease-in flex items-center justify-center w-8 h-8 rounded-lg border border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 hover:bg-zinc-900 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent text-sm font-medium"
                    >
                        {">>"}
                    </button>
                </div>
            )}
            <List transactionsList={dataTransactions} isLoadingPage={loadingPage}/>
            {/* Pagination Controls */}
            {totalPages > 1 && (
                <div className="flex justify-center items-center gap-x-4 mt-4 w-full">
                    <button
                        onClick={() => setCurrentPage(1)}
                        disabled={currentPage === 1}
                        className="transform transition duration-100 ease-in flex items-center justify-center w-8 h-8 rounded-lg border border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 hover:bg-zinc-900 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent text-sm font-medium"
                    >
                        {"<<"}
                    </button>
                    <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="transform transition duration-100 ease-in flex items-center justify-center w-8 h-8 rounded-lg border border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 hover:bg-zinc-900 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent text-sm font-medium"
                    >
                        {"<"}
                    </button>
                    <div className="flex items-center justify-center px-4 py-2 rounded-lg border border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 bg-zinc-900 text-sm font-medium min-w-[60px]">
                        {currentPage}
                    </div>
                    <button
                        onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                        disabled={currentPage === totalPages}
                        className="transform transition duration-100 ease-in flex items-center justify-center w-8 h-8 rounded-lg border border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 hover:bg-zinc-900 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent text-sm font-medium"
                    >
                        {">"}
                    </button>
                    <button
                        onClick={() => setCurrentPage(totalPages)}
                        disabled={currentPage === totalPages}
                        className="transform transition duration-100 ease-in flex items-center justify-center w-8 h-8 rounded-lg border border-zinc-900 shadow-[0_0_8px_rgba(0,0,0,0.5)] shadow-zinc-700 hover:bg-zinc-900 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent text-sm font-medium"
                    >
                        {">>"}
                    </button>
                </div>
            )}
        </div>
    )
}