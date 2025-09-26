export const mockStepsTest = [
    {
        type: "progress",
        content: "🤔 Analyzing your request about fraud detection...",
        progress_type: "thinking",
        timestamp: new Date().toISOString()
    },
    {
        type: "progress",
        content: "🔧 Invoking get_all_transactions_tool to retrieve transaction data...",
        progress_type: "tool_call",
        timestamp: new Date().toISOString()
    },
    {
        type: "progress",
        content: "Transaction history for customer Daniel Dias:\n\nResults \n1. Customer: CUST_72886 | Amount: $377.43 | Fraud: No2. Customer: CUST_70474 | Amount: $572.72 | Fraud: Yes3. Customer: CUST_10715 | Amount: $666.79 | Fraud: No4. Customer: CUST_16193 | Amount: $409.89 | Fraud: No5. Customer: CUST_87572 | Amount: $434.97 | Fraud: Yes6. Customer: CUST_55630 | Amount: $2.00 | Fraud: Yes7. Customer: CUST_89147 | Amount: $443.05 | Fraud: No8. Customer: CUST_10150 | Amount: $878.03 | Fraud: No9. Customer: CUST_83143 | Amount: $62.95 | Fraud: No10. Customer: CUST_35022 | Amount: $2524.57 | Fraud: Yes11. Customer: CUST_64274 | Amount: $346.45 | Fraud: No12. Customer: CUST_65989 | Amount: $561.34 | Fraud: No13. Customer: CUST_82514 | Amount: $282.95 | Fraud: No14. Customer: CUST_42282 | Amount: $0.37 | Fraud: Yes15. Customer: CUST_79886 | Amount: $699.49 | Fraud: No16. Customer: CUST_80907 | Amount: $349.98 | Fraud: No17. Customer: CUST_81861 | Amount: $1186.18 | Fraud: No18. Customer: CUST_75970 | Amount: $1333.25 | Fraud: No19. Customer: CUST_75986 | Amount: $448.72 | Fraud: No20. Customer: CUST_75433 | Amount: $393.74 | Fraud: No  ",
        progress_type: "tool_result",
        timestamp: new Date().toISOString()
    },
    {
        type: "progress",
        content: "🤔 Now I need to check for fraud patterns. Let me get the fraud-specific data...",
        progress_type: "thinking",
        timestamp: new Date().toISOString()
    },
    {
        type: "progress",
        content: "🔧 Invoking get_fraud_transactions_tool to analyze fraudulent patterns...",
        progress_type: "tool_call",
        timestamp: new Date().toISOString()
    },
    {
        type: "progress",
        content: "✅ Found 8 fraudulent transactions\n\nAnalysis shows:\n- 3 transactions with suspicious amounts over $3000\n- 5 transactions from flagged customer IDs\n- Average fraud amount: $2,845",
        progress_type: "tool_result",
        timestamp: new Date().toISOString()
    }
];