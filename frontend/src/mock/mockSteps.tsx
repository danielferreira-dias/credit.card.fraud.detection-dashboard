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
        content: "✅ Retrieved 50 transactions from database\n\nFound transactions from various customers with amounts ranging from $10 to $5000",
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