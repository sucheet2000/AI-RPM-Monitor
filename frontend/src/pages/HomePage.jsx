/**
 * Home Page Component
 * 
 * Landing page showing system overview and patient selection.
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchStats } from '../services/api';

export default function HomePage() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [patientInput, setPatientInput] = useState('');

    useEffect(() => {
        fetchStats()
            .then(setStats)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    // Demo patient IDs for quick access
    const demoPatients = [
        'patient-demo001',
        'patient-demo002',
        'patient-demo003'
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            {/* Hero Header */}
            <header className="border-b border-gray-700/50 backdrop-blur-sm bg-gray-900/50">
                <div className="max-w-7xl mx-auto px-4 py-8">
                    <div className="flex items-center gap-4 mb-2">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
                            <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                                />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-white">
                                AI RPM Monitor
                            </h1>
                            <p className="text-gray-400">
                                Real-time Remote Patient Monitoring with AI-Powered Analytics
                            </p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 py-8">
                {/* Stats Overview */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <StatsCard
                        title="Total Records"
                        value={stats?.total_records || 0}
                        icon="📊"
                        loading={loading}
                    />
                    <StatsCard
                        title="Active Patients"
                        value={stats?.patient_count || 0}
                        icon="👥"
                        loading={loading}
                    />
                    <StatsCard
                        title="Critical Alerts"
                        value={stats?.by_state?.Critical || 0}
                        icon="🔴"
                        loading={loading}
                        highlight={stats?.by_state?.Critical > 0}
                    />
                    <StatsCard
                        title="Normal Readings"
                        value={stats?.by_state?.Normal || 0}
                        icon="✅"
                        loading={loading}
                    />
                </div>

                {/* Patient Search */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700/50 p-6 mb-8">
                    <h2 className="text-xl font-semibold text-white mb-4">Patient Dashboard</h2>
                    <div className="flex gap-4">
                        <input
                            type="text"
                            value={patientInput}
                            onChange={(e) => setPatientInput(e.target.value)}
                            placeholder="Enter Patient ID (e.g., patient-abc12345)"
                            className="flex-1 bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                        />
                        <Link
                            to={patientInput ? `/dashboard/${patientInput}` : '#'}
                            className={`px-6 py-3 rounded-lg font-medium transition-all ${patientInput
                                    ? 'bg-primary-500 hover:bg-primary-600 text-white'
                                    : 'bg-gray-700 text-gray-400 cursor-not-allowed'
                                }`}
                        >
                            View Dashboard
                        </Link>
                    </div>
                </div>

                {/* Demo Patients */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700/50 p-6">
                    <h2 className="text-xl font-semibold text-white mb-4">Quick Access</h2>
                    <p className="text-gray-400 text-sm mb-4">
                        Select a demo patient to view the monitoring dashboard:
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {demoPatients.map((patientId) => (
                            <Link
                                key={patientId}
                                to={`/dashboard/${patientId}`}
                                className="bg-gray-700/50 hover:bg-gray-700 border border-gray-600 hover:border-primary-500/50 rounded-lg p-4 transition-all group"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-primary-500/20 rounded-full flex items-center justify-center">
                                        <svg className="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                                            />
                                        </svg>
                                    </div>
                                    <div>
                                        <p className="text-white font-medium group-hover:text-primary-400 transition-colors">
                                            {patientId}
                                        </p>
                                        <p className="text-gray-500 text-sm">View vitals →</p>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                </div>

                {/* System Status */}
                <div className="mt-8 flex items-center justify-center gap-6 text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span>System Online</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span>Kafka Connected</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                        <span>PostgreSQL Active</span>
                    </div>
                </div>
            </main>
        </div>
    );
}

function StatsCard({ title, value, icon, loading, highlight = false }) {
    return (
        <div className={`bg-gray-800/50 backdrop-blur-sm rounded-xl border p-6 transition-all ${highlight ? 'border-red-500/50 bg-red-500/5' : 'border-gray-700/50'
            }`}>
            {loading ? (
                <div className="animate-pulse">
                    <div className="h-4 bg-gray-700 rounded w-20 mb-2"></div>
                    <div className="h-8 bg-gray-700 rounded w-16"></div>
                </div>
            ) : (
                <>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400 text-sm">{title}</span>
                        <span className="text-2xl">{icon}</span>
                    </div>
                    <p className={`text-3xl font-bold ${highlight ? 'text-red-400' : 'text-white'}`}>
                        {typeof value === 'number' ? value.toLocaleString() : value}
                    </p>
                </>
            )}
        </div>
    );
}
