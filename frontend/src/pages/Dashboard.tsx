import { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, LabelList, RadialBar, RadialBarChart, BarChart, Bar, PolarRadiusAxis, Label, PieChart, Pie } from "recharts"
import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { type ChartConfig, ChartContainer } from "@/components/ui/chart"
import { ChartLegend, ChartLegendContent } from "@/components/ui/chart"
import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card"
import StatsCard, { StatsCardDashboard } from "@/components/StatsCard"
import { PanelLeft, PanelRight } from "lucide-react"
import { useNavbar } from "@/context/NavbarContext"
import { useUser } from "@/context/UserContext"
import { useNotification } from "@/hooks/useNotification"


interface StatsResponse {
    countries: Record<string, { total_transactions: number; fraud_transactions: number }>;
    merchant_category: Record<string, { total_transactions: number; fraud_transactions: number }>;
    device: Record<string, { total_transactions: number; fraud_transactions: number }>;
    channel: Record<string, { total_transactions: number; fraud_transactions: number }>;
    high_risk_merchant: Record<string, { total_transactions: number; fraud_transactions: number }>;
    distance_from_home: Record<string, { total_transactions: number; fraud_transactions: number }>;
    card_present: Record<string, { total_transactions: number; fraud_transactions: number }>;
    weekend_transaction: Record<string, { total_transactions: number; fraud_transactions: number }>;
    hourly_stats: Array<{
        hour: number;
        total_transactions: number;
        fraud_transactions: number;
    }>;
}

// Skeleton Loader Components
const BarChartSkeleton = ({ height = 300 }: { height?: number }) => (
    <div className="w-full animate-pulse" style={{ height: `${height}px` }}>
        <div className="flex flex-col h-full justify-end items-center gap-2 px-8 pb-8">
            <div className="flex w-full items-end justify-around h-full gap-3">
                <div className="bg-zinc-800 rounded-t w-full" style={{ height: '60%' }}></div>
                <div className="bg-zinc-800 rounded-t w-full" style={{ height: '85%' }}></div>
                <div className="bg-zinc-800 rounded-t w-full" style={{ height: '45%' }}></div>
                <div className="bg-zinc-800 rounded-t w-full" style={{ height: '72%' }}></div>
                <div className="bg-zinc-800 rounded-t w-full" style={{ height: '55%' }}></div>
                <div className="bg-zinc-800 rounded-t w-full" style={{ height: '68%' }}></div>
            </div>
            <div className="flex gap-4 w-full justify-center mt-4">
                <div className="h-2 w-20 bg-zinc-800 rounded"></div>
                <div className="h-2 w-20 bg-zinc-800 rounded"></div>
            </div>
        </div>
    </div>
)

const PieChartSkeleton = () => (
    <div className="w-full h-[250px] animate-pulse flex items-center justify-center">
        <div className="relative">
            <div className="w-40 h-40 rounded-full border-0" style={{ boxShadow: 'var(--shadow-s)'}}></div>
            <div className="w-40 h-40 rounded-full border-zinc-700/50 absolute top-0 left-0"
                 style={{
                     clipPath: 'polygon(50% 50%, 50% 0, 100% 0, 100% 100%, 50% 100%)',
                     transform: 'rotate(45deg)'
                 }}>
            </div>
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-1">
                <div className="h-2 w-12 bg-zinc-800 rounded"></div>
                <div className="h-2 w-8 bg-zinc-800 rounded"></div>
            </div>
        </div>
    </div>
)

const CardSkeleton = ({ isPie = false, className = "" }: { isPie?: boolean; className?: string }) => (
    <Card className={`bg-zinc-950 border-0  style={{ boxShadow: 'var(--shadow-s)'}}${className}`}>
        <CardHeader>
            <div className="h-6 w-48 bg-zinc-800 rounded animate-pulse mb-2"></div>
            <div className="h-4 w-36 bg-zinc-800/70 rounded animate-pulse"></div>
        </CardHeader>
        <CardContent>
            {isPie ? <PieChartSkeleton /> : <BarChartSkeleton />}
        </CardContent>
    </Card>
)

