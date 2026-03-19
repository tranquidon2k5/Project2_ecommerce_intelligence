/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        shopee: '#EE4D2D',
        tiki: '#0D5CB6',
        lazada: '#0F146D',
      },
    },
  },
  plugins: [],
}
