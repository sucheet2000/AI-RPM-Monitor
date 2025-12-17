import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-4">
            <div className="max-w-2xl text-center space-y-8">
                {/* Hero Section */}
                <h1 className="text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-teal-400">
                    Welcome to the AI-RPM Monitor
                </h1>

                <p className="text-xl text-gray-400 leading-relaxed">
                    Advanced Remote Patient Monitoring powered by Artificial Intelligence.
                    Real-time vital signs analysis, automated triage, and critical alert detection
                    for healthcare providers.
                </p>

                {/* Call to Action */}
                <div className="mt-10">
                    <Link
                        to="/dashboard/1001"
                        className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-lg text-white bg-status-normal hover:bg-emerald-600 transition-all duration-200 shadow-lg hover:shadow-emerald-500/30 transform hover:-translate-y-1"
                    >
                        Launch Dashboard
                    </Link>
                </div>

                {/* Features / Footer hint */}
                <div className="pt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-500 border-t border-gray-800">
                    <div className="flex flex-col items-center">
                        <span className="text-2xl mb-2">⚡️</span>
                        <p>Real-time Kafka Streaming</p>
                    </div>
                    <div className="flex flex-col items-center">
                        <span className="text-2xl mb-2">🤖</span>
                        <p>LLM-Powered Triage</p>
                    </div>
                    <div className="flex flex-col items-center">
                        <span className="text-2xl mb-2">🏥</span>
                        <p>Clinical Decision Support</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HomePage;
