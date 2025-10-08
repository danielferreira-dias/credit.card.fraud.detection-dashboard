import { useUser } from "@/context/UserContext";
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
    const [analysisData, setAnalysisData] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const { user } = useUser();

    console.log('transaction -> ', transaction)

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
        setError(null);

        try {
            // Call the backend analysis endpoint
            // Note: Using user_id = 1 as a default. In a real app, this would come from authentication context
            const userId = user?.id;
            const response = await fetch(`http://localhost:80/transactions/analysis/${userId}?transaction_id=${transaction.transaction_id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            

            if (!response.ok) {
                throw new Error(`Analysis request failed: ${response.status}`);
            }

            const data = await response.json();

            console.log('data -> ', data)

            // Extract the analysis content from the response
            const analysisContent = data.analysis_content || data.report_content || data;

            // If the analysis content is a string, use it directly, otherwise extract meaningful text
            if (typeof analysisContent === 'string') {
                setAnalysisData(analysisContent);
            } else if (analysisContent && typeof analysisContent === 'object') {
                // Try to extract text content from the object
                const textContent = analysisContent.text || analysisContent.content || analysisContent.analysis || JSON.stringify(analysisContent, null, 2);
                setAnalysisData(textContent);
            } else {
                setAnalysisData('Analysis completed successfully, but no detailed content was returned.');
            }
        } catch (err) {
            console.error('Failed to get analysis:', err);
            setError(err instanceof Error ? err.message : 'Failed to get analysis');
            setAnalysisData(null);
        } finally {
            setLoadingInsight(false);
        }
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
                        ) : error ? (
                            <div className="bg-red-950 border border-red-800 rounded p-3 text-sm text-red-300">
                                <p className="font-semibold">Analysis Error</p>
                                <p className="mt-1">{error}</p>
                                <button
                                    onClick={handleGetInsight}
                                    className="mt-2 text-xs underline hover:text-red-200"
                                >
                                    Try again
                                </button>
                            </div>
                        ) : analysisData ? (
                            <div className="bg-zinc-900 rounded p-3 text-sm text-zinc-300">
                                <div className="leading-relaxed whitespace-pre-wrap">
                                    {analysisData}
                                </div>
                            </div>
                        ) : (
                            <div className="bg-zinc-900 rounded p-3 text-sm text-zinc-300">
                                <p className="leading-relaxed">
                                    No analysis data available. Please try clicking the "AI Insight" button again.
                                </p>
                            </div>
                        )}
                    </div>
                )}
            </div>

        </div>
    );
}