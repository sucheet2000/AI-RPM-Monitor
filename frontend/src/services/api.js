/**
 * API Service for communicating with the backend.
 */

const API_BASE_URL = '/api';

/**
 * Fetch patient vitals for the last N hours.
 * @param {string} patientId - Patient identifier
 * @param {number} hours - Hours of data to fetch (default: 24)
 * @returns {Promise<Object>} Vitals data
 */
export async function fetchVitals(patientId, hours = 24) {
    const response = await fetch(`${API_BASE_URL}/vitals/${patientId}?hours=${hours}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch vitals: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch critical alerts for a patient.
 * @param {string} patientId - Patient identifier
 * @returns {Promise<Object>} Alerts data
 */
export async function fetchAlerts(patientId) {
    const response = await fetch(`${API_BASE_URL}/alerts/${patientId}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch alerts: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch LLM summaries for a patient.
 * @param {string} patientId - Patient identifier
 * @returns {Promise<Object>} Summaries data
 */
export async function fetchSummaries(patientId) {
    const response = await fetch(`${API_BASE_URL}/summaries/${patientId}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch summaries: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Fetch system-wide statistics.
 * @returns {Promise<Object>} Stats data
 */
export async function fetchStats() {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) {
        throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    return response.json();
}
