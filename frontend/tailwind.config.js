/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'retro-amber': '#F5A623',
        'retro-cream': '#F5F0E8',
        'retro-brown': '#3E2723',
        'retro-dark': '#1C1009',
        'retro-warm': '#8D6E63',
      },
      fontFamily: {
        'retro': ['"Space Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
