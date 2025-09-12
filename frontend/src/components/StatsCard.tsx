interface StatsCardProps {
    typeStat: string;
    statValue: number;
    colour: string;
  }

export default function StatsCard( { typeStat, statValue , colour } : StatsCardProps  )  {
    const formattedValue = `${statValue.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} $`;
    return (
        <div className={`flex flex-col justify-evenly ${colour} w-[95%] h-40 rounded-2xl opacity-80 items-center p-2 `}>
            <div className={`flex flex-row justify-evenly w-full items-center`}>
                <span className="opacity-100 text-[0.90rem]">{typeStat}</span>
                <img src={"/left-arrow-backup-2-svgrepo-com.svg"} alt="Toggle sidebar" className={`w-5 h-5 transform transition duration-300 }`} />
            </div>
            <span className="text-2xl font-semibold">{formattedValue}</span>
        </div>
    )
}