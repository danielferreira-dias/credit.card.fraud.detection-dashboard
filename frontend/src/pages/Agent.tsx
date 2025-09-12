export default function AgentPage(){
    return (
        <div className="flex w-full min-h-screen max-h-[fit] gap-x-2">
            <div className="flex flex-col h-full w-[80%] text-white border-[1px] rounded-xl bg-[#0F0F11] border-zinc-700 min-h-screen max-h-[fit]">

                <div className="flex-1 p-4 overflow-y-auto">
                    <div className="text-gray-400 text-center">Chat messages will appear here</div>
                </div>
                
                <div className="p-4 w-full lg:w-[85%] mx-auto">
                    <div className="flex items-end gap-2 bg-zinc-900 rounded-xl p-3 border border-zinc-600">
                        <div className="flex-1">
                            <textarea
                                placeholder="Ask a Question"
                                className="w-full bg-transparent text-white placeholder-gray-400 resize-none outline-none border-none text-sm leading-relaxed min-h-[20px] max-h-32"
                                rows={1}
                                onInput={(e) => {
                                    const target = e.target as HTMLTextAreaElement;
                                    target.style.height = 'auto';
                                    target.style.height = target.scrollHeight + 'px';
                                }}
                            />
                        </div>
                        <button className="flex-shrink-0 w-8 h-8 bg-zinc-800  rounded-full flex items-center justify-center transition-all duration-200 hover:scale-105">
                            <img src="/public/arrow-up-svgrepo-com.svg" className="w-5 h-5"></img>
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