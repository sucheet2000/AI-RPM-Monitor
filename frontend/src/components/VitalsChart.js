import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getVitals } from '../api';
import socketIOClient from 'socket.io-client';

const ENDPOINT = "http://localhost:5001";

const VitalsChart = ({ patientId }) => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchHistory = async () => {
        try {
            setError(null);
            const result = await getVitals(patientId, 24); // Fetch last 24 hours
            if (result.error) {
                throw new Error(result.error);
            }

            // Transform data for recharts: only take HR and convert timestamp
            // Backend returns Descending (newest first), so we REVERSE to get Ascending (oldest first)
            const formattedData = result.records.map(record => ({
                time: new Date(record.reading_timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                heart_rate: record.vitals.heart_rate,
            })).reverse();

            setData(formattedData);
        } catch (err) {
            console.error("Error fetching vitals history:", err);
            setError("Failed to load vitals data.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // 1. Initial Load of History
        fetchHistory();

        // 2. Connect to Socket.IO server
        const socket = socketIOClient(ENDPOINT, {
            query: { patientId } // Join room automatically
        });

        // 3. Listen for real-time updates
        socket.on(`new_vitals_${patientId}`, (newRecord) => {
            console.log("Real-time vital received:", newRecord);

            const newDataPoint = {
                time: new Date(newRecord.reading_timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                heart_rate: newRecord.vitals.heart_rate,
            };

            setData((prevData) => {
                // Append new data to the end (right side of chart)
                return [...prevData, newDataPoint];
            });
        });

        // Cleanup on unmount or patient change
        return () => {
            socket.off(`new_vitals_${patientId}`);
            socket.disconnect();
        };
    }, [patientId]);

    if (loading) return <div className="p-4 text-center">Loading Vitals Chart...</div>;
    if (error) return <div className="p-4 text-center text-secondary-red bg-red-900/20 border border-secondary-red rounded-lg">{error}</div>;

    // Determine min/max Y-axis for stability
    const hrValues = data.map(d => d.heart_rate);
    const minHR = Math.min(...hrValues, 60); // Default to reasonable range if empty
    const maxHR = Math.max(...hrValues, 100);

    const yDomainMin = Math.max(0, Math.floor(Math.min(minHR, 50) / 10) * 10 - 10);
    const yDomainMax = Math.ceil(Math.max(maxHR, 100) / 10) * 10 + 10;

    return (
        <div className="h-96 w-full p-4">
            <h3 className="text-xl font-semibold mb-4 text-gray-200">Heart Rate Trend (Real-Time)</h3>
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
                        isAnimationActive={false} // Disable animation for smoother streaming
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default VitalsChart;
