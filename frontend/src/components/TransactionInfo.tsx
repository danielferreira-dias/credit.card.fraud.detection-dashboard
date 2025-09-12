import { useEffect, useState } from "react";

interface TransactionData {
    customer_id: string,
    card_number: string,
    timestamp: string,
    merchant: string,
    merchant_type: string,
    amount: number,
    currency: string,
    country: string,
    city: string,
    card_type: string,
    device: string,
    channel: string,
    ip_address: string,
    status: TransactionStatus,
}

type statusType = "Processed" | "Under Review" | "Blocked"

interface TransactionStatus {
    fraud_probability: string,
    status: statusType,
}

export default function TransactionInfo() {
    const [transaction, setTransaction] = useState<TransactionData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchTransaction = async () => {
            try {
                setLoading(true);
                // Simulating API call
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                const mockData: TransactionData = {
                    customer_id: "CUST_72886",
                    card_number: "************3109",
                    timestamp: "2024-09-30T00:00:01.034820",
                    merchant: "Taco Bell",
                    merchant_type: "fast_food",
                    amount: 294.87,
                    currency: "GBP",
                    country: "UK",
                    city: "London",
                    card_type: "Platinum Credit",
                    device: "iOS App",
                    channel: "mobile",
                    ip_address: "197.153.60.199",
                    status: {
                        fraud_probability: "85%",
                        status: "Under Review"
                    }
                };
                
                setTransaction(mockData);
            } catch (error) {
                console.error("Error fetching transaction:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchTransaction();
    }, []);

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
            default: return "text-gray-200";
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
            </div>
        );
    }

    if (!transaction) {
        return (
            <div className="text-center p-8 text-gray-200">
                No transaction data available
            </div>
        );
    }

    return (
        <div className="bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-2 shadow-[0_0_8px_rgba(0,0,0,0.5)]">
            <div className="flex flex-col space-y-2">
                {/* Header with merchant and amount */}
                <div className="flex justify-between items-start">
                    <div>
                        <h3 className="text-lg font-semibold text-white">{transaction.merchant}</h3>
                        <p className="text-xs text-gray-200">{transaction.merchant_type}</p>
                    </div>
                    <div className="text-right  ">
                        <p className="text-lg font-bold text-white">{formatAmount(transaction.amount, transaction.currency)}</p>
                        <p className="text-xs text-gray-200">{formatTimestamp(transaction.timestamp)}</p>
                    </div>
                </div>

                <div className="flex flex-row w-full justify-between">
                    {/* Transaction details grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs w-[95%]">
                        <div>
                            <p className="text-gray-200">Customer ID</p>
                            <p className="text-white font-medium">{transaction.customer_id}</p>
                        </div>
                        <div>
                            <p className="text-gray-200">Card Number</p>
                            <p className="text-white font-medium">{transaction.card_number}</p>
                        </div>
                        <div>
                            <p className="text-gray-200">Card Type</p>
                            <p className="text-white font-medium">{transaction.card_type}</p>
                        </div>
                        <div>
                            <p className="text-gray-200">Location</p>
                            <p className="text-white font-medium">{transaction.city}, {transaction.country}</p>
                        </div>
                        <div>
                            <p className="text-gray-200">Device</p>
                            <p className="text-white font-medium">{transaction.device}</p>
                        </div>
                        <div>
                            <p className="text-gray-200">Channel</p>
                            <p className="text-white font-medium capitalize">{transaction.channel}</p>
                        </div>
                        <div>
                            <p className="text-gray-200">IP Address</p>
                            <p className="text-white font-medium font-mono">{transaction.ip_address}</p>
                        </div>
                        <div>
                            <p className="text-gray-200">Status</p>
                            <p className={`font-medium ${getStatusColor(transaction.status.status)}`}>
                                {transaction.status.status}
                            </p>
                        </div>
                    </div>
                    <div className="flex flex-col justify-end">
                        <p className="text-gray-200 text-xs">Probability</p>
                        <p className="text-red-400 font-bold text-sm">{transaction.status.fraud_probability}</p>
                    </div>
                </div>
            </div>
            
        </div>
    );
}