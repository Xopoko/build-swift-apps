#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

function parseArgs(argv) {
  const args = { outputDir: ".appstore-screenshots/scraped" };
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key === "--url") args.url = value, i += 1;
    else if (key === "--output-dir") args.outputDir = value, i += 1;
    else if (key === "--help" || key === "-h") args.help = true;
    else throw new Error(`Unknown argument: ${key}`);
  }
  return args;
}

function usage() {
  console.log("Usage: scrape.mjs --url APP_STORE_URL [--output-dir .appstore-screenshots/scraped]");
}

function appStoreId(url) {
  const match = String(url).match(/\/id(\d+)/);
  return match?.[1] ?? null;
}

const args = parseArgs(process.argv.slice(2));
if (args.help) {
  usage();
  process.exit(0);
}
if (!args.url) {
  usage();
  throw new Error("--url is required");
}

const id = appStoreId(args.url);
if (!id) throw new Error("Only App Store URLs containing /id<digits> are supported by this helper.");

const response = await fetch(`https://itunes.apple.com/lookup?id=${id}`);
if (!response.ok) throw new Error(`Lookup failed: ${response.status} ${response.statusText}`);
const data = await response.json();

await fs.mkdir(args.outputDir, { recursive: true });
const output = path.resolve(args.outputDir, `app-store-${id}.json`);
await fs.writeFile(output, `${JSON.stringify(data, null, 2)}\n`);
console.log(JSON.stringify({ output, resultCount: data.resultCount ?? 0 }, null, 2));
