import { Bar, BarChart, XAxis, Pie, PieChart, Label } from "recharts"
import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { type ChartConfig, ChartContainer,  } from "@/components/ui/chart"
import { ChartLegend, ChartLegendContent } from "@/components/ui/chart"
import { TrendingUp } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"


export default function DashboardPage(){
    const chartData = [
        { month: "January", desktop: 186, mobile: 80 },
        { month: "February", desktop: 305, mobile: 200 },
        { month: "March", desktop: 237, mobile: 120 },
        { month: "April", desktop: 73, mobile: 190 },
        { month: "May", desktop: 209, mobile: 130 },
        { month: "June", desktop: 214, mobile: 140 },
    ]

    const chartConfig = {
    desktop: {
        label: "Desktop",
        color: "#2563eb",
    },
    mobile: {
        label: "Mobile",
        color: "#60a5fa",
    },
    } satisfies ChartConfig

    const chartData_Pie = [
        { browser: "chrome", visitors: 275, fill: "var(--color-chrome)" },
        { browser: "other", visitors: 90, fill: "var(--color-other)" },
    ]

    const chartConfig_Pie = {
        visitors: {
            label: "Visitors",
        },
        chrome: {
            label: "Chrome",
            color: "#2563eb",
        },
        other: {
            label: "Other",
            color: "#60a5fa",
        },
    } satisfies ChartConfig

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
                <h3 className="text-sm opacity-70">Here you have access to all the analytic charts where you have an AI Agent insight</h3>
                <div className="flex flex-col sm:flex-row gap-x-6 gap-y-6 flex-wrap">
                    <ChartContainer config={chartConfig} className="min-h-[200px] w-90 h-70">
                        <BarChart accessibilityLayer data={chartData}>
                            <XAxis
                            dataKey="month"
                            tickLine={false}
                            tickMargin={10}
                            axisLine={false}
                            tickFormatter={(value) => value.slice(0, 3)}
                            />
                            <ChartTooltip content={<ChartTooltipContent />} />
                            <ChartLegend content={<ChartLegendContent />} />
                            <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
                            <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
                        </BarChart>
                    </ChartContainer>
                    <ChartContainer config={chartConfig} className="min-h-[200px] w-90 h-70">
                        <BarChart accessibilityLayer data={chartData}>
                            <XAxis
                            dataKey="month"
                            tickLine={false}
                            tickMargin={10}
                            axisLine={false}
                            tickFormatter={(value) => value.slice(0, 3)}
                            />
                            <ChartTooltip content={<ChartTooltipContent />} />
                            <ChartLegend content={<ChartLegendContent />} />
                            <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
                            <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
                        </BarChart>
                    </ChartContainer>
                    <ChartContainer
                        config={chartConfig_Pie}
                        className="pb-0 min-h-[200px] w-90 h-70"
                        >
                        <PieChart>
                            <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                            <ChartLegend content={<ChartLegendContent />} />
                            <Pie data={chartData_Pie} dataKey="visitors" label nameKey="browser" />
                        </PieChart>
                    </ChartContainer>
                    <ChartContainer
                        config={chartConfig_Pie}
                        className="pb-0 min-h-[200px] w-90 h-70"
                        >
                        <PieChart>
                            <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                            <ChartLegend content={<ChartLegendContent />} />
                            <Pie data={chartData_Pie} dataKey="visitors" label nameKey="browser" />
                        </PieChart>
                    </ChartContainer>
                </div>
            </div>
    )
}

