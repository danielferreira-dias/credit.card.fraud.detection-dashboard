import { Checkbox } from "@/components/ui/checkbox";
import { useNavbar } from "@/context/NavbarContext";
import { useUser } from "@/context/UserContext";
import { PanelLeft, PanelRight, AlertCircle, CheckCircle } from "lucide-react";
import { useEffect, useState } from "react";

interface ReportOutput {
    id: number;
    created_at: Date;
    report_content: ReportContent
}

interface ReportContent{
    title: string;
    created_at?: string;
    sentiment: "Urgent" | "Non Urgent";
    key_findings: {
        finding: string;
        evidence: string;
        severity: string;
    };
    critical_patterns: string[];
    recommendations: string[];
    analysis: string;
}


export default function PersonalPage(){
    const [reports, setReports] = useState<ReportOutput[]>([]);
    const [selectedReport, setSelectedReport] = useState<ReportOutput | null>(null);
    const [selectedReportIds, setSelectedReportIds] = useState<Set<number>>(new Set());
    const [activeTab, setActiveTab] = useState<"documents" | "transactions">("documents");
    const { user, loading } = useUser();


    useEffect(() => {
        const fetchReports = async () => {
            if (!user?.id) return; // Don't fetch if user is not loaded yet
            try {
                const response = await fetch(`http://localhost:80/users/reports/${user.id}`);
                if (!response.ok) throw new Error('Failed to fetch reports');
                const data = await response.json();
                console.log('data -> ', data)
                setReports(data);
            } catch (error) {
                console.error('Error fetching reports:', error);

            }
        };

        if (!loading && user) {
            fetchReports();
            const interval = setInterval(fetchReports, 5000);
            return () => clearInterval(interval);
        }
    }, [user, loading]);

    const handleCheckboxChange = (reportId: number) => {
        setSelectedReportIds(prev => {
            const newSet = new Set(prev);
            if (newSet.has(reportId)) {
                newSet.delete(reportId);
            } else {
                newSet.add(reportId);
            }
            return newSet;
        });
    };

    const handleDeleteSelected = async () => {
        if (selectedReportIds.size === 0) return;

        try {
            const deletePromises = Array.from(selectedReportIds).map(reportId =>
                fetch(`http://localhost:80/users/reports/${reportId}`, {
                    method: 'DELETE',
                })
            );

            await Promise.all(deletePromises);

            // Refresh reports after deletion
            if (user?.id) {
                const response = await fetch(`http://localhost:80/users/reports/${user.id}`);
                const data = await response.json();
                setReports(data);
            }

            // Clear selection
            setSelectedReportIds(new Set());
        } catch (error) {
            console.error('Error deleting reports:', error);
        }
    };

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

                {/* Tabs Section */}
                <div className="flex flex-col w-full border-b-[1px] border-b-zinc-700 border-t-[1px] border-t-zinc-700 mt-2">
                    <div className="flex flex-col gap-y-2 sm:flex-row sm:justify-between sm:items-center">
                        <div className="flex flex-row">
                            <button
                                onClick={() => setActiveTab("documents")}
                                className={`text-md py-3 pr-4 text-lg transition-colors ${
                                    activeTab === "documents"
                                        ? "text-white border-b-2 border-white"
                                        : "text-zinc-400 hover:text-white"
                                }`}
                            >
                                Documents
                            </button>
                            <button
                                onClick={() => setActiveTab("transactions")}
                                className={`text-md px-4 py-3 text-lg transition-colors ${
                                    activeTab === "transactions"
                                        ? "text-white border-b-2 border-white"
                                        : "text-zinc-400 hover:text-white"
                                }`}
                            >
                                Transactions
                            </button>
                        </div>
                        {activeTab === "documents" && selectedReportIds.size > 0 && (
                            <button
                                onClick={handleDeleteSelected}
                                className="flex items-center gap-2 px-4 py-2 bg-zinc-950 rounded transition-colors"
                            >
                                Delete
                            </button>
                        )}
                    </div>
                </div>

                {/* Documents Tab Content */}
                {activeTab === "documents" && (
                    reports.length === 0 ? (
                        <div className="w-full overflow-x-auto rounded-lg border-[1px] border-zinc-800">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-zinc-800 bg-zinc-950">
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
                        <div className="w-full overflow-x-auto rounded-lg border-[1px] border-zinc-800">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-zinc-900 bg-zinc-950">
                                        <th className="py-3 px-4 text-md font-medium text-zinc-200 w-12"></th>
                                        <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Title</th>
                                        <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Date</th>
                                        <th className="text-left py-3 px-4 text-md font-medium text-zinc-200">Sentiment</th>
                                        <th className="text-right py-3 px-4 text-md font-medium text-zinc-200">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {reports.map((report, index) => (
                                        <tr key={index} className="border-b border-zinc-800 hover:bg-zinc-900 transition-colors items-center">
                                            <td className="py-3 px-4">
                                                <div className="flex items-center justify-center">
                                                    <Checkbox
                                                    checked={selectedReportIds.has(report.id)}
                                                    onCheckedChange={() => handleCheckboxChange(report.id)}
                                                    aria-label="Select row"
                                                    />
                                                </div>
                                            </td>
                                            <td className="py-3 px-4 text-sm">{report.report_content.title}</td>
                                            <td className="py-3 px-4 text-sm text-zinc-300">
                                                {report.created_at ? `${new Date(report.created_at).toLocaleString()}` : 'Date not available'}
                                            </td>
                                            <td className="py-3 px-4 text-sm">
                                                <span className={`px-2 py-1 rounded text-xs flex items-center gap-1 w-fit ${
                                                    report.report_content.sentiment === "Urgent"
                                                        ? "bg-red-900/30 text-red-400"
                                                        : "bg-blue-900/30 text-blue-400"
                                                }`}>
                                                    {report.report_content.sentiment === "Urgent" ? (
                                                        <AlertCircle className="w-3 h-3" />
                                                    ) : (
                                                        <CheckCircle className="w-3 h-3" />
                                                    )}
                                                    {report.report_content.sentiment}
                                                </span>
                                            </td>
                                            <td className="py-3  text-sm text-right">
                                                <button
                                                    onClick={() => setSelectedReport(report)}
                                                    className="px-3 py-1 hover:text-white text-zinc-200 rounded text-sm transition-colors"
                                                >
                                                    View Details
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )
                )}

                {/* Transactions Tab Content */}
                {activeTab === "transactions" && (
                    <div className="w-full rounded-lg border-[1px] border-zinc-800 p-8">
                        <div className="flex flex-col items-center justify-center gap-4">
                            <p className="text-zinc-400 text-lg">Transactions view coming soon</p>
                            <p className="text-zinc-500 text-sm">This feature will display your transaction history</p>
                        </div>
                    </div>
                )}

                {/* Report Detail Modal/Section */}
                {selectedReport && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" onClick={() => setSelectedReport(null)}>
                        <div className=" rounded-lg bg-black max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-zinc-800" onClick={(e) => e.stopPropagation()}>
                            <div className="sticky top-0 bg-black border-b border-zinc-800 p-6 flex justify-between items-start">
                                <div>
                                    <h2 className="text-2xl font-semibold">{selectedReport.report_content.title}</h2>
                                    <p className="text-sm text-zinc-400 mt-1">
                                        {selectedReport.created_at ? `Generated on ${new Date(selectedReport.created_at).toLocaleString()}` : 'Date not available'}
                                    </p>
                                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs mt-2 ${
                                        selectedReport.report_content.sentiment === "Urgent"
                                            ? "bg-red-900/30 text-red-400"
                                            : "bg-blue-900/30 text-blue-400"
                                    }`}>
                                        {selectedReport.report_content.sentiment === "Urgent" ? (
                                            <AlertCircle className="w-3 h-3" />
                                        ) : (
                                            <CheckCircle className="w-3 h-3" />
                                        )}
                                        {selectedReport.report_content.sentiment}
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
                                    <div className="bg-zinc-900 p-4 rounded border border-zinc-800 space-y-3">
                                        <div>
                                            <p className="text-sm font-semibold text-red-400 mb-2">
                                                Severity: {selectedReport.report_content.key_findings.severity}
                                            </p>
                                            <p className="text-sm font-medium text-zinc-300 mb-3">
                                                {selectedReport.report_content.key_findings.finding}
                                            </p>
                                            <div className="text-sm text-zinc-400 mt-2">
                                                <p className="font-semibold text-zinc-300 mb-1">Evidence:</p>
                                                <pre className="whitespace-pre-wrap font-sans">
                                                    {selectedReport.report_content.key_findings.evidence}
                                                </pre>
                                            </div>
                                        </div>
                                    </div>
                                </section>

                                {/* Critical Patterns */}
                                <section>
                                    <h3 className="text-lg font-semibold mb-3 text-zinc-200">Critical Patterns</h3>
                                    <ul className="space-y-2">
                                        {selectedReport.report_content.critical_patterns.map((pattern, idx) => (
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
                                        {selectedReport.report_content.recommendations.map((rec, idx) => (
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
                                    <div className="bg-zinc-950 p-4 rounded border border-zinc-800">
                                        <p className="text-sm text-zinc-300 whitespace-pre-wrap leading-relaxed">
                                            {selectedReport.report_content.analysis}
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