
import { useState, useRef, useEffect } from 'react';
import { ReasoningFlowComponent } from '../components/ReasoningFlowComponent';
import { mockStepsTest } from '../mock/mockSteps';

interface ReasoningStep {
    type: 'thinking' | 'tool_call' | 'tool_result' | 'final_response';
    content: string;
    toolName?: string;
    timestamp: string;
}
interface Message {
    type: 'system' | 'User' | 'Agent' | 'typing' | 'progress' | 'error';
    content: string;
    timestamp: string;
    progress_type?: string;
    reasoning_steps?: ReasoningStep[];
}

export default function AgentPage(){
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isConnected, setIsConnected] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [currentReasoningSteps, setCurrentReasoningSteps] = useState<ReasoningStep[]>([]);
    const [expandedReasoning, setExpandedReasoning] = useState<{[key: number]: boolean}>({});
    const [useMockResponse, setUseMockResponse] = useState(false); // Toggle for testing
    const wsRef = useRef<WebSocket | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const reasoningStepsRef = useRef<ReasoningStep[]>([]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const extractToolNameFromContent = (content: string): string => {
        // Try to extract tool name from content patterns
        const toolMatch = content.match(/(?:using|calling|invoking|executing)\s+(\w+)/i) ||
                         content.match(/tool:\s*(\w+)/i) ||
                         content.match(/(\w+)_tool/i);
        return toolMatch ? toolMatch[1] : 'Unknown';
    };

    const simulateMockAgentResponse = async () => {
        setIsTyping(true);
        const mockSteps = mockStepsTest
        // Accumulate reasoning steps locally (fixes async state issue)
        const accumulatedSteps: ReasoningStep[] = [];
        // Simulate streaming responses
        for (let i = 0; i < mockSteps.length; i++) {
            await new Promise(resolve => setTimeout(resolve, 1000)); // Delay between steps
            const mockMessage = mockSteps[i];
            // Create reasoning step
            const newStep: ReasoningStep = {
                type: mockMessage.progress_type === 'tool_invocation' ? 'tool_call' :
                      mockMessage.progress_type === 'tool_result' ? 'tool_result' : 'thinking',
                content: mockMessage.content,
                toolName: mockMessage.progress_type === 'tool_invocation' || mockMessage.progress_type === 'tool_result'
                    ? extractToolNameFromContent(mockMessage.content) : undefined,
                timestamp: mockMessage.timestamp
            };
            // Add to local accumulator
            accumulatedSteps.push(newStep);
            // Update state for real-time display
            setCurrentReasoningSteps([...accumulatedSteps]);
            setMessages(prev => {
                const withoutProgress = prev.filter(m => m.type !== 'progress');
                return [...withoutProgress, {
                    type: 'progress' as const,
                    content: mockMessage.content,
                    timestamp: mockMessage.timestamp,
                    progress_type: mockMessage.progress_type
                }];
            });
        }
        // Final response
        await new Promise(resolve => setTimeout(resolve, 1000));
        setIsTyping(false);
        const finalResponse = {
            type: 'Agent' as const,
            content: `Based on the analysis of your transaction data:

            📊 **Transaction Summary:**
            - Total transactions analyzed: 50
            - Fraudulent transactions found: 8
            - Fraud rate: 16%

            🚨 **Key Findings:**
            - High-value transactions (>$3000) show 60% fraud rate
            - Customer ID patterns suggest potential account compromise
            - Peak fraud activity occurs in transactions between $2000-$4000

            💡 **Recommendations:**
            1. Implement additional verification for transactions over $2000
            2. Monitor flagged customer accounts more closely
            3. Consider real-time fraud scoring for high-value transactions

            The get_all_transactions_tool and get_fraud_transactions_tool provided comprehensive data for this analysis.`,
            timestamp: new Date().toISOString(),
            reasoning_steps: accumulatedSteps // Use local accumulator instead of state
        };
        setMessages(prev => {
            const withoutProgress = prev.filter(m => m.type !== 'progress');
            return [...withoutProgress, finalResponse];
        });
        setCurrentReasoningSteps([]);
    };

    // Websocket Managment
    useEffect(() => {
        const connectWebSocket = () => {
            const ws = new WebSocket('ws://localhost:80/chat/ws/agent/0');
            ws.onopen = () => {
                console.log('Connected to agent WebSocket');
                setIsConnected(true);
            };
            ws.onmessage = (event) => {
                const message: Message = JSON.parse(event.data);
                console.log("WebSocket message received:", message);

                // Skip User messages from WebSocket - they're already added locally
                if (message.type === 'User') {
                    console.log("Skipping User message from WebSocket (already added locally)");
                    return;
                }

                if (message.type === 'typing') {
                    setIsTyping(true);
                    return;
                }

                // Handle progress messages differently
                if (message.type === 'progress') {
                    // Keep typing true during progress - agent is still working
                    setIsTyping(true);

                    // Collect reasoning steps based on progress type
                    const newStep: ReasoningStep = {
                        type: message.progress_type === 'tool_invocation' ? 'tool_call' :
                              message.progress_type === 'tool_result' ? 'tool_result' :
                              message.progress_type === 'final_response' ? 'final_response' : 'thinking',
                        content: message.content.replace(/\\n/g, '\n'),
                        toolName: message.progress_type === 'tool_invocation' || message.progress_type === 'tool_result'
                            ? extractToolNameFromContent(message.content) : undefined,
                        timestamp: message.timestamp || new Date().toISOString()
                    };

                    // Add new process step to the Reasoning Steps
                    reasoningStepsRef.current = [...reasoningStepsRef.current, newStep];
                    setCurrentReasoningSteps(reasoningStepsRef.current);
                    console.log('Updated reasoning steps:', reasoningStepsRef.current);

                    // Add progress message temporarily
                    const processedMessage = {
                        ...message,
                        content: message.content.replace(/\\n/g, '\n')
                    };

                    setMessages(prev => {
                        // Remove previous progress messages to keep only the latest
                        const withoutProgress = prev.filter(m => m.type !== 'progress');
                        return [...withoutProgress, processedMessage];
                    });
                    return;
                }

                // Agent final message - stop typing
                setIsTyping(false);

                // Process final agent message
                const processedMessage = {
                    ...message,
                    content: message.content.replace(/\\n/g, '\n'),
                    reasoning_steps: reasoningStepsRef.current
                };

                console.log("processedMessage -> ", processedMessage)

                setMessages(prev => {
                    console.log('Previous messages before adding final:', prev.length);
                    // Remove progress messages when final message arrives
                    const withoutProgress = prev.filter(m => m.type !== 'progress');
                    const updated = [...withoutProgress, processedMessage];
                    console.log('Messages after adding final:', updated.length);
                    return updated;
                });

                // Clear reasoning steps after final message
                if (message.type === 'Agent') {
                    reasoningStepsRef.current = [];
                    setCurrentReasoningSteps([]);
                }
            };
            ws.onclose = () => {
                console.log('WebSocket connection closed');
                setIsConnected(false);
                // Attempt to reconnect after 3 seconds
                setTimeout(connectWebSocket, 3000);
            };
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                setIsConnected(false);
            };
            wsRef.current = ws;
        };
        // Calls Websocket function
        connectWebSocket();
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    // SendMessage Management
    const sendMessage = () => {
        if (!inputMessage.trim()) return;

        const userMessage = inputMessage.trim();
        // Add user message to chat
        const userMessageObj = {
            type: 'User' as const,
            content: userMessage,
            timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, userMessageObj]);
        setInputMessage('');
        // Reset textarea height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
        // Use mock response or real WebSocket
        if (useMockResponse) {
            simulateMockAgentResponse();
        } else {
            if (!wsRef.current || !isConnected) return;
            const messageData = {
                content: userMessage
            };
            wsRef.current.send(JSON.stringify(messageData));
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const toggleReasoningExpansion = (messageIndex: number) => {
        setExpandedReasoning(prev => ({
            ...prev,
            [messageIndex]: !prev[messageIndex]
        }));
    };

    
    return (
        <div className="flex w-full min-h-screen max-h-[fit] gap-x-2">
            <div className="flex flex-col h-full w-[80%] text-white border-[1px] rounded-xl bg-[#0F0F11] border-zinc-700 min-h-screen max-h-[fit]">

                <div className="flex-1 p-4 overflow-y-auto">
                    {/* Connection status and mock toggle */}
                    <div className="flex items-center justify-between mb-4">
                        <div className={`text-sm px-3 py-2 rounded-lg w-fit ${
                            isConnected
                                ? 'bg-green-900/15 text-green-700 border border-green-900'
                                : 'bg-red-900/20 text-red-400 border border-red-800'
                        }`}>
                            {isConnected ? 'Connected to AI Agent' : 'Disconnected - Attempting to reconnect...'}
                        </div>

                        <div className="flex items-center space-x-2">
                            <label className="text-sm text-zinc-400">Mock Mode:</label>
                            <button
                                onClick={() => setUseMockResponse(!useMockResponse)}
                                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                                    useMockResponse
                                        ? 'bg-blue-900/0 text-blue-300 border border-blue-800'
                                        : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
                                }`}
                            >
                                {useMockResponse ? 'ON' : 'OFF'}
                            </button>
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="space-y-4">
                        {messages.map((message, index) => (
                            <div key={index} className={`flex ${message.type === 'User' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
                                    message.type === 'User' ? 'bg-zinc-800 text-white text-xl':  message.type === 'error' ? 'bg-transparent text-white' : message.type === 'Agent' ? 'bg-transparent text-white' : message.type === 'system' ? 'bg-green-900/20 text-green-400 border border-green-800' : message.type === 'progress' ? 'bg-blue-900/20 text-blue-300 border border-blue-800 animate-pulse' : 'bg-yellow-900/20 text-yellow-400 border border-yellow-800' } `}>
                                    {message.type === 'Agent' && message.reasoning_steps && (
                                        <ReasoningFlowComponent
                                            steps={message.reasoning_steps}
                                            messageIndex={index}
                                            expandedReasoning={expandedReasoning}
                                            toggleReasoningExpansion={toggleReasoningExpansion}
                                        />
                                    )}
                                    <div className="text-sm">
                                        {message.type === 'progress' && (
                                            <div className="flex items-center space-x-2 mb-1">
                                                <span className="text-xs text-blue-400 uppercase tracking-wide">
                                                    {message.progress_type || 'Processing'}
                                                </span>
                                            </div>
                                        )}
                                        <div className="whitespace-pre-wrap text-[1rem]">{message.content}</div>
                                    </div>
                                    
                                </div>
                            </div>
                        ))}

                        {/* Typing indicator */}
                        {isTyping && (
                            <div className="flex justify-start">
                                <div className=" text-white border border-zinc-700 rounded-lg p-3 max-w-[80%]">
                                    <div className="flex items-center space-x-3">
                                        <span className="text-xs text-gray-400">Agent is thinking...</span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                </div>
                
                <div className="p-4 w-full lg:w-[85%] mx-auto">
                    <div className="flex items-end gap-2 bg-zinc-900 rounded-xl p-3 border border-zinc-600">
                        <div className="flex-1">
                            <textarea
                                ref={textareaRef}
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Ask about transactions, fraud detection, or analytics..."
                                disabled={!isConnected}
                                className="w-full bg-transparent text-white placeholder-gray-400 resize-none outline-none border-none text-sm leading-relaxed min-h-[20px] max-h-32 disabled:opacity-50"
                                rows={1}
                                onInput={(e) => {
                                    const target = e.target as HTMLTextAreaElement;
                                    target.style.height = 'auto';
                                    target.style.height = target.scrollHeight + 'px';
                                }}
                            />
                        </div>
                        <button
                            onClick={sendMessage}
                            disabled={!isConnected || !inputMessage.trim()}
                            className="flex-shrink-0 w-8 h-8 bg-zinc-800 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
            <div className="flex h-full flex-1 text-white justify-center items-center border-[1px] rounded-xl bg-[#0F0F11] border-zinc-700 min-h-screen max-h-[fit]">
                Chat History
            </div>
        </div>
    )
}