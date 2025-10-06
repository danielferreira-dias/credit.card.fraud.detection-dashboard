interface StatsCardProps {
    typeStat: string;
    statValue: number;
    colour: string;
  }

export default function StatsCard( { typeStat, statValue , colour } : StatsCardProps  )  {
    const formatValue = (value: number) => {
        if (value === undefined || value === null) return "0";

        // For percentage values (fraud detection percentage)
        if (typeStat.toLowerCase().includes("percentage")) {
            return `${value.toFixed(2)}%`;
        }

        // For transaction counts (no decimal places needed)
        if (typeStat.toLowerCase().includes("transactions")) {
            return value.toLocaleString('en-US');
        }

        // Default formatting with currency
        return `${value.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
    };

    return (
        <div className={`flex flex-col justify-evenly ${colour} w-[90%] h-30 rounded-2xl opacity-80 items-center p-2`} style={{ boxShadow: 'var(--shadow-l)' }}>
            <div className={`flex flex-row justify-evenly w-full items-center`}>
                <span className="opacity-100 text-[1.0rem]">{typeStat}</span>
                {/* <img src={"/left-arrow-backup-2-svgrepo-com.svg"} alt="Toggle sidebar" className={`w-5 h-5 transform transition duration-300 }`} /> */}
            </div>
            <span className="text-2xl font-bold">{formatValue(statValue)}</span>
        </div>
    )
}


export function StatsCardDashboard( { typeStat, statValue , colour } : StatsCardProps  )  {
    const formatValue = (value: number) => {
        if (value === undefined || value === null) return "0";

        // For percentage values (fraud detection percentage)
        if (typeStat.toLowerCase().includes("percentage")) {
            return `${value.toFixed(2)}%`;
        }

        // For transaction counts (no decimal places needed)
        if (typeStat.toLowerCase().includes("transactions")) {
            return value.toLocaleString('en-US');
        }

        // Default formatting with currency
        return `${value.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
    };

    return (
        <div className={`flex flex-col justify-evenly ${colour} w-50 h-20 rounded-2xl opacity-80 items-center p-2`} style={{ boxShadow: 'var(--shadow-l)' }}>
            <div className={`flex flex-row justify-evenly w-full items-center`}>
                <span className="opacity-100 text-[1.0rem]">{typeStat}</span>
                {/* <img src={"/left-arrow-backup-2-svgrepo-com.svg"} alt="Toggle sidebar" className={`w-5 h-5 transform transition duration-300 }`} /> */}
            </div>
            <span className="text-2xl font-bold">{formatValue(statValue)}</span>
        </div>
    )
}