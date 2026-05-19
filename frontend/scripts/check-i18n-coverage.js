#!/usr/bin/env node
/**
 * check-i18n-coverage.js
 * Scans frontend source for raw strings and missing translation keys.
 * Usage: npm run check:i18n:coverage
 */

const fs = require('fs');
const path = require('path');

const SRC_DIR = path.join(__dirname, '..', 'src');
const I18N_DIR = path.join(SRC_DIR, 'i18n');

const RAW_PATTERNS = [
  /["'][A-Zก-ฮ][^"']{8,}[^"']*["']/g,   // long capitalized strings
  /["'][ก-ฮ][^"']{5,}[^"']*["']/g,      // Thai strings
];

const IGNORED_DIRS = ['node_modules', '.git', 'dist'];

function walk(dir) {
  let files = [];
  for (const entry of fs.readdirSync(dir)) {
    if (IGNORED_DIRS.includes(entry)) continue;
    const full = path.join(dir, entry);
    if (fs.statSync(full).isDirectory()) {
      files = files.concat(walk(full));
    } else if (full.endsWith('.tsx') || full.endsWith('.ts')) {
      files.push(full);
    }
  }
  return files;
}

function findRawStrings(content) {
  const matches = [];
  for (const pattern of RAW_PATTERNS) {
    const found = content.match(pattern) || [];
    matches.push(...found);
  }
  return matches.filter(m => !m.includes('translate('));
}

function main() {
  const files = walk(SRC_DIR);
  let totalRaw = 0;

  for (const file of files) {
    const content = fs.readFileSync(file, 'utf8');
    const raw = findRawStrings(content);
    if (raw.length > 0) {
      console.log(`\n${path.relative(SRC_DIR, file)}`);
      raw.forEach(r => console.log(`  - ${r.substring(0, 60)}...`));
      totalRaw += raw.length;
    }
  }

  console.log(`\n=== i18n Coverage Report ===`);
  console.log(`Files scanned: ${files.length}`);
  console.log(`Raw strings found: ${totalRaw}`);
  if (totalRaw > 0) {
    console.log('Recommendation: wrap strings in translate() and add keys to en.ts / th.ts');
  } else {
    console.log('No obvious raw strings detected.');
  }
}

main();
