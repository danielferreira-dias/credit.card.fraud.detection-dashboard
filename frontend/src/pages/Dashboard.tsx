import { useEffect, useState } from "react"
import { Bar, BarChart, XAxis, YAxis, Pie, PieChart, Cell } from "recharts"
import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { type ChartConfig, ChartContainer } from "@/components/ui/chart"
import { ChartLegend, ChartLegendContent } from "@/components/ui/chart"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import StatsLoadingCard from "@/components/StatsLoadingCard"
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
}

// Mockup data matching backend response format
const mockupStats: StatsResponse = {
    countries: {
        "USA": { total_transactions: 4532, fraud_transactions: 287 },
        "UK": { total_transactions: 3421, fraud_transactions: 198 },
        "Germany": { total_transactions: 2987, fraud_transactions: 154 },
        "France": { total_transactions: 2654, fraud_transactions: 176 },
        "Canada": { total_transactions: 2341, fraud_transactions: 132 },
        "Australia": { total_transactions: 2103, fraud_transactions: 98 },
        "Japan": { total_transactions: 1876, fraud_transactions: 67 },
        "Brazil": { total_transactions: 1654, fraud_transactions: 245 },
        "Mexico": { total_transactions: 1432, fraud_transactions: 189 },
        "Nigeria": { total_transactions: 987, fraud_transactions: 156 },
    },
    merchant_category: {
        "Retail": { total_transactions: 5432, fraud_transactions: 321 },
        "Online Shopping": { total_transactions: 4876, fraud_transactions: 412 },
        "Food & Dining": { total_transactions: 3987, fraud_transactions: 187 },
        "Travel": { total_transactions: 3456, fraud_transactions: 234 },
        "Entertainment": { total_transactions: 2987, fraud_transactions: 156 },
        "Gas Stations": { total_transactions: 2654, fraud_transactions: 98 },
        "Healthcare": { total_transactions: 2341, fraud_transactions: 76 },
        "Utilities": { total_transactions: 1987, fraud_transactions: 54 },
        "Insurance": { total_transactions: 1654, fraud_transactions: 43 },
        "Education": { total_transactions: 1432, fraud_transactions: 32 },
    },
    device: {
        "Chrome": { total_transactions: 6543, fraud_transactions: 387 },
        "Safari": { total_transactions: 5432, fraud_transactions: 298 },
        "Android App": { total_transactions: 4321, fraud_transactions: 321 },
        "iOS App": { total_transactions: 3987, fraud_transactions: 254 },
        "Firefox": { total_transactions: 2876, fraud_transactions: 176 },
        "Edge": { total_transactions: 2134, fraud_transactions: 143 },
        "Chip Reader": { total_transactions: 1876, fraud_transactions: 234 },
        "NFC Payment": { total_transactions: 1543, fraud_transactions: 198 },
        "Magnetic Stripe": { total_transactions: 987, fraud_transactions: 156 },
    },
    channel: {
        "web": { total_transactions: 12543, fraud_transactions: 765 },
        "mobile": { total_transactions: 9876, fraud_transactions: 654 },
        "pos": { total_transactions: 6432, fraud_transactions: 432 },
        "medium": { total_transactions: 2341, fraud_transactions: 187 },
    },
    high_risk_merchant: {
        "false": { total_transactions: 24567, fraud_transactions: 1234 },
        "true": { total_transactions: 6625, fraud_transactions: 804 },
    },
    distance_from_home: {
        "0": { total_transactions: 18765, fraud_transactions: 876 },
        "1": { total_transactions: 12427, fraud_transactions: 1162 },
    },
    card_present: {
        "true": { total_transactions: 14532, fraud_transactions: 654 },
        "false": { total_transactions: 16660, fraud_transactions: 1384 },
    },
    weekend_transaction: {
        "false": { total_transactions: 21543, fraud_transactions: 1345 },
        "true": { total_transactions: 9649, fraud_transactions: 693 },
    },
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
            <div className="w-40 h-40 rounded-full border-[16px] border-0" style={{ boxShadow: 'var(--shadow-s)'}}></div>
            <div className="w-40 h-40 rounded-full border-[16px] border-zinc-700/50 absolute top-0 left-0"
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
    const [stats, setStats] = useState<StatsResponse | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchStats = async () => {
            try {
                // Simulate loading delay to see skeleton loaders
                await new Promise(resolve => setTimeout(resolve, 2000))

                // Use mockup data instead of fetching from backend
                setStats(mockupStats)

                // Uncomment below to use real backend when available
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
                
        </div>
    )
}

