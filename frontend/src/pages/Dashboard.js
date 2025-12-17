import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import VitalsChart from '../components/VitalsChart';
import AlertBanner from '../components/AlertBanner';
import TriageModal from '../components/TriageModal';
import ReportCard from '../components/ReportCard';
import PatientSidebar from '../components/PatientSidebar';

const Dashboard = () => {
    const { patientId } = useParams();
    const [isModalOpen, setIsModalOpen] = useState(false);

    return (
        <div className="min-h-screen bg-slate-900">
            <PatientSidebar />

            <div className="ml-64 pt-16 transition-all duration-300">
                <AlertBanner
                    patientId={patientId}
                    onAlertClick={() => setIsModalOpen(true)}
                />

                <TriageModal
                    patientId={patientId}
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                />

                <header className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <h1 className="text-4xl font-extrabold text-white">
                        Patient {patientId} Monitoring Dashboard
                    </h1>
                    <p className="text-gray-400 mt-1">Real-time Vitals and AI Triage System</p>
                </header>

                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-10">
                    {/* Top Section: Charts and Reports */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                        {/* Report Card (1/3 width) */}
                        <div className="lg:col-span-1">
                            <ReportCard patientId={patientId} />
                        </div>

                        {/* Vitals Chart (2/3 width) */}
                        <div className="lg:col-span-2 bg-dark-card rounded-lg shadow-xl border border-gray-700">
                            <VitalsChart patientId={patientId} />
                        </div>
                    </div>

                    {/* Bottom Section: Raw Alert List (Placeholder for future expansion) */}
                    <div className="bg-dark-card p-6 rounded-lg shadow-xl border border-gray-700">
                        <h2 className="text-2xl font-bold mb-4 text-gray-200">Recent Critical Events Log</h2>
                        <p className="text-gray-400">
                            Detailed log of all critical vital records is available here via the
                            <code className="bg-gray-700 p-1 rounded">/api/alerts/{patientId}</code> endpoint.
                        </p>
                        {/* In a real app, this would be a list/table of the VitalsRecord data */}
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Dashboard;
