import { useEffect, useState } from "react";
import type { Transaction } from "../types/transactions";

interface TransactionCardProps {
  transaction: Transaction;
}

type statusType = "Processed" | "Under Review" | "Blocked"

interface TransactionStatus {
    fraud_probability: string,
    status: statusType,
}

export default function TransactionInfo({ transaction }: TransactionCardProps) {
    
    const formatAmount = (amount: number, currency: string) => {
        return `${amount.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${currency}`;
    };

    const formatTimestamp = (timestamp: string) => {
        return new Date(timestamp).toLocaleString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getStatusColor = (status: statusType) => {
        switch (status) {
            case "Processed": return "text-green-400";
            case "Under Review": return "text-yellow-400";
            case "Blocked": return "text-red-400";
            default: return "text-white";
        }
    };

   

    return (
        <div className="bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-2 shadow-[0_0_8px_rgba(0,0,0,0.5)]">
            <div className="flex flex-col space-y-2">
                {/* Header with merchant and amount */}
                <div className="flex justify-between items-start">
                    <div>
                        <h3 className="text-lg font-semibold text-white">{transaction.merchant}</h3>
                        <p className="text-xs text-white">{transaction.merchant_type}</p>
                    </div>
                    <div className="text-right  ">
                        <p className="text-lg font-bold text-white">{formatAmount(transaction.amount, transaction.currency)}</p>
                        <p className="text-xs text-white">{formatTimestamp(transaction.timestamp)}</p>
                    </div>
                </div>

                <div className="flex flex-row w-full justify-between">
                    {/* Transaction details grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-8 gap-2 text-xs w-[95%]">
                        <div>
                            <p className="text-white">Customer ID</p>
                            <p className="text-white font-medium">{transaction.customer_id}</p>
                        </div>
                        <div>
                            <p className="text-white">Card Number</p>
                            <p className="text-white font-medium">{transaction.card_number}</p>
                        </div>
                        <div>
                            <p className="text-white">Card Type</p>
                            <p className="text-white font-medium">{transaction.card_type}</p>
                        </div>
                        <div>
                            <p className="text-white">Location</p>
                            <p className="text-white font-medium">{transaction.city}, {transaction.country}</p>
                        </div>
                        <div>
                            <p className="text-white">Device</p>
                            <p className="text-white font-medium">{transaction.device}</p>
                        </div>
                        <div>
                            <p className="text-white">Channel</p>
                            <p className="text-white font-medium capitalize">{transaction.channel}</p>
                        </div>
                        <div>
                            <p className="text-white">IP Address</p>
                            <p className="text-white font-medium font-mono">{transaction.ip_address}</p>
                        </div>
                        <div>
                            <p className="text-white">Status</p>
                            <p className={`font-medium ${getStatusColor('Under Review')}`}>
                                Under Review
                            </p>
                        </div>
                    </div>
                    <div className="flex flex-col justify-end">
                        <p className="text-white text-xs">Probability</p>
                        <p className="text-red-400 font-bold text-sm">0.80</p>
                    </div>
                </div>
            </div>
            
        </div>
    );
}