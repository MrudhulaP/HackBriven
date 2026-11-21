/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          900: '#081C15',
          800: '#1B4332',
          700: '#2D6A4F',
          600: '#40916C',
          500: '#52B788',
          400: '#74C69D',
          300: '#95D5B2',
          200: '#D8F3DC',
        },
        cream: {
          50: '#FDFCF7',
          100: '#F8F6F0',
          200: '#EFECE2',
          300: '#E2DEC6',
        },
        charcoal: {
          900: '#191C1A',
          800: '#2C312E',
          700: '#404642',
          600: '#5B625E',
          500: '#78807B',
        },
        terracotta: {
          500: '#E07A5F',
          600: '#D06042',
        },
        amberGold: {
          500: '#F4A261',
          600: '#E76F51',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'sound-wave': 'soundWave 1.2s ease-in-out infinite alternate',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { transform: 'scale(1)', boxShadow: '0 0 0 0 rgba(45, 106, 79, 0.4)' },
          '50%': { transform: 'scale(1.05)', boxShadow: '0 0 0 16px rgba(45, 106, 79, 0)' },
        },
        soundWave: {
          '0%': { height: '12%' },
          '100%': { height: '100%' },
        }
      }
    },
  },
  plugins: [],
}
