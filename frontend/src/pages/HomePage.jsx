import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);
    }, []);

    return (
        <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center relative overflow-hidden font-sans selection:bg-cyan-500 selection:text-white">

            {/* Background Ambient Glow */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-cyan-600/10 rounded-full blur-[100px]"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px]"></div>
            </div>

            <div className={`relative z-10 max-w-6xl px-4 text-center transition-all duration-1000 transform ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>

                {/* Main Title Section */}
                <div className="mb-8">
                    <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-2 drop-shadow-2xl">
                        Welcome to the <br className="md:hidden" />
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 animate-pulse">
                            AI-RPM Monitor
                        </span>
                    </h1>
                    <div className="h-1 w-24 bg-gradient-to-r from-cyan-500 to-blue-500 mx-auto rounded-full mt-6 mb-6"></div>
                </div>

                {/* Subtitle */}
                <p className="text-xl md:text-2xl text-slate-300 mb-12 max-w-3xl mx-auto leading-relaxed font-light">
                    Enterprise-grade Remote Patient Monitoring.
                    <span className="text-cyan-400 font-medium block md:inline md:ml-2">
                        Real-time Kafka Streaming.
                    </span>
                    <span className="text-yellow-400 font-medium block md:inline md:ml-2">
                        GenAI Triage Analysis.
                    </span>
                    <span className="text-emerald-400 font-medium block md:inline md:ml-2">
                        Clinician Intelligence.
                    </span>
                </p>

                {/* CTA Button */}
                <div className="mb-20">
                    <Link
                        to="/dashboard/1001"
                        className="group relative inline-flex items-center justify-center px-10 py-5 text-lg font-bold text-slate-900 transition-all duration-300 bg-cyan-400 rounded-full focus:outline-none focus:ring-4 focus:ring-cyan-500/50 hover:scale-110 hover:bg-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.5)] hover:shadow-[0_0_40px_rgba(34,211,238,0.8)]"
                    >
                        <span className="relative z-10">Launch Dashboard</span>
                        <div className="absolute inset-0 rounded-full bg-white opacity-0 group-hover:animate-ping"></div>
                        <svg className="w-6 h-6 ml-2 transition-transform duration-300 group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                    </Link>
                </div>

                {/* Feature Grid with Staggered Animation */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
                    <FeatureCard
                        isVisible={isVisible}
                        delay="delay-[200ms]"
                        icon="⚡️"
                        title="Real-time Streaming"
                        desc="High-throughput ingestion pipeline powered by Apache Kafka, processing thousands of vital signs per second with At-Least-Once delivery guarantees."
                        color="cyan"
                    />
                    <FeatureCard
                        isVisible={isVisible}
                        delay="delay-[400ms]"
                        icon="🧠"
                        title="LLM-Powered Triage"
                        desc="Integrated Google Gemini 2.0 Pro model automates clinical reasoning, converting raw data into structured, actionable JSON triage reports."
                        color="yellow"
                    />
                    <FeatureCard
                        isVisible={isVisible}
                        delay="delay-[600ms]"
                        icon="🛡️"
                        title="Secure Infrastructure"
                        desc="Production-ready architecture with Docker containerization, separated backend/frontend services, and robust PostgreSQL persistence."
                        color="emerald"
                    />
                </div>

                <div className="mt-16 text-slate-500 text-sm font-mono">
                    System Status: <span className="text-emerald-500">● Online</span> | v1.0.0-stable
                </div>
            </div>
        </div>
    );
};

const FeatureCard = ({ icon, title, desc, delay, isVisible, color }) => {
    // Dynamic border color class based on prop
    const borderClass = {
        cyan: 'hover:border-cyan-500/50 group-hover:shadow-[0_0_20px_rgba(6,182,212,0.2)]',
        yellow: 'hover:border-yellow-500/50 group-hover:shadow-[0_0_20px_rgba(234,179,8,0.2)]',
        emerald: 'hover:border-emerald-500/50 group-hover:shadow-[0_0_20px_rgba(16,185,129,0.2)]'
    }[color];

    return (
        <div className={`group p-8 bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl transition-all duration-1000 transform hover:-translate-y-2 ${isVisible ? `opacity-100 translate-y-0 ${delay}` : 'opacity-0 translate-y-12'} ${borderClass}`}>
            <div className="text-4xl mb-6 bg-slate-900/50 w-16 h-16 flex items-center justify-center rounded-xl border border-slate-700 shadow-inner">
                {icon}
            </div>
            <h3 className="text-xl font-bold text-white mb-3 group-hover:text-cyan-400 transition-colors">{title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
        </div>
    );
};

export default HomePage;
