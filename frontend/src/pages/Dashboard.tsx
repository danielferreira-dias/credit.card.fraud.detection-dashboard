import { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, LabelList, RadialBar, RadialBarChart, BarChart, Bar } from "recharts"
import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { type ChartConfig, ChartContainer } from "@/components/ui/chart"
import { ChartLegend, ChartLegendContent } from "@/components/ui/chart"
import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card"
import StatsCard from "@/components/StatsCard"


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
        ? Object.entries(cacheStats.device).map(([device, data], index) => ({
            device: device,
            total: data.total_transactions,
            fraud: data.fraud_transactions,
            fill: `hsl(var(--chart-${(index % 5) + 1}))`
        }))
        : [];

    const chartData_Channel = cacheStats?.channel
        ? Object.entries(cacheStats.channel).map(([channel, data], index) => ({
            channel: channel,
            total: data.total_transactions,
            fraud: data.fraud_transactions,
            fill: `hsl(var(--chart-${(index % 5) + 1}))`
        }))
        : [];

    const chartData_Country = cacheStats?.countries
        ? Object.entries(cacheStats.countries).map(([countries, data], index) => ({
            countries: countries,
            total: data.total_transactions,
            fraud: data.fraud_transactions,
            fill: `hsl(var(--chart-${(index % 5) + 1}))`
        }))
        : [];

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
            <h2 className="text-2xl font-semibold opacity-90 mt-4">Insight Dashboard Analytics</h2>
            <h3 className="text-sm opacity-70 mb-6">Real-time fraud detection analytics with AI-powered insights</h3>

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
                <div className="flex flex-col md:flex-row justify-between items-center">
                    <div className="flex flex-col">
                        <h2 className="text-2xl font-semibold opacity-90 mt-4">Insight Dashboard Analytics</h2>
                        <h3 className="text-sm opacity-70 mb-6">Real-time fraud detection analytics with AI-powered insights</h3>
                    </div>
                    <button className="w-40 h-10 p-2 rounded-xl text-sm" style={{ boxShadow: 'var(--shadow-s)'}}> Generate Report </button>
                </div>
                
                <div className="flex flex-col">
                    <Card className="bg-zinc-950 border-0 w-full" style={{ boxShadow: 'var(--shadow-m)'}}>
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
                                        tickMargin={8}
                                    />
                                    <YAxis
                                        stroke="#a1a1aa"
                                        tick={{ fill: '#a1a1aa' }}
                                        tickLine={false}
                                        axisLine={false}
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
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 w-full items-center mt-6">
                    {stats.map((stat) => (
                        <StatsCard
                            key={stat.id}
                            typeStat={stat.typeStat}
                            statValue={stat.statValue}
                            colour={stat.cardColour}
                        />
                    ))}
                    </div>
                    <div className="w-full flex flex-col sm:flex-row flex-wrap gap-x-4">
                        <Card className="bg-zinc-950 border-0 w-fit mt-6" style={{ boxShadow: 'var(--shadow-s)'}}>
                            <CardHeader>
                                <h3 className="text-xl font-semibold text-zinc-200">Device Fraud Analysis</h3>
                                <p className="text-sm opacity-70 text-zinc-200">Fraud transactions by device type</p>
                            </CardHeader>
                            <CardContent className="flex items-center justify-start pb-0 w-fit h-fit">
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
                                    className="h-60 w-70">
                                    <RadialBarChart
                                        data={chartData_Devices}
                                        startAngle={-90}
                                        endAngle={250}
                                        innerRadius={30}
                                        outerRadius={130}
                                    >
                                        <ChartTooltip
                                            cursor={false}
                                            content={<ChartTooltipContent hideLabel nameKey="device" />}
                                        />
                                        <ChartLegend content={<ChartLegendContent />} />
                                        <RadialBar dataKey="fraud" background>
                                            <LabelList
                                                position="insideStart"
                                                dataKey="device"
                                                className="fill-white capitalize mix-blend-luminosity"
                                                fontSize={11}
                                            />
                                        </RadialBar>
                                    </RadialBarChart>
                                </ChartContainer>
                            </CardContent>
                        </Card>
                        <Card className="bg-zinc-950 border-0 w-fit mt-6" style={{ boxShadow: 'var(--shadow-s)'}}>
                            <CardHeader>
                                <h3 className="text-xl font-semibold text-zinc-200">Channel Fraud Analysis</h3>
                                <p className="text-sm opacity-70 text-zinc-200">Fraud transactions by Channel type</p>
                            </CardHeader>
                            <CardContent className="flex items-center justify-start pb-0 w-fit h-fit">
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
                                    className="h-60 w-60">
                                    <RadialBarChart
                                        data={chartData_Channel}
                                        startAngle={-90}
                                        endAngle={250}
                                        innerRadius={30}
                                        outerRadius={130}
                                    >
                                        <ChartTooltip
                                            cursor={false}
                                            content={<ChartTooltipContent hideLabel nameKey="device" />}
                                        />
                                        <ChartLegend content={<ChartLegendContent />} />
                                        <RadialBar dataKey="fraud" background>
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
                        <Card className="bg-zinc-950 border-0 flex-1 mt-6" style={{ boxShadow: 'var(--shadow-s)'}}>
                            <CardHeader>
                                <h3 className="text-xl font-semibold text-zinc-200">Countries Fraud Analysis</h3>
                                <p className="text-sm opacity-70 text-zinc-200">Fraud transactions by Countries</p>
                            </CardHeader>
                            <CardContent>
                                <ChartContainer config={{
                                    total: {
                                        label: "Total Transactions",
                                        color: "#ffffff",
                                    },
                                    fraud: {
                                        label: "Fraud Transactions",
                                        color: "#ef4444",
                                    },
                                } satisfies ChartConfig}
                                className="h-60 w-full">
                                <BarChart accessibilityLayer data={chartData_Country}>
                                    <CartesianGrid vertical={false} />
                                    <XAxis
                                    dataKey="countries"
                                    tickLine={false}
                                    tickMargin={10}
                                    axisLine={false}
                                    tickFormatter={(value) => value.slice(0, 3)}
                                    />
                                    <ChartTooltip
                                    cursor={false}
                                    content={<ChartTooltipContent indicator="dashed" />}
                                    />
                                    <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
                                    <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
                                </BarChart>
                                </ChartContainer>
                            </CardContent>
                        </Card>
                    </div>
                </div>

            </div>
    )
}

