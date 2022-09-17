/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
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
  plugins: [],
};
