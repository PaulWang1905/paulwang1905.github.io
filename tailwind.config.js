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
    themes: ["winter", "light", "dark"], // Include your desired themes
  },
};
