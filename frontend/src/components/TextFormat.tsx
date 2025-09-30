export const formatMessageContent = (content: string): React.ReactElement => {
    // Check if content contains table patterns (lines with | characters)
    const lines = content.split('\n');
    const hasTable = lines.some(line =>
        line.includes('|') && line.split('|').length > 2
    );

    if (hasTable) {
        // Find table sections and format them separately
        const sections: React.ReactElement[] = [];
        let currentSection = '';
        let inTable = false;
        let sectionIndex = 0;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const isTableLine = line.includes('|') && line.split('|').length > 2;

            if (isTableLine && !inTable) {
                // Starting a table - save previous section
                if (currentSection.trim()) {
                    sections.push(
                        <span key={`text-${sectionIndex++}`}>
                            {formatTextContent(currentSection)}
                        </span>
                    );
                }
                currentSection = line + '\n';
                inTable = true;
            } else if (isTableLine && inTable) {
                // Continue table
                currentSection += line + '\n';
            } else if (!isTableLine && inTable) {
                // End of table
                sections.push(
                    <div key={`table-${sectionIndex++}`} className="table-content">
                        {currentSection.trim()}
                    </div>
                );
                currentSection = line + '\n';
                inTable = false;
            } else {
                // Regular content
                currentSection += line + '\n';
            }
        }

        // Handle remaining content
        if (currentSection.trim()) {
            if (inTable) {
                sections.push(
                    <div key={`table-${sectionIndex}`} className="table-content">
                        {currentSection.trim()}
                    </div>
                );
            } else {
                sections.push(
                    <span key={`text-${sectionIndex}`}>
                        {formatTextContent(currentSection)}
                    </span>
                );
            }
        }

        return <>{sections}</>;
    }

    // No tables, use regular formatting
    return <>{formatTextContent(content)}</>;
};
export const formatTextContent = (content: string): React.ReactElement => {
    // Split content by **text** patterns to handle bold formatting
    const parts = content.split(/(\*\*.*?\*\*)/g);
    return (
        <>
            {parts.map((part, index) => {
                // Check if this part is bold (wrapped in **)
                if (part.startsWith('**') && part.endsWith('**')) {
                    const boldText = part.slice(2, -2); // Remove the ** from both ends
                    return <span key={index} className="font-bold">{boldText}</span>;
                }
                // Regular text - preserve line breaks
                return <span key={index}>{part}</span>;
            })}
        </>
    );
};