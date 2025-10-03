import { useEffect, useState } from "react"
import { useUser } from "../context/UserContext"

interface chatHistory{
    id: number,
    title: string,
    thread_id: string,
    updated_at: string
}

interface ChatHistoryProps {
    onSelectChat: (conversationId: number, threadID: string) => void;
    refreshTrigger?: number;
    currentConversationId?: number | null;
}

export default function ChatHistory({ onSelectChat, refreshTrigger, currentConversationId }: ChatHistoryProps){
    const { user } = useUser();
    const [historyList, setHistoryList] = useState<chatHistory[]>([]);

    useEffect(() => {
        if (!user) return; // Don't fetch if user is not loaded

        const fetchData = async () => {
            const token = localStorage.getItem('access_token');
            if (!token) {
                console.error('No access token found');
                return;
            }
            console.log('Token -> ', token)

            const url = `http://localhost:80/chat/${user.id}`;
            const res = await fetch(url, {
                method: "GET",
                headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
                },
            });

            if (!res.ok) {
                throw new Error("Error in request: " + res.status);
            }
            const data = await res.json();
            console.log('Chat history:', data);
            setHistoryList(data);
        };

        fetchData().catch(error => {
            console.error('Failed to fetch chat history:', error);
        });
    }, [user, refreshTrigger]); // Add refreshTrigger to dependencies

    // Sort conversations by updated_at whenever historyList changes
    const sortedHistoryList = [...historyList].sort((a: chatHistory, b: chatHistory) =>
        new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );

    return (
        <div className="flex flex-1 flex-col sticky top-0 text-white gap-y-2 p-2 justify-start items-center rounded-xl bg-zinc-950 h-svh" style={{
                border: 'double 1px transparent',
                borderRadius: '0.75rem',
                backgroundImage: `
                    linear-gradient(#0a0a0a, #0a0a0a),
                    linear-gradient(135deg, rgba(75, 75, 75, 1) 0%, rgba(10, 10, 10, 1) 25%, rgba(10, 10, 10, 1) 85%, rgba(75, 75, 75, 1) 100%),
                    linear-gradient(225deg, rgba(75, 75, 75, 1) 0%, rgba(10, 10, 10, 1) 15%, rgba(10, 10, 10, 1) 85%, rgba(75, 75, 75, 1) 100%)
                `,
                backgroundOrigin: 'border-box',
                backgroundClip: 'padding-box, border-box, border-box'
            }}>
            {sortedHistoryList.map((chat) => (
                <button
                    key={chat.id}
                    onClick={() => onSelectChat(chat.id, chat.thread_id)}
                    className={`w-full h-12 text-xs border-zinc-800 hover:bg-zinc-800 rounded-lg justify-center items-center flex flex-col ${
                        currentConversationId === chat.id ? 'bg-zinc-800' : ''
                    }`}
                    style={{ boxShadow: 'var(--shadow-s)' }}
                >
                    <div>{chat.title}</div>
                </button>
            ))}
        </div>
    )
}