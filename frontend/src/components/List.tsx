import { useEffect, useMemo, useState } from "react";
import TransactionInfo from "./TransactionInfo";

export default function List(){
    const [total, setTotal] = useState<number>(42);
    const [page, setPage] = useState<number>(1);
    const pageSize = 5;

    const pageCount = Math.max(1, Math.ceil(total / pageSize));
    
    useEffect(() => {
        if (page > pageCount) setPage(pageCount);
    }, [pageCount, page]);

    
    const items = useMemo(() => {
        const start = (page - 1) * pageSize;
        const remaining = Math.max(0, total - start);
        const count = Math.min(pageSize, remaining);
        return Array.from({ length: count }, (_, i) => i);
    }, [page, total]);

    return (
        <div className="w-full h-fit text-white rounded-xl flex flex-col opacity-50 gap-y-1">
            {items.map((i) => (
                <TransactionInfo key={`${page}-${i}`} />
            ))}

            <div className="flex items-center justify-center gap-4 mt-3">
                <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-700 hover:bg-zinc-800 ">
                    <img src="/left-arrow-backup-2-svgrepo-com.svg" alt="Toggle sidebar" className={`w-3 h-3 m-auto transform transition duration-300 `} />
                </button>
                <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="rounded-full w-8 h-8 bg-zinc-900 border border-zinc-700 hover:bg-zinc-800  text-white">
                    1
                </button>
                <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="rounded-full w-8 h-8 bg-zinc-900 border border-zinc-700 hover:bg-zinc-800  text-white">
                    2
                </button>
                
                <span className="text-xs opacity-70">...</span>
                <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="rounded-full w-8 h-8 bg-zinc-900 border border-zinc-700 hover:bg-zinc-800  text-white">
                    {pageCount-1}
                </button>
                <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="rounded-full w-8 h-8 bg-zinc-900 border border-zinc-700 hover:bg-zinc-800  text-white">
                    {pageCount}
                </button>
                <button
                    onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
                    disabled={page === pageCount}
                    className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-700 hover:bg-zinc-800 ">
                    <img src="/right-chevron-svgrepo-com.svg" alt="Toggle sidebar" className={`w-3 h-3 m-auto transform transition duration-300 `} />
                </button>
            </div>
        </div>
    )
}