export default function DashboardPage() {
    const { isCollapsed, toggleCollapsed } = useNavbar()
    const [cacheStats, setStats] = useState<StatsResponse | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await fetch('http://localhost:80/stats/overview')
                const data = await response.json()
                console.log('Data to Dashboard -> ', data)
                setStats(data)
            } catch (error) {
                console.error('Failed to fetch statistics:', error)
            } finally {
                setLoading(false)
            }
        }
        fetchStats()
    }, [])

    const chartData = cacheStats?.hourly_stats?.map(item => ({
        hour: `${item.hour}:00`,
        total: item.total_transactions,
        fraud: item.fraud_transactions
    })) || [];

    const chartData_Devices = cacheStats?.device
        ? Object.entries(cacheStats.device).map(([device, data]) => {
            const total = data.total_transactions;
            const fraud = data.fraud_transactions;
            return {
                device,
                total,
                fraud,
            };
            })
        : [];

    const chartData_Channel = cacheStats?.channel
        ? Object.entries(cacheStats.channel).map(([channel, data]) => {
            const total = data.total_transactions;
            const fraud = data.fraud_transactions;
            return {
                channel,
                fraud,
                total,
            };
            })
    : [];

    const chartData_HighRisk_Merchant = cacheStats?.high_risk_merchant
        ? Object.entries(cacheStats.high_risk_merchant).map(([risk_level, data]) => ({
            risk_level: risk_level === "true" ? "High Risk" : "Low Risk",
            transactions: data.total_transactions,
            fraud: data.fraud_transactions,
            fill: risk_level === "true" ? "#ef4444" : "#fafafaff"
        }))
        : [];

    const chartData_Weekend_Transaction = cacheStats?.weekend_transaction
        ? Object.entries(cacheStats.weekend_transaction).map(([weekend_key, data]) => ({
            risk_level: weekend_key === "true" ? "Weekend" : "Weekday",
            transactions: data.total_transactions,
            fraud: data.fraud_transactions,
            fill: weekend_key === "true" ? "#ef4444" : "#fafafaff"
        }))
        : [];

    const chartData_Distance_From_Home = cacheStats?.distance_from_home
        ? Object.entries(cacheStats.distance_from_home).map(([distance_key, data]) => ({
            risk_level: distance_key === "1.0" ? "Away from Home" : "Home",
            transactions: data.total_transactions,
            fraud: data.fraud_transactions,
            fill: distance_key === "1.0" ? "#ef4444" : "#ffffff"
        }))
        : [];

    const chartData_Country = cacheStats?.countries
        ? Object.entries(cacheStats.countries).map(([countries, data]) => ({
            countries: countries,
            total: data.total_transactions,
            fraud: data.fraud_transactions,
        }))
        : [];

    const { user } = useUser();

    const { showSuccess, showError } = useNotification();

    if (loading) {
        return (
        <div className="flex h-full w-full text-white p-4 bg-zinc-950 min-h-screen max-h-[fit] flex-col" style={{
            border: 'double 1px transparent',
            borderRadius: '0.75rem',
            backgroundImage: `
                linear-gradient(#0a0a0a, #0a0a0a),
                linear-gradient(135deg, rgba(75, 75, 75, 1) 0%, rgba(10, 10, 10, 1) 5%, rgba(10, 10, 10, 1) 85%, rgba(75, 75, 75, 1) 100%),
                linear-gradient(225deg, rgba(75, 75, 75, 1) 0%, rgba(10, 10, 10, 1) 15%, rgba(10, 10, 10, 1) 85%, rgba(75, 75, 75, 1) 100%)
            `,
            backgroundOrigin: 'border-box',
            backgroundClip: 'padding-box, border-box, border-box'
        }}>
            <div className="flex flex-col gap-3 mt-4">
                <div className="flex flex-row justify-evenly gap-x-1">
                    <button onClick={toggleCollapsed} className="hover:shadow-2xl hover:shadow-zinc-800  w-8 h-8 bg-zinc-950 shadow-r-lg flex items-center justify-center">
                        {isCollapsed ? <PanelRight color="white" size={18} /> : <PanelLeft color="white" size={18} />}
                    </button>
                    <div className="h-full flex flex-col border-zinc-900 px-4 gap-y-1">
                        <h2 className="text-2xl font-semibold opacity-90">Insight Dashboard Analytics</h2>
                        <h3 className="text-sm opacity-70 mb-6">Real-time fraud detection analytics with AI-powered insights</h3>
                    </div>
                </div>
                
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                <CardSkeleton isPie className="" />
                <CardSkeleton isPie className="" />
                <CardSkeleton isPie className="" />
                <CardSkeleton isPie className="" />
                <CardSkeleton className="md:col-span-2" />
                <CardSkeleton className="md:col-span-2" />
                <CardSkeleton className="" />
                <CardSkeleton className="md:col-span-2" />
            </div>
        </div>
        )
    }

     const stats = [
        { id: 1, typeStat: "Countries", statValue: cacheStats ? Object.keys(cacheStats.countries).length : 0, cardColour: "card-1" },
        { id: 2, typeStat: "Channels", statValue: cacheStats ? Object.keys(cacheStats.channel).length : 0, cardColour: "card-2" },
        { id: 3, typeStat: "Devices", statValue: cacheStats ? Object.keys(cacheStats.device).length : 0, cardColour: "card-3" },
        { id: 4, typeStat: "Merchants Category", statValue: cacheStats ? Object.keys(cacheStats.merchant_category).length : 0, cardColour: "card-4" },
    ];

    const handleButton = async () => {
        try {
            const response = await fetch(`http://localhost:80/users/reports/${user?.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: user?.id,
            }),
            });

            if (!response.ok) {
                showError('There was an error with the Agent Report')
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('✅ Success:', data);
            showSuccess('Report added to your Personal Page')
        } catch (error) {
            console.error('❌ Error:', error);
        }
    }

    return (
        <div className="flex h-full w-full text-white p-4 bg-zinc-950 min-h-screen max-h-[fit] flex-col " style={{
                border: 'double 1px transparent',
                borderRadius: '0.75rem',
                backgroundImage: `
                    linear-gradient(#0a0a0a, #0a0a0a),
                    linear-gradient(135deg, rgba(75, 75, 75, 1) 0%, rgba(10, 10, 10, 1) 5%, rgba(10, 10, 10, 1) 85%, rgba(75, 75, 75, 1) 100%),
                    linear-gradient(225deg, rgba(75, 75, 75, 1) 0%, rgba(10, 10, 10, 1) 15%, rgba(10, 10, 10, 1) 85%, rgba(75, 75, 75, 1) 100%)
                `,
                backgroundOrigin: 'border-box',
                backgroundClip: 'padding-box, border-box, border-box'
            }}>
                <div className="flex flex-row justify-between gap-3 mt-4 items-center">
                    <div className="flex flex-row gap-x-1">
                        <button onClick={toggleCollapsed} className="hover:shadow-2xl hover:shadow-zinc-800  w-8 h-8 bg-zinc-950 shadow-r-lg flex items-center justify-center">
                            {isCollapsed ? <PanelRight color="white" size={18} /> : <PanelLeft color="white" size={18} />}
                        </button>
                        <div className="h-full flex flex-col border-zinc-900 px-4 gap-y-1">
                            <h2 className="text-2xl font-semibold opacity-90">Insight Dashboard Analytics</h2>
                            <h3 className="text-sm opacity-70 mb-6">Real-time fraud detection analytics with AI-powered insights</h3>
                        </div>
                    </div>
                    <button className="w-40 h-10 bg-zinc-950 hover:bg-zinc-900 text-white rounded-lg" onClick={handleButton} style={{ boxShadow: 'var(--shadow-s)'}}>Generate Report</button>
                </div>

                <div className="flex flex-col">
                    <Card className="bg-[#0a0a0a] border-0 w-full" style={{ boxShadow: 'var(--shadow-m)'}}>
                        <CardHeader>
                            <h3 className="text-xl font-semibold text-zinc-200">Transaction Volume</h3>
                            <p className="text-sm opacity-70 text-zinc-200">Hourly transactions over the last 90 days</p>
                        </CardHeader>
                        <CardContent className="w-full text-zinc-200">
                            <ChartContainer
                                config={{
                                    total: {
                                        label: "Total Transactions",
                                        color: "#ffffff",
                                    },
                                    fraud: {
                                        label: "Fraud Transactions",
                                        color: "#ef4444",
                                    },
                                } satisfies ChartConfig}
                                className="h-[500px] w-full"
                            >
                                <LineChart
                                    data={chartData}
                                    margin={{
                                        left: 12,
                                        right: 12,
                                    }}
                                >
                                    <CartesianGrid strokeDasharray="2 2" stroke="#27272a" />
                                    <XAxis
                                        dataKey="hour"
                                        stroke="#a1a1aa"
                                        tick={{ fill: '#a1a1aa' }}
                                        tickLine={false}
                                        axisLine={false}
                                        tickMargin={20}
                                    />
                                    <YAxis
                                        stroke="#a1a1aa"
                                        tick={{ fill: '#a1a1aa' }}
                                        tickLine={false}
                                        axisLine={false}
                                        domain={[0, 500000]}
                                    />
                                    <ChartTooltip content={<ChartTooltipContent />} />
                                    <ChartLegend content={<ChartLegendContent />} />
                                    <Line
                                        type="monotone"
                                        dataKey="total"
                                        stroke="#ffffff"
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="fraud"
                                        stroke="#ef4444"
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                </LineChart>
                            </ChartContainer>
                        </CardContent>
                    </Card>
                    
                    <div className="w-full flex flex-col sm:flex-row flex-wrap gap-x-4">
                        <Card className="bg-[#0a0a0a] border-0 w-fit mt-6" style={{ boxShadow: 'var(--shadow-s)'}}>
                            <CardHeader>
                                <h3 className="text-xl font-semibold text-zinc-200">Device Fraud Analysis</h3>
                                <p className="text-sm opacity-70 text-zinc-200">Fraud transactions by device type</p>
                            </CardHeader>
                            <CardContent className="flex items-center justify-start pb-0 w-80 h-fit">
                                <ChartContainer
                                    config={{
                                        total: {
                                        label: "Total Transactions",
                                        color: "#ffffff",
                                        },
                                        fraud: {
                                        label: "Fraud Transactions",
                                        color: "#736262ff",
                                        },
                                    }}
                                    className="h-80 w-70"
                                    >
                                    <RadialBarChart
                                        data={chartData_Devices}
                                        startAngle={-90}
                                        endAngle={250}
                                        innerRadius={30}
                                        outerRadius={145}
                                    >
                                        <ChartTooltip
                                        cursor={false}
                                        content={<ChartTooltipContent hideLabel nameKey="device" />}
                                        />
                                        <ChartLegend content={<ChartLegendContent />} />

                                        {/* Base layer: total (white) */}
                                        <RadialBar
                                        dataKey="transactions"
                                        stackId="a"
                                        fill="#ffffff"
                                        background={true}
                                        cornerRadius={10}
                                        />

                                        {/* Overlay: fraud (#736262ff) */}
                                        <RadialBar
                                        dataKey="fraud"
                                        stackId="a"
                                        fill="#ef4444"
                                        cornerRadius={10}
                                        >
                                        <LabelList
                                            position="insideStart"
                                            dataKey="device"
                                            className="fill-white capitalize mix-blend-luminosity"
                                            fontSize={14}
                                        />
                                        </RadialBar>
                                    </RadialBarChart>
                                </ChartContainer>
                            </CardContent>
                        </Card>
                        <div className="flex flex-col gap-y-2 justify-between">
                            <Card className="bg-[#0a0a0a] border-0 w-fit mt-6 flex-1" style={{ boxShadow: 'var(--shadow-s)'}}>
                                <CardHeader>
                                    <h3 className="text-xl font-semibold text-zinc-200">Channel Fraud Analysis</h3>
                                    <p className="text-sm opacity-70 text-zinc-200">Fraud transactions by Channel type</p>
                                </CardHeader>
                                <CardContent className="flex items-center justify-start pb-0 w-fit h-50">
                                    <ChartContainer
                                        config={{
                                            total: {
                                            label: "Total Transactions",
                                            color: "#ffffff",
                                            },
                                            fraud: {
                                            label: "Fraud Transactions",
                                            color: "#736262ff",
                                            },
                                        }}
                                        className="h-60 w-60"
                                        >
                                        <RadialBarChart
                                            data={chartData_Channel}
                                            startAngle={-90}
                                            endAngle={250}
                                            innerRadius={30}
                                            outerRadius={110}
                                        >
                                            <ChartTooltip
                                            cursor={false}
                                            content={<ChartTooltipContent hideLabel nameKey="channel" />}
                                            />
                                            <ChartLegend content={<ChartLegendContent />} />

                                            {/* Base layer: total (white) */}
                                            <RadialBar
                                            dataKey="transactions"
                                            stackId="a"
                                            fill="#ffffff"
                                            background={true}
                                            cornerRadius={10}
                                            />

                                            {/* Overlay: fraud (#736262ff) */}
                                            <RadialBar
                                            dataKey="fraud"
                                            stackId="a"
                                            fill="#ef4444"
                                            cornerRadius={10}
                                            >
                                            <LabelList
                                                position="insideStart"
                                                dataKey="channel"
                                                className="fill-white capitalize mix-blend-luminosity"
                                                fontSize={14}
                                            />
                                            </RadialBar>
                                        </RadialBarChart>
                                    </ChartContainer>
                                </CardContent>
                            </Card>
                            <Card className="bg-[#0a0a0a] border-0 w-70 h-30 p-4" style={{ boxShadow: 'var(--shadow-s)'}}>
                                <CardContent className="flex flex-1 pb-0">
                                    <ChartContainer
                                        config={{
                                            total: {
                                                label: "Total Transactions",
                                                color: "#ffffff",
                                            },
                                            fraud: {
                                                label: "Fraud Transactions",
                                                color: "#ef4444",
                                            },
                                        } satisfies ChartConfig}
                                        className=" w-full h-full"
                                        >
                                        <RadialBarChart
                                            data={[{
                                                name: "transactions",
                                                total: cacheStats ? Object.values(cacheStats.countries).reduce((sum, country) => sum + country.total_transactions, 0) : 0,
                                                fraud: cacheStats ? Object.values(cacheStats.countries).reduce((sum, country) => sum + country.fraud_transactions, 0) : 0
                                            }]}
                                            startAngle={0}
                                            endAngle={180}
                                            innerRadius={80}
                                            outerRadius={130}
                                            className=""
                                            cy="80%"
                                        >
                                            <ChartTooltip
                                            cursor={false}
                                            content={<ChartTooltipContent hideLabel />}
                                            />
                                            <PolarRadiusAxis tick={false} tickLine={false} axisLine={false}>
                                            <Label
                                                content={({ viewBox }: { viewBox?: any }) => {
                                                if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                                                    const totalTransactions = cacheStats ? Object.values(cacheStats.countries).reduce((sum, country) => sum + country.total_transactions, 0) : 0;
                                                    const fraudTransactions = cacheStats ? Object.values(cacheStats.countries).reduce((sum, country) => sum + country.fraud_transactions, 0) : 0;
                                                    const centerX = viewBox.cx;
                                                    const centerY = viewBox.cy - 15;
                                                    return (
                                                    <text x={centerX} y={centerY} textAnchor="middle" dominantBaseline="middle">
                                                        <tspan
                                                        x={centerX}
                                                        y={centerY - 24}
                                                        className="fill-zinc-200 text-lg font-bold"
                                                        >
                                                        {totalTransactions.toLocaleString()}
                                                        </tspan>
                                                        <tspan
                                                        x={centerX}
                                                        y={centerY - 8}
                                                        className="fill-zinc-400 text-xs"
                                                        >
                                                        Total Transactions
                                                        </tspan>
                                                        <tspan
                                                        x={centerX}
                                                        y={centerY + 12}
                                                        className="fill-red-400 text-md font-semibold"
                                                        >
                                                        {fraudTransactions.toLocaleString()}
                                                        </tspan>
                                                        <tspan
                                                        x={centerX}
                                                        y={centerY + 26}
                                                        className="fill-red-300 text-xs"
                                                        >
                                                        Fraudulent
                                                        </tspan>
                                                    </text>
                                                    )
                                                }
                                                }}
                                            />
                                            </PolarRadiusAxis>
                                            <RadialBar
                                            dataKey="total"
                                            stackId="a"
                                            cornerRadius={5}
                                            fill="#ffffff"
                                            className="stroke-transparent stroke-2"
                                            />
                                            <RadialBar
                                            dataKey="fraud"
                                            fill="#ef4444"
                                            stackId="a"
                                            cornerRadius={5}
                                            className="stroke-transparent stroke-2"
                                            />
                                        </RadialBarChart>
                                    </ChartContainer>
                                </CardContent>
                            </Card>
                        </div>
                        <div className="flex flex-col gap-y-2 flex-1">
                            <Card className="bg-[#0a0a0a] border-0 flex-1 mt-6" style={{ boxShadow: 'var(--shadow-s)'}}>
                                <CardHeader>
                                    <h3 className="text-xl font-semibold text-zinc-200">Countries Fraud Analysis</h3>
                                    <p className="text-sm opacity-70 text-zinc-200">Fraud transactions by Countries</p>
                                </CardHeader>
                                <CardContent>
                                    <ChartContainer config={{
                                        transactions: {
                                            label: "Transactions",
                                        },
                                        "Total Transactions": {
                                            label: "Total Transactions",
                                            color: "#736262ff",
                                        },
                                        "Fraud Transactions": {
                                            label: "Fraud Transactions",
                                            color: "#fafafaff",
                                        },
                                        total: {
                                            label: "Total Transactions",
                                            color: "#ffffff",
                                        },
                                        fraud: {
                                            label: "Fraud Transactions",
                                            color: "#ef4444",
                                        },
                                    } satisfies ChartConfig}
                                    className="h-60 w-full text-white">
                                    <BarChart accessibilityLayer data={chartData_Country}>
                                        <CartesianGrid vertical={false} stroke="#27272a" />
                                        <XAxis
                                        dataKey="countries"
                                        tickLine={false}
                                        tickMargin={10}
                                        axisLine={false}
                                        tick={{ fill: '#a1a1aa' }}
                                        tickFormatter={(value) => value.slice(0, 3)}
                                        />
                                        <YAxis
                                        stroke="#a1a1aa"
                                        tick={{ fill: '#a1a1aa' }}
                                        tickLine={false}
                                        axisLine={false}
                                        />
                                        <ChartTooltip
                                        cursor={false}
                                        content={<ChartTooltipContent indicator="dashed" />}
                                        />
                                        <ChartLegend content={<ChartLegendContent />} />
                                        <Bar dataKey="total" fill="#ffffff" radius={4} />
                                        <Bar dataKey="fraud" fill="#ef4444" radius={4} />
                                    </BarChart>
                                    </ChartContainer>
                                </CardContent>
                            </Card>
                            <div className="flex flex-col sm:flex-row justify-evenly items-start flex-wrap gap-2 w-full mt-2">
                            {stats.map((stat) => (
                                <StatsCardDashboard
                                    key={stat.id}
                                    typeStat={stat.typeStat}
                                    statValue={stat.statValue}
                                    colour={stat.cardColour}
                                />
                            ))}
                            
                            </div>
                        </div>
                    </div>
                    <div className="flex flex-col sm:flex-row flex-wrap w-full mt-6 justify-evenly">
                        <Card className="flex flex-col w-[32%] bg-[#0a0a0a] border-0" style={{ boxShadow: 'var(--shadow-s)'}}>
                            <CardHeader className="items-center pb-0">
                                <h3 className="text-xl font-semibold text-zinc-200">High Risk Merchants Analysis</h3>
                                <p className="text-sm opacity-70 text-zinc-200">Transaction distribution by risk level</p>
                            </CardHeader>
                            <CardContent className="flex-1 pb-0">
                                <ChartContainer config={{
                                    transactions: {
                                        label: "Transactions",
                                    },
                                    "High Risk": {
                                        label: "High Risk",
                                        color: "#736262ff",
                                    },
                                    "Low Risk": {
                                        label: "Low Risk",
                                        color: "#fafafaff",
                                    },
                                } satisfies ChartConfig}
                                className="mx-auto aspect-square max-h-[250px] text-white"
                                >
                                <PieChart>
                                    <Pie
                                        key="high-risk-pie"
                                        data={chartData_HighRisk_Merchant}
                                        dataKey="transactions"
                                        nameKey="risk_level"
                                    />
                                    <ChartTooltip
                                        cursor={false}
                                        content={<ChartTooltipContent hideLabel />}
                                    />
                                    <ChartLegend
                                        content={<ChartLegendContent nameKey="risk_level" />}
                                        className="-translate-y-2 gap-2 *:basis-1/2 *:justify-center *flex-row"
                                    />
                                </PieChart>
                                </ChartContainer>
                            </CardContent>
                        </Card>
                        <Card className="flex flex-col w-[32%] bg-[#0a0a0a] border-0" style={{ boxShadow: 'var(--shadow-s)'}}>
                            <CardHeader className="items-center pb-0">
                                <h3 className="text-xl font-semibold text-zinc-200">Distance from Home Analysis</h3>
                                <p className="text-sm opacity-70 text-zinc-200">Transaction distribution by distance from home</p>
                            </CardHeader>
                            <CardContent className="flex-1 pb-0">
                                <ChartContainer config={{
                                    transactions: {
                                        label: "Transactions",
                                    },
                                    "Away from Home": {
                                        label: "Away from Home",
                                        color: "#736262ff",
                                    },
                                    "Home": {
                                        label: "Home",
                                        color: "#fafafaff",
                                    },
                                } satisfies ChartConfig}
                                className="mx-auto aspect-square max-h-[250px] text-white"
                                >
                                <PieChart>
                                    <Pie
                                        key="distance-pie"
                                        data={chartData_Distance_From_Home}
                                        dataKey="transactions"
                                        nameKey="risk_level"
                                    />
                                    <ChartTooltip
                                        cursor={false}
                                        content={<ChartTooltipContent hideLabel />}
                                    />
                                    <ChartLegend
                                        content={<ChartLegendContent nameKey="risk_level" />}
                                        className="-translate-y-2 gap-2 *:basis-1/2 *:justify-center *flex-row"
                                    />
                                </PieChart>
                                </ChartContainer>
                            </CardContent>
                        </Card>
                        <Card className="flex flex-col w-[32%] bg-[#0a0a0a] border-0" style={{ boxShadow: 'var(--shadow-s)'}}>
                            <CardHeader className="items-center pb-0">
                                <h3 className="text-xl font-semibold text-zinc-200">Weekend Transaction Analysis</h3>
                                <p className="text-sm opacity-70 text-zinc-200">Transaction distribution by day type</p>
                            </CardHeader>
                            <CardContent className="flex-1 pb-0">
                                <ChartContainer config={{
                                    transactions: {
                                        label: "Transactions",
                                    },
                                    "Weekend": {
                                        label: "Weekend",
                                        color: "#ef4444",
                                    },
                                    "Weekday": {
                                        label: "Weekday",
                                        color: "#fafafaff",
                                    },
                                } satisfies ChartConfig}
                                className="mx-auto aspect-square max-h-[250px] text-white"
                                >
                                <PieChart>
                                    <Pie
                                        key="weekend-pie"
                                        data={chartData_Weekend_Transaction}
                                        dataKey="transactions"
                                        nameKey="risk_level"
                                    />
                                    <ChartTooltip
                                        cursor={false}
                                        content={<ChartTooltipContent hideLabel />}
                                    />
                                    <ChartLegend
                                        content={<ChartLegendContent nameKey="risk_level" />}
                                        className="-translate-y-2 gap-2 *:basis-1/2 *:justify-center *flex-row"
                                    />
                                </PieChart>
                                </ChartContainer>
                            </CardContent>
                        </Card>
                    </div>
                </div>

            </div>
    )
}

