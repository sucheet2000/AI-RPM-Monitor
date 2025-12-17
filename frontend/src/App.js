import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import Dashboard from './pages/Dashboard';

function App() {
    // Use a default patient ID to make the app runnable immediately
    const DEFAULT_PATIENT_ID = '1001';

    return (
        <Router>
            <Routes>
                {/* Landing Page */}
                <Route path="/" element={<HomePage />} />

                {/* Main Dashboard View */}
                <Route path="/dashboard/:patientId" element={<Dashboard />} />
            </Routes>
        </Router>
    );
}

export default App;
