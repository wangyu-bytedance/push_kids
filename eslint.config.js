module.exports = [
  {
    files: ["apps/miniprogram/**/*.js", "tests/frontend/**/*.js"],
    languageOptions: { ecmaVersion: 2021, sourceType: "commonjs" },
    rules: {
      "no-undef": "off",
      "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
      "eqeqeq": "error",
      "semi": ["error", "always"]
    }
  }
];
