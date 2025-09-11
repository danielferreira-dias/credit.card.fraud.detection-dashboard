export default function StatsCard( { typeStat, statValue } : { typeStat : string, statValue : number } )  {
    return (
        <div className="flex flex-row bg-[#0F0F11] w-[100%] h-40 rounded-2xl justify-center items-center">
            {typeStat}, {statValue}
        </div>
    )
}