import { cpSync, existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const projectRoot = resolve(process.cwd());
const sourceDir = resolve(projectRoot, "sw");
const targetDir = resolve(projectRoot, "public", "sw");

if (!existsSync(sourceDir)) {
  console.error(`Missing source service-worker directory: ${sourceDir}`);
  process.exit(1);
}

mkdirSync(resolve(projectRoot, "public"), { recursive: true });
if (existsSync(targetDir)) {
  rmSync(targetDir, { recursive: true, force: true });
}

cpSync(sourceDir, targetDir, { recursive: true });
const wrapperPath = resolve(projectRoot, "public", "sw.js");
writeFileSync(wrapperPath, 'import "./sw/sw.js";\n');

console.log(`Synced service worker files: ${sourceDir} -> ${targetDir}`);
console.log(`Generated service worker wrapper: ${wrapperPath}`);
