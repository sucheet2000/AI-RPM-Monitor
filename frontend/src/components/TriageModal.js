import React, { useState, useEffect } from 'react';
import { getSummaries } from '../api';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { monokai } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const TriageModal = ({ patientId, isOpen, onClose }) => {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!isOpen) return;

        const fetchSummary = async () => {
            setLoading(true);
            setError(null);
            try {
                const result = await getSummaries(patientId);
                if (result.error) {
                    throw new Error(result.error);
                }
                // Check if any summary exists
                if (result.summaries && result.summaries.length > 0) {
                    setSummary(result.summaries[0]);
                } else {
                    setError("No LLM summaries found for this patient.");
                }
            } catch (err) {
                console.error("Error fetching summary:", err);
                setError("Failed to load LLM summary. Check backend connection.");
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, [isOpen, patientId]);

    if (!isOpen) return null;

    let structuredJsonContent = null;
    try {
        if (summary?.structured_json) {
            // Requirement 5: Display structured_json in a readable format
            structuredJsonContent = JSON.stringify(summary.structured_json, null, 2);
        }
    } catch (e) {
        structuredJsonContent = "Error parsing structured JSON content.";
    }


    return (
        <div className="fixed inset-0 bg-black bg-opacity-70 z-50 flex justify-center items-center p-4">
            <div className="bg-dark-card rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
                <div className="flex justify-between items-center p-6 border-b border-gray-700">
                    <h2 className="text-2xl font-bold text-secondary-red">
                        🔴 CRITICAL LLM TRIAGE REPORT (Patient {patientId})
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white text-3xl leading-none">&times;</button>
                </div>

                <div className="p-6 overflow-y-auto flex-grow">
                    {loading && <p className="text-center text-gray-400">Fetching latest triage report...</p>}
                    {error && <p className="text-center text-secondary-red">{error}</p>}

                    {!loading && structuredJsonContent && (
                        <>
                            <p className="text-gray-400 mb-4">
                                This is the raw, machine-readable JSON output from the Gemini LLM, enforced by Pydantic schema for reliability.
                            </p>
                            <div className="syntax-highlighter-block">
                                {/* Requirement 5: Syntax-highlighted code block */}
                                <SyntaxHighlighter language="json" style={monokai}>
                                    {structuredJsonContent}
                                </SyntaxHighlighter>
                            </div>
                        </>
                    )}
                </div>

                <div className="p-4 border-t border-gray-700 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-primary-blue text-white rounded hover:bg-blue-700 transition"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TriageModal;
