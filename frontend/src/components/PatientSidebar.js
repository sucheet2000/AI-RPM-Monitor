import React from 'react';
import { NavLink, useParams } from 'react-router-dom';

const PatientSidebar = () => {
    const { patientId } = useParams();
    const patients = ['1001', '1002', '1003'];

    return (
        <aside className="fixed top-0 left-0 w-64 h-full bg-slate-800 border-r border-slate-700 shadow-xl z-20 pt-20">
            <div className="px-6 mb-8">
                <h2 className="text-xl font-bold text-white tracking-wide">
                    Patient List
                </h2>
                <p className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">
                    Live Monitoring
                </p>
            </div>

            <nav className="px-4 space-y-2">
                {patients.map((id) => (
                    <NavLink
                        key={id}
                        to={`/dashboard/${id}`}
                        className={({ isActive }) =>
                            `flex items-center px-4 py-3 rounded-lg transition-all duration-200 group ${isActive
                                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_15px_rgba(6,182,212,0.1)]'
                                : 'text-slate-400 hover:bg-slate-700/50 hover:text-white border border-transparent'
                            }`
                        }
                    >
                        <div className={`w-2 h-2 rounded-full mr-3 ${id === patientId ? 'bg-cyan-400 animate-pulse' : 'bg-slate-600'}`}></div>
                        <span className="font-medium">Patient {id}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="absolute bottom-8 left-0 w-full px-6">
                <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
                    <p className="text-xs text-slate-500 text-center">
                        AI-RPM Monitor v1.0 <br />
                        <span className="text-emerald-500/80">● System Health: Good</span>
                    </p>
                </div>
            </div>
        </aside>
    );
};

export default PatientSidebar;
