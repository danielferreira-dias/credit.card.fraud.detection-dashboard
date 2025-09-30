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

// export const simulateMockAgentResponse = async () => {
//     setIsTyping(true);
//     const mockSteps = mockStepsTest
//     // Accumulate reasoning steps locally (fixes async state issue)
//     const accumulatedSteps: ReasoningStep[] = [];
//     // Simulate streaming responses
//     for (let i = 0; i < mockSteps.length; i++) {
//         await new Promise(resolve => setTimeout(resolve, 1000)); // Delay between steps
//         const mockMessage = mockSteps[i];
//         // Create reasoning step
//         const newStep: ReasoningStep = {
//             type: mockMessage.progress_type === 'tool_call' ? 'tool_call' :
//                     mockMessage.progress_type === 'tool_result' ? 'tool_result' :
//                     mockMessage.progress_type === 'tool_progress' ? 'tool_progress' :
//                     mockMessage.progress_type === 'final_response' ? 'final_response' :
//                     'thinking',
//             content: mockMessage.content,
//             toolName: mockMessage.progress_type === 'tool_call' || mockMessage.progress_type === 'tool_result'
//                 ? extractToolNameFromContent(mockMessage.content) : undefined,
//             timestamp: mockMessage.timestamp
//         };
//         // Add to local accumulator
//         accumulatedSteps.push(newStep);
//         // Update state for real-time display
//         setCurrentReasoningSteps([...accumulatedSteps]);
//         setMessages(prev => {
//             const withoutProgress = prev.filter(m => m.type !== 'progress');
//             return [...withoutProgress, {
//                 type: 'progress' as const,
//                 content: mockMessage.content,
//                 timestamp: mockMessage.timestamp,
//                 progress_type: mockMessage.progress_type
//             }];
//         });
//     }
//     // Final response
//     await new Promise(resolve => setTimeout(resolve, 1000));
//     setIsTyping(false);
//     const finalResponse = {
//         type: 'Agent' as const,
//         content: "Here are the first 20 transactions from the database:\n\n1. **Customer:** CUST_72886 | **Amount:** $377.43 | **Fraud:** No  \n2. **Customer:** CUST_70474 | **Amount:** $572.72 | **Fraud:** Yes  \n3. **Customer:** CUST_10715 | **Amount:** $666.79 | **Fraud:** No  \n4. **Customer:** CUST_16193 | **Amount:** $409.89 | **Fraud:** No  \n5. **Customer:** CUST_87572 | **Amount:** $434.97 | **Fraud:** Yes  \n6. **Customer:** CUST_55630 | **Amount:** $2.00 | **Fraud:** Yes  \n7. **Customer:** CUST_89147 | **Amount:** $443.05 | **Fraud:** No  \n8. **Customer:** CUST_10150 | **Amount:** $878.03 | **Fraud:** No  \n9. **Customer:** CUST_83143 | **Amount:** $62.95 | **Fraud:** No  \n10. **Customer:** CUST_35022 | **Amount:** $2524.57 | **Fraud:** Yes  \n11. **Customer:** CUST_64274 | **Amount:** $346.45 | **Fraud:** No  \n12. **Customer:** CUST_65989 | **Amount:** $561.34 | **Fraud:** No  \n13. **Customer:** CUST_82514 | **Amount:** $282.95 | **Fraud:** No  \n14. **Customer:** CUST_42282 | **Amount:** $0.37 | **Fraud:** Yes  \n15. **Customer:** CUST_79886 | **Amount:** $699.49 | **Fraud:** No  \n16. **Customer:** CUST_80907 | **Amount:** $349.98 | **Fraud:** No  \n17. **Customer:** CUST_81861 | **Amount:** $1186.18 | **Fraud:** No  \n18. **Customer:** CUST_75970 | **Amount:** $1333.25 | **Fraud:** No  \n19. **Customer:** CUST_75986 | **Amount:** $448.72 | **Fraud:** No  \n20. **Customer:** CUST_75433 | **Amount:** $393.74 | **Fraud:** No  \n\n⚠️ Note: The **transaction IDs** are currently missing in this dataset, so identifying specific transactions will need additional queries.\n\nDo you want me to show **the next 20 transactions** or perhaps filter only **fraudulent ones**?",
//         timestamp: new Date().toISOString(),
//         reasoning_steps: accumulatedSteps // Use local accumulator instead of state
//     };
//     setMessages(prev => {
//         const withoutProgress = prev.filter(m => m.type !== 'progress');
//         const newMessages = [...withoutProgress, finalResponse];
//         // Start typing animation for the new message
//         const messageIndex = newMessages.length - 1;
//         setTimeout(() => startTypingAnimation(messageIndex, finalResponse.content), 100);
//         return newMessages;
//     });
//     setCurrentReasoningSteps([]);
// };