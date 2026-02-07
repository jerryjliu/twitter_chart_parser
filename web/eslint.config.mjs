/** @type {import("eslint").Linter.Config[]} */
const config = [
  {
    files: ["src/**/*.{ts,tsx}"],
    rules: {
      "no-console": "warn",
    },
  },
];

export default config;
