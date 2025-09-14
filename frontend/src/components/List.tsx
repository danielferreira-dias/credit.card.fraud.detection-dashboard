import { useEffect, useState } from "react";
import TransactionInfo from "./TransactionInfo";
import type { Transaction } from "../types/transactions";

export default function List( { transactionsList } : { transactionsList : Transaction[] } ){
    console.log("transactionsList in List component -> ", transactionsList);
    const totalTransactions = transactionsList.length;
    const listTransactions : Transaction[] = transactionsList;

    const [page, setPage] = useState<number>(1);
    const pageSize = 5;

    const pageCount = Math.max(1, Math.ceil(totalTransactions / pageSize));
    
    useEffect(() => {
        if (page > pageCount) setPage(pageCount);
    }, [pageCount, page]);

    console.log("listTransactions -> ", listTransactions);

    return (
        <div className="w-full h-fit text-white rounded-xl flex flex-col opacity-50 gap-y-1">
            {listTransactions.map((currTransaction) => (
                <TransactionInfo key={currTransaction.timestamp} transaction={currTransaction} />
            ))}

            
        </div>
    )
}