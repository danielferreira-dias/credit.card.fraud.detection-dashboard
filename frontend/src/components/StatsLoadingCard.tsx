import ContentLoader from "react-content-loader"

interface StatsLoadingCardProps {
    colour?: string;
}

const StatsLoadingCard = ({ colour = "bg-zinc-800" }: StatsLoadingCardProps) => (
    <div className={`flex flex-col justify-center items-center ${colour} w-[95%] h-30 rounded-2xl opacity-80 items-center p-2`}>
        <ContentLoader speed={2} width="100%" height={120} backgroundColor="#27272a" foregroundColor="#3f3f46">
            {/* Stat type text placeholder */}
            <rect x="10" y="15" rx="3" ry="3" width="140" height="16" />

            {/* Stat value placeholder */}
            <rect x="30" y="50" rx="4" ry="4" width="100" height="32" />
        </ContentLoader>
    </div>
)

export default StatsLoadingCard