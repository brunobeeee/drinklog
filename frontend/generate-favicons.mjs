import favicons from "favicons";
import fs from "fs/promises";
import path from "path";

const src = "./src/favicon.svg"; // Icon source file path.
const dest = "./dist/favicons"; // Output directory path.
const htmlBasename = "index.html"; // HTML file basename.

// Configuration (see above in the README file).
const configuration = {
  path: "static/favicons",
  appName: "drinklog",
  appDescription: "A habit tracker for tracking water intake",
  lang: "en-US",
  background: "#E6E8F0",
  theme_color: "#E6E8F0",
  start_url: "/",
  shortcuts: [
    // Your applications's Shortcuts (see: https://developer.mozilla.org/docs/Web/Manifest/shortcuts)
    {
      name: "Create new log",
      short_name: "new",
      description: "Create a new drinklog",
      url: "/log-create",
      icon: "./src/favicon.svg",
    },
    {
      name: "View plot",
      short_name: "plot",
      description: "View the plot of your logs",
      url: "/log-plot",
      icon: "./src/favicon.svg",
    },
  ],
};

// Below is the processing.
const response = await favicons(src, configuration);
await fs.mkdir(dest, { recursive: true });
await Promise.all(
  response.images.map(
    async (image) =>
      await fs.writeFile(path.join(dest, image.name), image.contents),
  ),
);
await Promise.all(
  response.files.map(
    async (file) =>
      await fs.writeFile(path.join(dest, file.name), file.contents),
  ),
);
await fs.writeFile(path.join(dest, htmlBasename), response.html.join("\n"));