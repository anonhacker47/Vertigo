/** @type {import('tailwindcss').Config} */
module.exports = {
 content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
 safelist: [
  'grid-cols-2',
  'grid-cols-3',
  'grid-cols-4',
  'grid-cols-5',
  'grid-cols-6',
  'grid-cols-7',
  'grid-cols-8',
  'grid-cols-9',
  'grid-cols-10',

  'opacity-50',

  'md:h-[70vh]',
  'md:h-[55vh]',
  'md:h-[50vh]',
  'md:h-[48vh]',
  'md:h-[42vh]',
  'md:h-[38vh]',
  'md:h-[35vh]',
  'md:h-[32vh]',
  'md:w-[20vw]',
  'md:w-[23vw]',
  'md:w-[22vw]',
  'md:w-[18vw]',
  'md:w-[16vw]',
  'md:w-[12vw]',
  'md:w-[10vw]',
  'md:w-[10vw]',
  'md:max-w-[12vw]',
  'md:max-w-[8vw]',
  'md:max-w-[6vw]',
  'md:max-w-[5vw]',
  'md:max-w-[10vw]',

  'h-[35vh]',
  'h-[25vh]',
  'h-[50vh]',
  'h-[48vh]',
  'h-[42vh]',
  'h-[38vh]',
  'h-[35vh]',
  'h-[32vh]',
  'w-[80vw]',
  'w-[75vw]',
  'w-[16vw]',
  'w-[12vw]',
  'w-[10vw]',
  'max-w-[40vw]',
  `max-w-[${75/2}vw]`,
  'max-w-[8vw]',
  'max-w-[6vw]',
  'max-w-[5vw]',
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
  daisyui: {
    themes: [
      {
        night: {
          ...require("daisyui/src/colors/themes")["[data-theme=night]"],
          accent: "#4ade80",
        },
      },
    ],
  },
};
