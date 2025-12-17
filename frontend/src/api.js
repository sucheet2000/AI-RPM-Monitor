const API_BASE_URL = 'http://localhost:5001/api';

/**
 * Generic fetch function for the API.
 * @param {string} endpoint - The API endpoint (e.g., 'vitals/1001?hours=24').
 * @returns {Promise<object>} The JSON response data.
 */
async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API Error ${response.status}: ${errorText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Fetch failed for endpoint:", endpoint, error);
        // Return structure that allows components to display an error state
        return { error: error.message || "Failed to connect to API" };
    }
}

// --- Specific API Calls ---

export const getVitals = (patientId, hours = 24) => {
    return fetchData(`vitals/${patientId}?hours=${hours}&limit=500`);
};

export const getAlerts = (patientId) => {
    return fetchData(`alerts/${patientId}?limit=50`);
};

export const getSummaries = (patientId) => {
    // We only need the latest summary, so limit=1
    return fetchData(`summaries/${patientId}?limit=1`);
};
