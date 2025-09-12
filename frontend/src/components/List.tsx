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

    const trio = useMemo(() => {
        if (pageCount <= 5) {
            return Array.from({ length: pageCount }, (_, i) => i + 1);
        }
        if (page <= 2) {
            return [1, 2, 3];                  
        }
        if (page >= pageCount - 1) {
            return [1, 2, 3];                  
        }
        return [page - 1, page, page + 1];     
    }, [page, pageCount]);

    const showRightEllipsis = pageCount > 5 && (trio[trio.length - 1] < pageCount - 2);

    const isInTrio = (n: number) => trio.includes(n);

    return (
        <div className="w-full h-fit text-white rounded-xl flex flex-col opacity-50 gap-y-1">
            {items.map((i) => (
                <TransactionInfo key={`${page}-${i}`} />
            ))}

            <div className="flex items-center justify-center gap-4 mt-3">
                <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-700 hover:bg-zinc-800 disabled:opacity-40">
                    <img src="/left-arrow-backup-2-svgrepo-com.svg" alt="Prev" className="w-3 h-3 m-auto transform transition duration-300" />
                </button>

                {trio.map(n => (
                    <button
                        key={n}
                        onClick={() => setPage(n)}
                        className={`rounded-full w-8 h-8 border border-zinc-700 text-white ${
                            page === n ? "bg-zinc-700" : "bg-zinc-900 hover:bg-zinc-800"
                        }`}>
                        {n}
                    </button>
                ))}

                {showRightEllipsis && <span className="text-xs opacity-70">...</span>}

                {pageCount >= 2 && !isInTrio(pageCount - 1) && (
                    <button
                        onClick={() => setPage(pageCount - 1)}
                        className={`rounded-full w-8 h-8 border border-zinc-700 text-white ${
                            page === pageCount - 1 ? "bg-zinc-700" : "bg-zinc-900 hover:bg-zinc-800"
                        }`}>
                        {pageCount - 1}
                    </button>
                )}

                {pageCount >= 1 && !isInTrio(pageCount) && (
                    <button
                        onClick={() => setPage(pageCount)}
                        className={`rounded-full w-8 h-8 border border-zinc-700 text-white ${
                            page === pageCount ? "bg-zinc-700" : "bg-zinc-900 hover:bg-zinc-800"
                        }`}>
                        {pageCount}
                    </button>
                )}

                <button
                    onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
                    disabled={page === pageCount}
                    className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-700 hover:bg-zinc-800 disabled:opacity-40">
                    <img src="/right-chevron-svgrepo-com.svg" alt="Next" className="w-3 h-3 m-auto transform transition duration-300" />
                </button>
            </div>
        </div>
    )
}