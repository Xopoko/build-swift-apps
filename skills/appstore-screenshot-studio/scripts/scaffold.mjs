#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

function parseArgs(argv) {
  const args = { outputDir: ".appstore-screenshots" };
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key === "--output-dir") args.outputDir = value, i += 1;
    else if (key === "--help" || key === "-h") args.help = true;
    else throw new Error(`Unknown argument: ${key}`);
  }
  return args;
}

function usage() {
  console.log("Usage: scaffold.mjs [--output-dir .appstore-screenshots]");
}

const args = parseArgs(process.argv.slice(2));
if (args.help) {
  usage();
  process.exit(0);
}

const root = path.resolve(args.outputDir);
const dirs = ["composites", "panels", "scraped", "sources", "review"].map((dir) => path.join(root, dir));
await fs.mkdir(root, { recursive: true });
for (const dir of dirs) await fs.mkdir(dir, { recursive: true });

const configPath = path.join(root, "config.json");
const manifestPath = path.join(root, "manifest.json");

async function writeIfMissing(file, data) {
  try {
    await fs.access(file);
  } catch {
    await fs.writeFile(file, `${JSON.stringify(data, null, 2)}\n`);
  }
}

await writeIfMissing(configPath, {
  appName: "",
  appStoreUrl: "",
  devices: ["iphone"],
  locales: ["en-US"],
  panelCount: 3,
  brandColors: [],
  benefits: [],
  notes: "",
});

await writeIfMissing(manifestPath, {
  version: 1,
  assets: [],
});

console.log(JSON.stringify({ workspace: root, config: configPath, manifest: manifestPath }, null, 2));
