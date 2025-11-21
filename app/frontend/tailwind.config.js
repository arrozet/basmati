/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'basmati-yellow': '#EBBE4D',
        'basmati-bg': '#FFFAEB',
        'basmati-black': '#1A1A1A',
        'basmati-blue': '#5496FF',
        'basmati-red': '#FF6B6B',
        'basmati-green': '#4ECDC4',
      },
      borderWidth: {
        '3': '3px',
      },
      boxShadow: {
        'hard': '4px 4px 0px 0px rgba(26,26,26,1)',
      }
    },
  },
  plugins: [],
}

