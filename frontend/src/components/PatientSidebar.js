import React, { useState, useMemo } from 'react';
import { NavLink, useParams } from 'react-router-dom';

// Generate 50 mock patients
const MOCK_PATIENTS = Array.from({ length: 50 }, (_, i) => {
    const id = (1001 + i).toString();
    const names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"];
    const firstNames = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth"];
    const randomName = `${firstNames[i % firstNames.length]} ${names[i % names.length]}`;

    // Special case for our demo high-risk patients
    let label = `${randomName}`;
    if (id === '1003') label += " (High Risk)";

    return { id, name: label };
});

const PatientSidebar = () => {
    const { patientId } = useParams();
    const [searchTerm, setSearchTerm] = useState('');

    // Filter patients based on search term
    const filteredPatients = useMemo(() => {
        if (!searchTerm) return MOCK_PATIENTS;
        const lowerTerm = searchTerm.toLowerCase();
        return MOCK_PATIENTS.filter(p =>
            p.id.includes(lowerTerm) ||
            p.name.toLowerCase().includes(lowerTerm)
        );
    }, [searchTerm]);

    return (
        <aside className="fixed top-0 left-0 w-64 h-full bg-slate-900 border-r border-slate-800 shadow-xl z-20 flex flex-col">
            {/* Header */}
            <div className="p-6 border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm">
                <h2 className="text-xl font-bold text-white tracking-wide">
                    Patient List
                </h2>
                <p className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">
                    Live Monitoring
                </p>

                {/* Search Input */}
                <div className="mt-4 relative">
                    <input
                        type="text"
                        placeholder="Search ID or Name..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full bg-slate-800 text-slate-200 text-sm rounded-lg pl-9 pr-3 py-2 border border-slate-700 
                                 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 placeholder-slate-500 transition-all"
                    />
                    <svg className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
            </div>

            {/* Scrollable List */}
            <nav className="flex-1 overflow-y-auto py-2 px-3 space-y-1 custom-scrollbar">
                {filteredPatients.length > 0 ? (
                    filteredPatients.map((patient) => (
                        <NavLink
                            key={patient.id}
                            to={`/dashboard/${patient.id}`}
                            className={({ isActive }) =>
                                `flex items-center px-3 py-2.5 rounded-lg transition-all duration-200 group text-sm ${isActive
                                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_15px_rgba(6,182,212,0.1)]'
                                    : 'text-slate-400 hover:bg-slate-800 hover:text-white border border-transparent'
                                }`
                            }
                        >
                            <div className={`w-2 h-2 rounded-full mr-3 flex-shrink-0 ${patient.id === patientId ? 'bg-cyan-400 animate-pulse' : 'bg-slate-600'}`}></div>
                            <div className="flex flex-col truncate">
                                <span className="font-medium truncate">{patient.name}</span>
                                <span className="text-xs opacity-70">ID: {patient.id}</span>
                            </div>
                        </NavLink>
                    ))
                ) : (
                    <div className="text-center py-8 text-slate-500 text-sm">
                        No patients found
                    </div>
                )}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/90">
                <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50">
                    <p className="text-[10px] text-slate-500 text-center uppercase tracking-wide">
                        System Status: <span className="text-emerald-500 font-bold">Online</span>
                    </p>
                </div>
            </div>
        </aside>
    );
};

export default PatientSidebar;
