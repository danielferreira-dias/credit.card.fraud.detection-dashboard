import ContentLoader from "react-content-loader"

const CardLoader = (props: any) => (
    <div className="bg-zinc-950 border border-zinc-700 rounded-lg px-4 py-2 shadow-[0_0_8px_rgba(0,0,0,0.5)]">
        <ContentLoader speed={2} width="100%" height={120} backgroundColor="#27272a" foregroundColor="#3f3f46" {...props}>
            {/* Header - Merchant name */}
            <rect x="0" y="10" rx="3" ry="3" width="150" height="28" />
            <rect x="0" y="45" rx="3" ry="3" width="60" height="10" />
            {/* Transaction details grid - 8 columns */}
            <rect x="0" y="80" rx="2" ry="2" width="1500" height="20" />
        </ContentLoader>
    </div>
)

export default CardLoader

