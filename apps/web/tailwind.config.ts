import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        panel: "#f7f8fb",
        line: "#d8dee8",
        accent: "#0f766e",
        danger: "#b42318",
        warning: "#b54708"
      }
    }
  },
  plugins: []
};

export default config;
