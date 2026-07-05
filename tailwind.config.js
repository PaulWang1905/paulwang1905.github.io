/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./docs/**/*.html",
    "./docs/page/*.html",
    "./docs/post/*.html",
  ],
  safelist: [], // Add safelisted classes here if needed
  theme: {
    extend: {
      
    },
  },
  plugins: [
    
    require('@tailwindcss/typography'),
    require('daisyui'),
  ],
  daisyui: {
    themes: ["winter", "dark"], // winter = default (light), dark = toggle target
  },
};
