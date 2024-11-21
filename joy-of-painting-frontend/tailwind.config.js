/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bob-ross-blue': '#4B8BC8',
        'bob-ross-brown': '#6E4434',
        'bob-ross-green': '#4E753E',
      }
    },
  },
  plugins: [],
}