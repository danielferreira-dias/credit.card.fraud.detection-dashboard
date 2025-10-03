import { useEffect, useState } from "react"
import { useUser } from "../context/UserContext"

interface chatHistory{
    id: number,
    title: string,
    thread_id: string
}

interface ChatHistoryProps {
    onSelectChat: (conversationId: number, threadID: string) => void;
    refreshTrigger?: number;
}

export default function ChatHistory({ onSelectChat, refreshTrigger }: ChatHistoryProps){
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
            setHistoryList(data)
            console.log('Chat history:', data);
        };

        fetchData().catch(error => {
            console.error('Failed to fetch chat history:', error);
        });
    }, [user, refreshTrigger]); // Add refreshTrigger to dependencies

    return (
        <div className="flex flex-1 flex-col sticky top-0 text-white gap-y-2 p-2 justify-start items-center rounded-xl bg-[#0F0F11] h-svh" style={{ boxShadow: 'var(--shadow-l)' }}>
            {historyList.map((chat) => (
                <button
                    key={chat.id}
                    onClick={() => onSelectChat(chat.id, chat.thread_id)}
                    className="w-full h-12 text-sm border-b-[1px] border-zinc-800 hover:bg-zinc-800  rounded-lg justify-center items-center flex flex-col">
                    <div>{chat.title}</div>
                </button>
            ))}
        </div>
    )
}