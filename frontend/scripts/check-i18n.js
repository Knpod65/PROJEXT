const fs = require('fs');
const path = require('path');

function readFile(p) {
  try {
    return fs.readFileSync(p, 'utf8');
  } catch (err) {
    console.error('Failed to read', p, err.message);
    process.exit(2);
  }
}

function extractKeys(text) {
  // crude extraction: match quoted keys before a colon
  const re = /['"`]()([^'"`]+?)['"`]\s*:/g;
  // fallback regex simpler
  const re2 = /['"`]([^'"`]+?)['"`]\s*:/g;
  const keys = new Set();
  let m;
  while ((m = re2.exec(text)) !== null) {
    keys.add(m[1]);
  }
  return keys;
}

const enPath = path.resolve(__dirname, '../src/i18n/en.ts');
const thPath = path.resolve(__dirname, '../src/i18n/th.ts');

const enText = readFile(enPath);
const thText = readFile(thPath);

const enKeys = extractKeys(enText);
const thKeys = extractKeys(thText);

const missingInTh = [...enKeys].filter(k => !thKeys.has(k)).sort();
const missingInEn = [...thKeys].filter(k => !enKeys.has(k)).sort();

console.log('i18n keys: en=', enKeys.size, ' th=', thKeys.size);
if (missingInTh.length === 0 && missingInEn.length === 0) {
  console.log('OK: en/th key sets are identical (by simple heuristic)');
  process.exit(0);
}

if (missingInTh.length) {
  console.log('\nKeys present in en.ts but missing in th.ts:');
  missingInTh.slice(0, 200).forEach(k => console.log('  ', k));
}
if (missingInEn.length) {
  console.log('\nKeys present in th.ts but missing in en.ts:');
  missingInEn.slice(0, 200).forEach(k => console.log('  ', k));
}

process.exit(1);
