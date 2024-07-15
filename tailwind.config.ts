import flowbitePlugin from 'flowbite/plugin'

import type { Config } from 'tailwindcss';

export default {
	content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {
      colors: {
        // flowbite-svelte
        primary: {
          50: '#eff2fe',
          100: '#e2e6fd',
          200: '#cbd0fa',
          300: '#abb1f6',
          400: '#8282ef',
          500: '#766de7',
          600: '#6651da',
          700: '#5742c0',
          800: '#47389b',
          900: '#3d347b',
          950: '#251e48',
      }
      }
    }
	},

	plugins: [flowbitePlugin]
} as Config;
