import type { Transaction } from "../types/transactions";
import { Sparkles } from "lucide-react";
import { useState } from "react";

interface TransactionCardProps {
  transaction: Transaction;
}

type statusType = "Processed" | "Under Review" | "Blocked"

function getTransactionStatus(probability: number): statusType {
    if (probability < 0.3) {
        return "Processed";
    } else if (probability < 0.7) {
        return "Under Review";
    } else {
        return "Blocked";
    }
}

export default function TransactionInfo({ transaction }: TransactionCardProps) {
    const [showInsight, setShowInsight] = useState(false);
    const [loadingInsight, setLoadingInsight] = useState(false);

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

    const transactionStatus = getTransactionStatus(transaction.fraud_probability);

    const getStatusColor = (status: statusType) => {
        switch (status) {
            case "Processed": return "text-green-400";
            case "Under Review": return "text-yellow-400";
            case "Blocked": return "text-red-400";
            default: return "text-white";
        }
    };

    const handleGetInsight = async () => {
        setLoadingInsight(true);
        setShowInsight(true);

        // TODO: Call agent API here to get insights for this transaction
        // For now, just simulate a delay
        setTimeout(() => {
            setLoadingInsight(false);
        }, 1500);
    };

    return (
        <div className=" rounded-lg px-6 py-4" style={{ boxShadow: 'var(--shadow-m)' }}>
            <div className="flex flex-col space-y-2">
                {/* Header with merchant and amount */}
                <div className="flex justify-between items-start">
                    <div className="flex flex-row gap-x-23">
                        <div className="flex-col flex">
                            <h3 className="text-lg font-semibold text-white">{transaction.merchant}</h3>
                            <p className="text-xs text-white">{transaction.merchant_type}</p>
                        </div>
                        
                    </div>
                    <div className="text-right  ">
                        <p className="text-lg font-bold text-white">{formatAmount(transaction.amount, transaction.currency)}</p>
                        <p className="text-xs text-white">{formatTimestamp(transaction.timestamp)}</p>
                    </div>
                </div>

                <div className="flex flex-col">
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
                                <p className={`font-bold text-sm ${getStatusColor(transactionStatus)}`}>
                                    {transactionStatus}
                                </p>
                            </div>
                        </div>
                        
                        <div className="flex flex-col justify-end gap-2">
                            <div className="flex flex-col items-end">
                                <p className="text-white text-xs">Probability</p>
                                <p className="text-red-400 font-extrabold text-lg">{(transaction.fraud_probability * 100).toFixed(3)}%</p>
                            </div>
                        </div>
                    </div>

                    <button onClick={handleGetInsight} className="flex items-center gap-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 rounded text-xs font text-white transition-all">
                        <Sparkles className="w-3 h-3 bg-gradient-to-r from-purple-600 to-blue-600" />
                        AI Insight
                    </button>
                </div>


                {/* AI Insight Section */}
                {showInsight && (
                    <div className="mt-4 pt-4 border-t border-zinc-800">
                        <div className="flex items-center gap-2 mb-2">
                            <Sparkles className="w-4 h-4 text-purple-400" />
                            <h4 className="text-sm font-semibold text-white">AI Agent Insight</h4>
                        </div>
                        {loadingInsight ? (
                            <div className="flex items-center gap-2 text-zinc-400 text-sm">
                                <div className="w-4 h-4 border-2 border-purple-400 border-t-transparent rounded-full animate-spin"></div>
                                Analyzing transaction...
                            </div>
                        ) : (
                            <div className="bg-zinc-900 rounded p-3 text-sm text-zinc-300">
                                <p className="leading-relaxed">
                                    This transaction shows a fraud probability of {(transaction.fraud_probability * 100).toFixed(1)}%.
                                    The transaction originated from {transaction.city}, {transaction.country} using a {transaction.device} device
                                    via {transaction.channel} channel. Based on the location and device fingerprint, this appears to be a
                                    {transactionStatus === "Blocked" ? " high-risk" : transactionStatus === "Under Review" ? " medium-risk" : " low-risk"} transaction.
                                </p>
                                <p className="mt-2 text-xs text-zinc-500 italic">
                                    Note: This is a placeholder. Real insights will be provided by the AI agent.
                                </p>
                            </div>
                        )}
                    </div>
                )}
            </div>

        </div>
    );
}