import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        glow: "var(--glow)",
        warning: "var(--warning)",
        text: "var(--text)",
        muted: "var(--muted)",
        "organism-membrane": "var(--organism-membrane)",
      },
      fontFamily: {
        bebas: ["var(--font-bebas)", "sans-serif"],
        jetbrains: ["var(--font-jetbrains)", "monospace"],
        space: ["var(--font-space)", "monospace"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;
