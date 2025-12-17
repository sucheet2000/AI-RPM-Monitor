import React, { useState, useEffect } from 'react';
import { getSummaries } from '../api';

const ReportCard = ({ patientId }) => {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchSummary = async () => {
            setLoading(true);
            try {
                const result = await getSummaries(patientId);
                if (result.error) {
                    throw new Error(result.error);
                }
                if (result.summaries && result.summaries.length > 0) {
                    setSummary(result.summaries[0]);
                    setError(null);
                } else {
                    setSummary(null);
                    setError("No recent LLM Summary available.");
                }
            } catch (err) {
                console.error("Error fetching summary for report card:", err);
                setError("Failed to load AI Triage Report.");
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
        // Poll less frequently than vitals/alerts, as summaries change less often
        const intervalId = setInterval(fetchSummary, 30000);
        return () => clearInterval(intervalId);
    }, [patientId]);

    if (loading) return <div className="bg-dark-card p-6 rounded-lg shadow-xl"><p className="text-gray-400">Loading AI Wellness Report...</p></div>;

    const riskColor = summary?.risk_score > 0.75 ? 'text-secondary-red' : summary?.risk_score > 0.5 ? 'text-status-warning' : 'text-status-normal';

    return (
        <div className="bg-dark-card p-6 rounded-lg shadow-xl border border-gray-700 h-full">
            <h2 className="text-2xl font-bold mb-4 flex items-center justify-between">
                AI Clinical Triage Report
                <span className={`text-xl font-mono ${riskColor}`}>
                    Risk: {summary ? (summary.risk_score * 100).toFixed(1) : 'N/A'}%
                </span>
            </h2>

            {error && <p className="text-secondary-red">{error}</p>}

            {summary && (
                <>
                    <div className="mb-6">
                        <h3 className="text-xl font-semibold mb-2 text-primary-blue">
                            Summary & Findings
                        </h3>
                        <p className="text-gray-300 whitespace-pre-line leading-relaxed">
                            {summary.summary_text}
                        </p>
                    </div>

                    <div className="border-t border-gray-700 pt-4">
                        <h3 className="text-xl font-semibold mb-2 text-primary-blue">
                            Recommended Actions
                        </h3>
                        <pre className="text-gray-300 font-sans whitespace-pre-wrap">
                            {summary.recommendation}
                        </pre>
                    </div>
                </>
            )}
        </div>
    );
};

export default ReportCard;
