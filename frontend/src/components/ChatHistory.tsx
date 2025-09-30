import { useEffect } from "react"
import { useUser } from "../context/UserContext"

export default function ChatHistory(){
    const { user } = useUser();

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
        };

        fetchData().catch(error => {
            console.error('Failed to fetch chat history:', error);
        });
    }, [user]); // Add user as dependency

    return (
        <div className="flex flex-1 sticky top-0 text-white justify-center items-center border-[1px] rounded-xl bg-[#0F0F11] border-zinc-700 h-svh">
            Chat History
        </div>
    )
}