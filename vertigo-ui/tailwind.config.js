/** @type {import('tailwindcss').Config} */
module.exports = {
  purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
 content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}","./presets/**/*.{js,vue,ts}",],
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
  'md:h-[34rem]',
  'md:h-[32rem]',
  'md:h-[27rem]',
  'md:h-[21.5rem]',
  'md:h-[19rem]',
  'md:h-[16.3rem]',
  'md:h-[14rem]',
  'md:h-[13.5rem]',

  'md:w-[22rem]',
  'md:w-[21rem]',
  'md:w-[17.5rem]',
  'md:w-[14rem]',
  'md:w-[12rem]',
  'md:w-[10.5rem]', 
  'md:w-[9.2rem]',
  'md:w-[9.2rem]',,

  'h-[19rem]',
  'h-[14rem]',
  'h-[9rem]',
  'h-[7.5rem]',
  'h-[42rem]',
  'h-[38rem]',
  'h-[35rem]',
  'h-[32rem]',
  'w-[12rem]',
  'w-[9.2rem]',
  'w-[6rem]',
  'w-[5rem]',
  'w-[10rem]',
  'max-w-[40rem]',
  `max-w-[${75/2}rem]`,
  'max-w-[8rem]',
  'max-w-[6rem]',
  'max-w-[5rem]',
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
          ...require("daisyui/src/theming/themes")["night"],
          accent: "#4ade80",
        },
      },
    ],
  },
};
