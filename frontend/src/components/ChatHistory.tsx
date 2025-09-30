import { useEffect, useState } from "react"
import { useUser } from "../context/UserContext"

interface chatHistory{
    id: number,
    title: string,
}

interface ChatHistoryProps {
    onSelectChat: (conversationId: number) => void;
}

export default function ChatHistory({ onSelectChat }: ChatHistoryProps){
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
    }, [user]); // Add user as dependency

    return (
        <div className="flex flex-1 flex-col sticky top-0 text-white gap-y-2 p-2 justify-start items-center border-[1px] rounded-xl bg-[#0F0F11] border-zinc-700 h-svh">
            {historyList.map((chat) => (
                <button
                    key={chat.id}
                    onClick={() => onSelectChat(chat.id)}
                    className="w-full h-12 bg-zinc-950 border-[1px] hover:bg-zinc-800 border-zinc-700 rounded-lg justify-center items-center flex flex-col">
                    <div>{chat.id}. {chat.title}</div>
                </button>
            ))}
        </div>
    )
}