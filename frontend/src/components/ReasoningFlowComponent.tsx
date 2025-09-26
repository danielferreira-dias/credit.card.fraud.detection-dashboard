import React from 'react';

interface ReasoningStep {
    type: 'thinking' | 'tool_call' | 'tool_result' | 'tool_progress' | 'final_response';
    content: string;
    toolName?: string;
    timestamp: string;
}

interface ReasoningFlowComponentProps {
    steps: ReasoningStep[];
    messageIndex: number;
    expandedReasoning: {[key: number]: boolean};
    toggleReasoningExpansion: (messageIndex: number) => void;
}

export const ReasoningFlowComponent: React.FC<ReasoningFlowComponentProps> = ({
    steps,
    messageIndex,
    expandedReasoning,
    toggleReasoningExpansion
}) => {
    const isExpanded = expandedReasoning[messageIndex];

    return (
        <div className="my-3 border-y border-zinc-700 py-3 w-full min-w-full">
            <button onClick={() => toggleReasoningExpansion(messageIndex)} className="flex items-center space-x-2 text-sm text-zinc-400 hover:text-zinc-300 transition-colors">
                <svg className={`w-4 h-4 transform transition-transform ${isExpanded ? 'rotate-89' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                <span>View Agent Reasoning ({steps.length} steps)</span>
            </button>

            {isExpanded && (
                <div className="mt-3 space-y-2 bg-zinc-900/50 rounded-lg p-3 border border-zinc-700 w-full">
                    {steps.map((step, index) => (
                        <div key={index} className="flex items-start space-x-3 py-4 px-2 border-y-[1px] border-zinc-800">
                            <div className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold bg-zinc-800 text-zinc-300">
                                {index + 1}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center space-x-2 mb-1">
                                    <span className={`text-xs px-2 py-1 rounded font-medium ${
                                        step.type === 'thinking' ? 'bg-blue-900/30 text-blue-300' :
                                        step.type === 'tool_call' ? 'bg-green-900/30 text-green-300' :
                                        step.type === 'tool_progress' ? 'bg-purple-900/30 text-purple-300' :
                                        'bg-yellow-900/30 text-yellow-300'
                                    }`}>
                                        {step.type === 'thinking' ? 'THINKING' :
                                         step.type === 'tool_call' ? `TOOL: ${step.toolName || 'Unknown'}` :
                                         step.type === 'tool_progress' ? 'PROGRESS' :
                                         step.type === 'tool_result' ? 'RESULT' :
                                         'RESPONSE'}
                                    </span>
                                    <span className="text-xs text-zinc-500">
                                        {new Date(step.timestamp).toLocaleTimeString()}
                                    </span>
                                </div>
                                <div className="text-sm text-zinc-300 whitespace-pre-wrap">
                                    {step.content}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};