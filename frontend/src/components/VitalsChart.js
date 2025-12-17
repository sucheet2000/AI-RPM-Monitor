import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getVitals } from '../api';

const VitalsChart = ({ patientId }) => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchVitals = async () => {
        try {
            setError(null);
            const result = await getVitals(patientId, 24); // Fetch last 24 hours
            if (result.error) {
                throw new Error(result.error);
            }

            // Transform data for recharts: only take HR and convert timestamp
            const formattedData = result.records.map(record => ({
                time: new Date(record.reading_timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                heart_rate: record.vitals.heart_rate,
            })).reverse(); // Reverse for chronological order on chart

            setData(formattedData);
        } catch (err) {
            console.error("Error fetching vitals:", err);
            setError("Failed to load vitals data. Check backend status.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Initial fetch
        fetchVitals();

        // Set up 10-second polling (Requirement 3)
        const intervalId = setInterval(fetchVitals, 10000);

        // Cleanup function
        return () => clearInterval(intervalId);
    }, [patientId]);

    if (loading) return <div className="p-4 text-center">Loading Vitals Chart...</div>;
    if (error) return <div className="p-4 text-center text-secondary-red bg-red-900/20 border border-secondary-red rounded-lg">{error}</div>;
    if (data.length === 0) return <div className="p-4 text-center text-status-warning">No vital records found for the last 24 hours.</div>;

    // Determine min/max Y-axis for stability, ensuring normal range (50-100) is always visible
    const hrValues = data.map(d => d.heart_rate);
    const minHR = Math.min(...hrValues);
    const maxHR = Math.max(...hrValues);

    const yDomainMin = Math.max(0, Math.floor(Math.min(minHR, 50) / 10) * 10 - 10);
    const yDomainMax = Math.ceil(Math.max(maxHR, 100) / 10) * 10 + 10;

    return (
        <div className="h-96 w-full p-4">
            <h3 className="text-xl font-semibold mb-4 text-gray-200">Heart Rate Trend (Last 24 Hours)</h3>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="time" stroke="#9ca3af" />
                    <YAxis
                        label={{ value: 'Heart Rate (bpm)', angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                        domain={[yDomainMin, yDomainMax]}
                        stroke="#9ca3af"
                    />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                    <Line
                        type="monotone"
                        dataKey="heart_rate"
                        stroke="#10b981"
                        strokeWidth={2}
                        dot={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default VitalsChart;
