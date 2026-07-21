/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        dreamco: {
          dark: '#0f172a',
          card: '#1e293b',
          accent: '#6366f1',
          green: '#22c55e',
          red: '#ef4444',
          yellow: '#f59e0b',
        },
      },
    },
  },
  plugins: [],
};
