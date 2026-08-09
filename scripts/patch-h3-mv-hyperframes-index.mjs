#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";

const project = process.argv[2];
if (!project) throw new Error("usage: node patch-h3-mv-hyperframes-index.mjs <project-dir>");
const path = `${project}/index.html`;
let html = readFileSync(path, "utf8");

const rootStyle = '      #root { position: relative; width: 1280px; height: 704px; overflow: hidden; }';
const styledRoot = `${rootStyle}\n      .bg-video { position: absolute; inset: 0; z-index: 0; width: 100%; height: 100%; object-fit: cover; }`;
if (!html.includes('.bg-video {')) {
  if (!html.includes(rootStyle)) throw new Error('root style marker not found');
  html = html.replace(rootStyle, styledRoot);
}

const marker = '      <div\n        id="el-01-f01-rooftop"';
const background = `      <video\n        id="h3-mv-plate"\n        class="bg-video clip"\n        src="assets/h3_jpop_mv_5segment_keyint30.mp4"\n        data-start="0"\n        data-duration="29.256"\n        data-track-index="0"\n        muted\n        playsinline\n        preload="auto"\n      ></video>\n\n`;
if (!html.includes('id="h3-mv-plate"')) {
  if (!html.includes(marker)) throw new Error("frame host marker not found");
  html = html.replace(marker, `${background}${marker}`);
}
writeFileSync(path, html);
console.log(`✓ patched ${path} with the H3 MV video plate`);
