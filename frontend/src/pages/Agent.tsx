
import { useState, useRef, useEffect } from 'react';

interface Message {
    type: 'system' | 'user' | 'agent' | 'typing';
    content: string;
    timestamp: string;
}

export default function AgentPage(){
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isConnected, setIsConnected] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        // Connect to WebSocket
        const connectWebSocket = () => {
            const ws = new WebSocket('ws://localhost:80/chat/ws/agent/0');

            ws.onopen = () => {
                console.log('Connected to agent WebSocket');
                setIsConnected(true);
            };

            ws.onmessage = (event) => {
                const message: Message = JSON.parse(event.data);

                if (message.type === 'typing') {
                    setIsTyping(true);
                    return;
                }

                setIsTyping(false);
                setMessages(prev => [...prev, message]);
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

        connectWebSocket();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    const sendMessage = () => {
        if (!inputMessage.trim() || !wsRef.current || !isConnected) return;

        const messageData = {
            content: inputMessage.trim()
        };

        wsRef.current.send(JSON.stringify(messageData));
        setInputMessage('');

        // Reset textarea height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const formatTimestamp = (timestamp: string) => {
        return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="flex w-full min-h-screen max-h-[fit] gap-x-2">
            <div className="flex flex-col h-full w-[80%] text-white border-[1px] rounded-xl bg-[#0F0F11] border-zinc-700 min-h-screen max-h-[fit]">

                <div className="flex-1 p-4 overflow-y-auto">
                    {/* Connection status */}
                    <div className={`text-center text-sm mb-4 px-3 py-2 rounded-lg ${
                        isConnected
                            ? 'bg-green-900/20 text-green-400 border border-green-800'
                            : 'bg-red-900/20 text-red-400 border border-red-800'
                    }`}>
                        {isConnected ? '🟢 Connected to AI Agent' : '🔴 Disconnected - Attempting to reconnect...'}
                    </div>

                    {/* Messages */}
                    <div className="space-y-4">
                        {messages.length === 0 ? (
                            <div className="text-gray-400 text-center">
                                Start a conversation with the AI Agent! Ask about transactions, fraud detection, or analytics.
                            </div>
                        ) : (
                            messages.map((message, index) => (
                                <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[80%] rounded-lg p-3 ${
                                        message.type === 'user'
                                            ? 'bg-blue-600 text-white'
                                            : message.type === 'agent'
                                            ? 'bg-zinc-800 text-white border border-zinc-700'
                                            : message.type === 'system'
                                            ? 'bg-green-900/20 text-green-400 border border-green-800'
                                            : 'bg-yellow-900/20 text-yellow-400 border border-yellow-800'
                                    }`}>
                                        <div className="text-sm">
                                            {message.type === 'agent' && (
                                                <div className="text-xs text-gray-400 mb-1">🤖 AI Agent</div>
                                            )}
                                            {message.type === 'user' && (
                                                <div className="text-xs text-blue-200 mb-1">You</div>
                                            )}
                                            <div className="whitespace-pre-wrap">{message.content}</div>
                                            <div className="text-xs text-gray-400 mt-1">{formatTimestamp(message.timestamp)}</div>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}

                        {/* Typing indicator */}
                        {isTyping && (
                            <div className="flex justify-start">
                                <div className="bg-zinc-800 text-white border border-zinc-700 rounded-lg p-3 max-w-[80%]">
                                    <div className="text-xs text-gray-400 mb-1">🤖 AI Agent</div>
                                    <div className="flex items-center space-x-1">
                                        <div className="flex space-x-1">
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                                        </div>
                                        <span className="text-sm text-gray-400 ml-2">Agent is thinking...</span>
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
                                placeholder={isConnected ? "Ask about transactions, fraud detection, or analytics..." : "Connecting..."}
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