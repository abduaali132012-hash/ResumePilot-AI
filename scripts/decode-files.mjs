/**
 * Decode .b64 files into public/ so Vite serves them at build & dev time.
 * Run with: node scripts/decode-files.mjs
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, '..');
const publicDir = join(root, 'public');

const files = [
  ['ResumePilot_AI_Presentation.pptx.b64', 'ResumePilot_AI_Presentation.pptx'],
  ['ResumePilot_AI_Presentation.pdf.b64',   'ResumePilot_AI_Presentation.pdf'],
  ['ResumePilot_AI_Source_Code.zip.b64',    'ResumePilot_AI_Source_Code.zip'],
  ['README.pdf.b64',                         'README.pdf'],
];

if (!existsSync(publicDir)) mkdirSync(publicDir, { recursive: true });

let count = 0;
for (const [b64Name, outputName] of files) {
  const b64Path = join(root, b64Name);
  if (!existsSync(b64Path)) {
    console.warn(`⚠️  Missing: ${b64Name}`);
    continue;
  }
  const encoded = readFileSync(b64Path, 'utf-8').trim();
  const decoded = Buffer.from(encoded, 'base64');
  const outPath = join(publicDir, outputName);
  writeFileSync(outPath, decoded);
  console.log(`✅ ${b64Name} → public/${outputName} (${decoded.length} bytes)`);
  count++;
}

console.log(`\nDone — ${count} file(s) decoded into public/`);