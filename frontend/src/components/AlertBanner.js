import React, { useState, useEffect } from 'react';
import { getAlerts } from '../api';

const AlertBanner = ({ patientId, onAlertClick }) => {
    const [alertCount, setAlertCount] = useState(0);
    const [loading, setLoading] = useState(true);

    const fetchAlerts = async () => {
        try {
            const result = await getAlerts(patientId);
            if (result.error) {
                // Do not throw, just log and set count to 0
                console.warn("API warning: Could not fetch alerts:", result.error);
                setAlertCount(0);
            } else {
                setAlertCount(result.count);
            }
        } catch (err) {
            console.error("Critical error fetching alerts:", err);
            setAlertCount(0);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Initial fetch and 10-second polling to detect new alerts
        fetchAlerts();
        const intervalId = setInterval(fetchAlerts, 10000);

        return () => clearInterval(intervalId);
    }, [patientId]);

    if (loading || alertCount === 0) return null;

    // Requirement 4: Prominent, sticky RED Alert Banner
    return (
        <div
            className="fixed top-0 left-0 right-0 z-40 bg-status-critical text-white p-3 shadow-2xl cursor-pointer hover:bg-red-700 transition duration-300"
            onClick={onAlertClick}
        >
            <div className="max-w-7xl mx-auto flex justify-between items-center font-bold">
                <span className="text-lg animate-pulse">
                    🚨 URGENT: {alertCount} CRITICAL VITAL ALERT{alertCount > 1 ? 'S' : ''} DETECTED FOR PATIENT {patientId} 🚨
                </span>
                <span className="text-sm border border-white px-2 py-1 rounded-full">
                    VIEW TRIAGE REPORT
                </span>
            </div>
        </div>
    );
};

export default AlertBanner;
