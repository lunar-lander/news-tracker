/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Pure black theme
        'app-black': '#000000',
        'app-white': '#FFFFFF',
        // Vibrant colors for charts and UI
        primary: '#FF6B6B',
        secondary: '#4ECDC4',
        success: '#95E1D3',
        warning: '#FFD93D',
        danger: '#F38181',
        // Additional chart colors
        'chart-1': '#FF6B6B',
        'chart-2': '#4ECDC4',
        'chart-3': '#FFD93D',
        'chart-4': '#95E1D3',
        'chart-5': '#F38181',
        'chart-6': '#A8E6CF',
        'chart-7': '#FF8B94',
        'chart-8': '#C7CEEA',
      },
    },
  },
  plugins: [],
}
