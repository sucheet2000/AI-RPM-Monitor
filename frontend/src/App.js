import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';

function App() {
    // Use a default patient ID to make the app runnable immediately
    const DEFAULT_PATIENT_ID = '1001';

    return (
        <Router>
            <Routes>
                {/* Redirect base URL to the default patient's dashboard */}
                <Route path="/" element={<Navigate replace to={`/dashboard/${DEFAULT_PATIENT_ID}`} />} />

                {/* Main Dashboard View */}
                <Route path="/dashboard/:patientId" element={<Dashboard />} />
            </Routes>
        </Router>
    );
}

export default App;
