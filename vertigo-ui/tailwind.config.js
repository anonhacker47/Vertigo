/** @type {import('tailwindcss').Config} */
module.exports = {
 content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
 safelist: [
  'grid-cols-3',
  'grid-cols-4',
  'grid-cols-5',
  'grid-cols-6',
  'grid-cols-7',
 ],
  theme: {
    extend: {
      keyframes: {
        shake: {
          "0%": { transform: "rotate(-1deg)" },
          "50%": { transform: "rotate(1.5deg)" },
        },
        wiggle: {
          '0%': { transform: 'rotate(-1deg)' },
          '50%': { transform: 'rotate(1.5deg)' },
        }
      },
    },
    animation: {
      iosshake: "shake linear infinite",
      wiggle: 'wiggle .3s ease-in-out infinite',
    },
  },
  plugins: [require('daisyui')],
};
