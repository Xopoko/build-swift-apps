#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import sharp from "sharp";

const PRESETS = {
  iphone: { width: 1284, height: 2778, panels: 3 },
  ipad: { width: 2048, height: 2732, panels: 3 },
};

function parseArgs(argv) {
  const args = { device: "iphone", outputDir: ".appstore-screenshots/panels", prefix: "panel" };
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key === "--input") args.input = value, i += 1;
    else if (key === "--device") args.device = value, i += 1;
    else if (key === "--output-dir") args.outputDir = value, i += 1;
    else if (key === "--prefix") args.prefix = value, i += 1;
    else if (key === "--help" || key === "-h") args.help = true;
    else throw new Error(`Unknown argument: ${key}`);
  }
  return args;
}

function usage() {
  console.log(`Usage: crop.mjs --input composite.png [--device iphone|ipad] [--output-dir DIR] [--prefix NAME]`);
}

const args = parseArgs(process.argv.slice(2));
if (args.help) {
  usage();
  process.exit(0);
}
if (!args.input) {
  usage();
  throw new Error("--input is required");
}

const preset = PRESETS[args.device];
if (!preset) throw new Error(`Unknown device preset: ${args.device}`);

const input = path.resolve(args.input);
const outputDir = path.resolve(args.outputDir);
await fs.mkdir(outputDir, { recursive: true });

const image = sharp(input);
const meta = await image.metadata();
if (!meta.width || !meta.height) throw new Error(`Could not read dimensions for ${input}`);

const cropWidth = Math.floor(meta.width / preset.panels);
const outputs = [];
for (let index = 0; index < preset.panels; index += 1) {
  const left = index * cropWidth;
  const width = index === preset.panels - 1 ? meta.width - left : cropWidth;
  const filename = `${args.prefix}-${String(index + 1).padStart(2, "0")}.png`;
  const output = path.join(outputDir, filename);
  await sharp(input)
    .extract({ left, top: 0, width, height: meta.height })
    .resize(preset.width, preset.height, { fit: "cover", position: "center" })
    .png()
    .toFile(output);
  outputs.push({ file: output, width: preset.width, height: preset.height });
}

console.log(JSON.stringify({ input, device: args.device, outputs }, null, 2));
