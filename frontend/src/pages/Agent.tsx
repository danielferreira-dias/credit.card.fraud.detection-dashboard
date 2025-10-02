
import { useState, useRef, useEffect } from 'react';
import { ReasoningFlowComponent } from '../components/ReasoningFlowComponent';
// import { mockStepsTest, simulateMockAgentResponse } from '../mock/mockSteps';
import { useUser } from '../context/UserContext';
import { useNotification } from '../hooks/useNotification';
import { formatMessageContent } from '../components/TextFormat';
import ChatHistory from '../components/ChatHistory';

interface ReasoningStep {
    type: 'thinking' | 'tool_call' | 'tool_result' | 'tool_progress' | 'final_response' | 'agent_thinking';
    content: string;
    toolName?: string;
    tool_name?: string;
    tool_args?: any;
    timestamp: string;
}
interface Message {
    type: 'system' | 'User' | 'Agent' | 'typing' | 'progress' | 'error' | 'conversation_started';
    content: string;
    timestamp: string;
    progress_type?: string;
    reasoning_steps?: ReasoningStep[];
}

export default function AgentPage(){
    const { user, loading } = useUser();
    const { showSuccess, showError, showWarning, showInfo, showAgentNotification, showAuthSuccess } = useNotification();
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isConnected, setIsConnected] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [currentReasoningSteps, setCurrentReasoningSteps] = useState<ReasoningStep[]>([]);
    const [expandedReasoning, setExpandedReasoning] = useState<{[key: number]: boolean}>({});
    const [typingMessageIndex, setTypingMessageIndex] = useState<number | null>(null);
    const [displayedContent, setDisplayedContent] = useState<{[key: number]: string}>({});
    const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
    const [currentThreadID, setcurrentThreadID] = useState<string | null>(null);
    const [chatHistoryRefresh, setChatHistoryRefresh] = useState<number>(0);
    const wsRef = useRef<WebSocket | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const reasoningStepsRef = useRef<ReasoningStep[]>([]);
    const intentionalCloseRef = useRef<boolean>(false);
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };
    useEffect(() => {
        scrollToBottom();
    }, [messages, displayedContent]);
    
    // Load conversation history when a conversation is selected
    useEffect(() => {
        if (loading || !user || !currentConversationId) {
            return;
        }

        const token = localStorage.getItem('access_token');
        if (!token) {
            console.error('No access token found');
            return;
        }

        const fetchConversationHistory = async () => {
            try {
                const url = `http://localhost:80/chat/${user.id}/${currentConversationId}`;
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    throw new Error(`Failed to fetch conversation: ${response.status}`);
                }

                const conversationMessages = await response.json();
                console.log('Loaded conversation history:', conversationMessages);

                // Transform backend messages to frontend Message format
                const formattedMessages = conversationMessages.map((msg: any) => ({
                    type: msg.role === 'user' ? 'User' : 'Agent',
                    content: msg.content,
                    timestamp: msg.created_at,
                    reasoning_steps: msg.reasoning_steps
                }));
                console.log('conversationMessages ', conversationMessages)


                setMessages(formattedMessages);
            } catch (error) {
                console.error('Error fetching conversation history:', error);
                showError('Failed to load conversation history', 3000);
            }
        };

        fetchConversationHistory();
    }, [currentConversationId, user, loading])

    // Websocket Managment
    useEffect(() => {
        // Don't connect if user is not loaded or authenticated
        if (loading || !user) {
            console.log('WebSocket: Waiting for user to load...');
            return;
        }

        // Prevent multiple connections
        if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
            console.log('WebSocket: Already connected or connecting, skipping...');
            return;
        }

        const connectWebSocket = () => {
            const token = localStorage.getItem('access_token');
            if (!token) {
                console.error('No access token found');
                return;
            }

            // Reset intentional close flag when connecting
            intentionalCloseRef.current = false;

            // Build WebSocket URL without conversation_id (we'll send it in messages)
            const wsUrl = `ws://localhost:80/chat/ws/agent/${user.id}?token=${encodeURIComponent(token)}`;
            const ws = new WebSocket(wsUrl);
            ws.onopen = () => {
                console.log('Connected to agent WebSocket');
                setIsConnected(true);
                // showSuccess('Connected to AI Agent successfully!', 3000);
            };
            ws.onmessage = (event) => {
                const message: Message = JSON.parse(event.data);
                console.log("WebSocket message received:", message);

                // Handle conversation_started - update conversation ID and thread ID
                if (message.type === 'conversation_started') {
                    const convData = message as any;
                    setCurrentConversationId(convData.conversation_id);
                    setcurrentThreadID(convData.thread_id);
                    setChatHistoryRefresh(prev => prev + 1);
                    return;
                }

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
                        type: message.progress_type === 'tool_call' ? 'tool_call' :
                              message.progress_type === 'tool_progress' ? 'tool_progress' :
                              message.progress_type === 'tool_result' ? 'tool_result' :
                              message.progress_type === 'agent_thinking' ? 'agent_thinking' :
                              message.progress_type === 'final_response' ? 'final_response' : 'thinking',
                        content: message.content.replace(/\\n/g, '\n'),
                        tool_name: (message as any).tool_name,
                        tool_args: (message as any).tool_args,
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
                setMessages(prev => {
                    // Remove progress messages when final message arrives
                    const withoutProgress = prev.filter(m => m.type !== 'progress');
                    const updated = [...withoutProgress, processedMessage];
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
            };
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                setIsConnected(false);
                // showError('WebSocket connection error occurred', 5000);
            };
            wsRef.current = ws;
        };
        // Calls Websocket function
        connectWebSocket();
        return () => {
            if (wsRef.current) {
                intentionalCloseRef.current = true;
                wsRef.current.close();
            }
        };
    }, [user]);
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

        if (!wsRef.current || !isConnected) return;
        const messageData = {
            content: userMessage,
            conversation_id: currentConversationId,
            thread_id: currentThreadID
        };
        wsRef.current.send(JSON.stringify(messageData));
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

    const handleSelectChat = (conversationId: number, threadID: string) => {
        // Clear current messages and set new conversation
        setMessages([]);
        setCurrentConversationId(conversationId);
        setcurrentThreadID(threadID);

        // Don't close WebSocket - just update the conversation context
        // The next message sent will use the updated conversationId
    };

    const handleDeleteConversation = async () => {
        if (!currentConversationId || !user) return;

        const token = localStorage.getItem('access_token');
        if (!token) {
            showError('No access token found', 3000);
            return;
        }

        try {
            const response = await fetch(`http://localhost:80/chat/${user.id}/${currentConversationId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to delete conversation: ${response.status}`);
            }

            // Clear current conversation
            setMessages([]);
            setCurrentConversationId(null);
            setcurrentThreadID(null);
            setChatHistoryRefresh(prev => prev + 1);
            showSuccess('Conversation deleted successfully', 3000);
        } catch (error) {
            console.error('Error deleting conversation:', error);
            showError('Failed to delete conversation', 3000);
        }
    };

    const handleNewConversation = () => {
        // Clear current conversation state to start fresh
        setMessages([]);
        setCurrentConversationId(null);
        setcurrentThreadID(null);
        showInfo('Starting new conversation', 2000);
    };
    return (
        <div className="flex w-full min-h-screen max-h-[fit] gap-x-2">
            <div className="flex flex-col h-full w-[80%] text-white border-[1px] rounded-xl bg-[#0F0F11] border-zinc-700 min-h-screen max-h-[fit]">

                <div className="flex-1 p-4 overflow-y-auto">
                    {/* Connection status and mock toggle */}
                    <div className="flex items-center justify-between mb-4">
                        <div className={`text-xs px-3 py-2 rounded-lg w-fit ${
                            isConnected
                                ? 'bg-black text-green-700 border border-green-900'
                                : 'bg-black text-red-400 border border-red-800'
                        }`}>
                            {isConnected ? 'Connected to AI Agent' : 'Disconnected - Attempting to reconnect...'}
                        </div>
                        <div className='flex flex-row gap-x-2'>
                            <div className={`text-xs px-3 py-2 rounded-lg w-fit bg-black text-zinc-500 border border-zinc-500`}>
                                {currentConversationId ? `ID: ${currentConversationId}` : "New Conversation"}
                            </div>
                            <div className={`text-xs px-3 py-2 rounded-lg w-fit bg-black text-zinc-500 border border-zinc-500`}>
                                {currentThreadID ? `Thread ID: ${currentThreadID}` : "No Thread ID"}
                            </div>
                            {currentConversationId && (
                                <>
                                    <button
                                        onClick={handleNewConversation}
                                        className="text-xs px-3 py-2 rounded-lg bg-zinc-950 text-blue-400 border border-blue-800 hover:bg-blue-900/30 transition-colors"
                                    >
                                        New Conversation
                                    </button>
                                    <button
                                        onClick={handleDeleteConversation}
                                        className="text-xs px-3 py-2 rounded-lg bg-zinc-950 text-red-400 border border-red-800 hover:bg-red-900/30 transition-colors"
                                    >
                                        Delete Conversation
                                    </button>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="space-y-4">
                        {messages.map((message, index) => (
                            <div key={index} className={`flex ${message.type === 'User' ? 'justify-end' : 'justify-start'}`}>
                                <div className={` rounded-lg px-4 py-3 ${
                                    message.type === 'User' ? 'bg-zinc-800 text-white text-xl' :
                                    message.type === 'error' ? 'border-zinc-900 border-2 text-white w-[80%]' :
                                    message.type === 'Agent' ? 'bg-transparent text-white w-[80%]' :
                                    message.type === 'system' ? 'bg-green-900/20 text-green-400 border border-green-800 w-[80%]' :
                                    message.type === 'progress' ? 'text-zinc-300 border border-zinc-700 animate-pulse w-[80%]' :
                                    message.type === 'conversation_started' ? 'text-zinc-300 border border-zinc-700' :
                                    'bg-yellow-900/20 text-yellow-400 border border-yellow-800'
                                }`}>
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
                                                <span className="text-xs text-zinc-400 uppercase tracking-wide">
                                                    {message.progress_type || 'Processing'}
                                                </span>
                                            </div>
                                        )}
                                        <div className="whitespace-pre-wrap text-[1rem] ">
                                            {message.type === 'Agent' ?
                                                formatMessageContent(
                                                    typingMessageIndex === index
                                                        ? displayedContent[index] || ''
                                                        : displayedContent[index] || message.content
                                                ) :
                                                message.content
                                            }
                                            {typingMessageIndex === index && (
                                                <span className="animate-pulse text-zinc-400">|</span>
                                            )}
                                        </div>
                                    </div>
                                    
                                </div>
                            </div>
                        ))}
                        {/* Typing indicator */}
                        {isTyping && (
                            <div className="flex justify-start">
                                <div className=" text-white border border-zinc-700 rounded-lg p-3 max-w-[80%]">
                                    <div className="flex items-center space-x-3">
                                        <span className="special-affect">Agent is thinking...</span>
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
                                disabled={!isConnected || isTyping || typingMessageIndex !== null}
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
                            disabled={!isConnected || isTyping || typingMessageIndex !== null || !inputMessage.trim()}
                            className="flex-shrink-0 w-8 h-8 bg-zinc-800 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
            <ChatHistory onSelectChat={handleSelectChat} refreshTrigger={chatHistoryRefresh} />
        </div>
    )
}