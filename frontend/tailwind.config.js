/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'primary-blue': '#1e40af',
                'secondary-red': '#dc2626',
                'status-critical': '#b91c1c',
                'status-warning': '#fbbf24',
                'status-normal': '#10b981',
                'dark-bg': '#0f172a',
                'dark-card': '#1e293b',
            },
        },
    },
    plugins: [],
}
