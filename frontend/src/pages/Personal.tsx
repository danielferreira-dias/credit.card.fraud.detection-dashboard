import { useNavbar } from "@/context/NavbarContext";
import { useUser } from "@/context/UserContext";
import { PanelLeft, PanelRight, AlertCircle, CheckCircle } from "lucide-react";
import { useEffect, useState } from "react";

interface ReportOutput {
    title: string;
    date: string;
    sentiment: "Urgent" | "Non Urgent";
    key_findings: Array<{ category: string; finding: string }>;
    critical_patterns: string[];
    recommendations: string[];
    analysis: string;
}

export default function PersonalPage(){
    const [reports, setReports] = useState<ReportOutput[]>([]);
    const [selectedReport, setSelectedReport] = useState<ReportOutput | null>(null);
    const { user, loading } = useUser();

    useEffect(() => {
        const fetchReports = async () => {
            try {
                // Replace with your actual user ID
                const response = await fetch(`http://localhost:80/users/${user?.id}/reports`);
                if (!response.ok) throw new Error('Failed to fetch reports');
                const data = await response.json();
                setReports(data);
            } catch (error) {
                console.error('Error fetching reports:', error);
            } 
        };
        fetchReports();
    }, [user]);

    const { isCollapsed, toggleCollapsed } = useNavbar();
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
            <div className="flex flex-col gap-3 mt-4">
                <div className="flex flex-row gap-x-1">
                    <button onClick={toggleCollapsed} className="hover:shadow-2xl hover:shadow-zinc-800  w-8 h-8 bg-zinc-950 shadow-r-lg flex items-center justify-center">
                        {isCollapsed ? <PanelRight color="white" size={18} /> : <PanelLeft color="white" size={18} />}
                    </button>
                    <div className="h-full flex flex-col border-zinc-900 px-4 gap-y-1">
                        <h2 className="text-2xl font-semibold opacity-90">Account</h2>
                    </div>
                </div>

                {/* Reports Section */}
                <div className="flex flex-col w-full border-b-[1px] border-b-zinc-600 border-t-[1px] border-t-zinc-600 py-4 px-2 mt-6">
                    <h3 className="text-md opacity-100 ">Documents</h3>
                </div>

                {loading ? (
                    <div className="w-full overflow-x-auto rounded-lg border-[1px] border-zinc-900">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-zinc-900 bg-zinc-900">
                                    <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Title</th>
                                    <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Date</th>
                                    <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Sentiment</th>
                                    <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Patterns</th>
                                    <th className="text-right py-3 px-4 text-md font-medium text-zinc-200">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {[...Array(3)].map((_, index) => (
                                    <tr key={index} className="border-b border-zinc-800 animate-pulse">
                                        <td className="py-3 px-4">
                                            <div className="h-4 bg-zinc-800 rounded w-3/4"></div>
                                        </td>
                                        <td className="py-3 px-4">
                                            <div className="h-4 bg-zinc-800 rounded w-24"></div>
                                        </td>
                                        <td className="py-3 px-4">
                                            <div className="h-6 bg-zinc-800 rounded w-20"></div>
                                        </td>
                                        <td className="py-3 px-4">
                                            <div className="h-4 bg-zinc-800 rounded w-16"></div>
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <div className="h-7 bg-zinc-800 rounded w-24 ml-auto"></div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : reports.length === 0 ? (
                    <div className="w-full overflow-x-auto rounded-lg border-[1px] border-zinc-800"> 
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-zinc-800 bg-zinc-900">
                                    <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Title</th>
                                    <th className="py-3 px-4 text-md font-medium text-zinc-200">Date</th>
                                    <th className="py-3 px-4 text-md font-medium text-zinc-200">Sentiment</th>
                                    <th className="py-3 px-4 text-md font-medium text-zinc-200">Patterns</th>
                                    <th className="py-3 px-4 text-md font-medium text-zinc-200">Actions</th>
                                </tr>
                            </thead>
                        </table>
                        <div className="flex justify-center items-center py-8">
                            <p className="text-zinc-200">No reports available</p>
                        </div>
                    </div>
                ) : (
                    <div className="w-full overflow-x-auto rounded-lg border-[1px] border-zinc-900">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-zinc-900 bg-zinc-900">
                                    <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Title</th>
                                    <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Date</th>
                                    <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Sentiment</th>
                                    <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Patterns</th>
                                    <th className="text-right py-3 px-4 text-md font-medium text-zinc-200">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {reports.map((report, index) => (
                                    <tr key={index} className="border-b border-zinc-800 hover:bg-zinc-900 transition-colors">
                                        <td className="py-3 px-4 text-sm">{report.title}</td>
                                        <td className="py-3 px-4 text-sm text-zinc-300">
                                            {new Date(report.date).toLocaleDateString()}
                                        </td>
                                        <td className="py-3 px-4 text-sm">
                                            <span className={`px-2 py-1 rounded text-xs flex items-center gap-1 w-fit ${
                                                report.sentiment === "Urgent"
                                                    ? "bg-red-900/30 text-red-400"
                                                    : "bg-blue-900/30 text-blue-400"
                                            }`}>
                                                {report.sentiment === "Urgent" ? (
                                                    <AlertCircle className="w-3 h-3" />
                                                ) : (
                                                    <CheckCircle className="w-3 h-3" />
                                                )}
                                                {report.sentiment}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-zinc-300">
                                            {report.critical_patterns.length} patterns
                                        </td>
                                        <td className="py-3 px-4 text-sm text-right">
                                            <button
                                                onClick={() => setSelectedReport(report)}
                                                className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 rounded text-xs transition-colors"
                                            >
                                                View Details
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Report Detail Modal/Section */}
                {selectedReport && (
                    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50" onClick={() => setSelectedReport(null)}>
                        <div className="bg-zinc-950 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-zinc-800" onClick={(e) => e.stopPropagation()}>
                            <div className="sticky top-0 bg-zinc-950 border-b border-zinc-800 p-6 flex justify-between items-start">
                                <div>
                                    <h2 className="text-2xl font-semibold">{selectedReport.title}</h2>
                                    <p className="text-sm text-zinc-400 mt-1">
                                        Generated on {new Date(selectedReport.date).toLocaleString()}
                                    </p>
                                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs mt-2 ${
                                        selectedReport.sentiment === "Urgent"
                                            ? "bg-red-900/30 text-red-400"
                                            : "bg-blue-900/30 text-blue-400"
                                    }`}>
                                        {selectedReport.sentiment === "Urgent" ? (
                                            <AlertCircle className="w-3 h-3" />
                                        ) : (
                                            <CheckCircle className="w-3 h-3" />
                                        )}
                                        {selectedReport.sentiment}
                                    </span>
                                </div>
                                <button
                                    onClick={() => setSelectedReport(null)}
                                    className="text-zinc-400 hover:text-white text-2xl"
                                >
                                    ×
                                </button>
                            </div>

                            <div className="p-6 space-y-6">
                                {/* Key Findings */}
                                <section>
                                    <h3 className="text-lg font-semibold mb-3 text-zinc-200">Key Findings</h3>
                                    <div className="space-y-2">
                                        {selectedReport.key_findings.map((finding, idx) => (
                                            <div key={idx} className="bg-zinc-900 p-3 rounded border border-zinc-800">
                                                <p className="text-sm font-medium text-zinc-300">{finding.category}</p>
                                                <p className="text-sm text-zinc-400 mt-1">{finding.finding}</p>
                                            </div>
                                        ))}
                                    </div>
                                </section>

                                {/* Critical Patterns */}
                                <section>
                                    <h3 className="text-lg font-semibold mb-3 text-zinc-200">Critical Patterns</h3>
                                    <ul className="space-y-2">
                                        {selectedReport.critical_patterns.map((pattern, idx) => (
                                            <li key={idx} className="flex items-start gap-2 text-sm text-zinc-300">
                                                <span className="text-red-400 mt-1">•</span>
                                                <span>{pattern}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </section>

                                {/* Recommendations */}
                                <section>
                                    <h3 className="text-lg font-semibold mb-3 text-zinc-200">Recommendations</h3>
                                    <ul className="space-y-2">
                                        {selectedReport.recommendations.map((rec, idx) => (
                                            <li key={idx} className="flex items-start gap-2 text-sm text-zinc-300">
                                                <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                                                <span>{rec}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </section>

                                {/* Analysis */}
                                <section>
                                    <h3 className="text-lg font-semibold mb-3 text-zinc-200">Detailed Analysis</h3>
                                    <div className="bg-zinc-900 p-4 rounded border border-zinc-800">
                                        <p className="text-sm text-zinc-300 whitespace-pre-wrap leading-relaxed">
                                            {selectedReport.analysis}
                                        </p>
                                    </div>
                                </section>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}