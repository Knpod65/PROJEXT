import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function readFile(p) {
  try {
    return fs.readFileSync(p, 'utf8');
  } catch (err) {
    console.error('Failed to read', p, err.message);
    process.exit(2);
  }
}

function extractKeys(text) {
  const re2 = /['"`]([^'"`]+?)['"`]\s*:/g;
  const keys = new Set();
  let m;
  while ((m = re2.exec(text)) !== null) {
    keys.add(m[1]);
  }
  return keys;
}

// Raw string scanner
const RAW_FOLDERS = [
  'src/pages',
  'src/components',
  'src/hooks',
  'src/utils',
];

const ALLOWLIST_REGEX = [
  /className/,
  /class=/,
  /tailwind/i,
  /route/i,
  /icon/i,
  /import\s+/,
  /from\s+['"`]/,
  /url\(/,
  /http/i,
  /data-testid/,
  /^\d+$/,
  /['"`][A-Z_]+['"`]/, // enum-like
  /api\//,
  /console\./,
  /['"`][a-z0-9.-]+['"`]/, // likely keys or paths
];

function isAllowed(text) {
  return ALLOWLIST_REGEX.some((re) => re.test(text));
}

function scanRawStrings(dir) {
  const candidates = [];
  const fullDir = path.resolve(__dirname, '..', dir);
  if (!fs.existsSync(fullDir)) return candidates;

  const files = fs.readdirSync(fullDir, { withFileTypes: true });
  for (const file of files) {
    const fullPath = path.join(fullDir, file.name);
    if (file.isDirectory()) {
      candidates.push(...scanRawStrings(path.join(dir, file.name)));
    } else if (file.name.endsWith('.tsx') || file.name.endsWith('.ts')) {
      const content = fs.readFileSync(fullPath, 'utf8');
      // Simple heuristic: look for string literals in JSX text or common props
      const stringRegex = /['"`]([^'"`]{4,})['"`]/g;
      let match;
      while ((match = stringRegex.exec(content)) !== null) {
        const str = match[1].trim();
        if (str.length < 4) continue;
        if (isAllowed(str)) continue;
        if (str.includes('.') && str.split('.').length > 3) continue; // likely key
        candidates.push({
          file: path.relative(path.resolve(__dirname, '..'), fullPath).replace(/\\/g, '/'),
          line: content.substring(0, match.index).split('\n').length,
          text: str,
        });
      }
    }
  }
  return candidates;
}

function main() {
  const args = process.argv.slice(2);
  const isRaw = args.includes('--raw');
  const isStrict = args.includes('--strict');

  // Always run parity check first
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
  } else {
    if (missingInTh.length) {
      console.log('\nKeys present in en.ts but missing in th.ts:');
      missingInTh.slice(0, 200).forEach(k => console.log('  ', k));
    }
    if (missingInEn.length) {
      console.log('\nKeys present in th.ts but missing in en.ts:');
      missingInEn.slice(0, 200).forEach(k => console.log('  ', k));
    }
    if (!isRaw && !isStrict) {
      process.exit(1);
    }
  }

  if (isRaw || isStrict) {
    console.log('\n--- Raw string candidate scan ---');
    let allCandidates = [];
    for (const folder of RAW_FOLDERS) {
      allCandidates = allCandidates.concat(scanRawStrings(folder));
    }

    // Deduplicate
    const unique = new Map();
    for (const c of allCandidates) {
      const key = `${c.file}:${c.line}:${c.text}`;
      if (!unique.has(key)) unique.set(key, c);
    }
    const finalCandidates = [...unique.values()].slice(0, 100); // limit output

    if (finalCandidates.length === 0) {
      console.log('No raw string candidates found.');
    } else {
      finalCandidates.forEach(c => {
        console.log(`[raw-string] ${c.file}:${c.line}`);
        console.log(`  "${c.text}"`);
        console.log('  reason: JSX text / label candidate');
      });
    }

    console.log('\nRaw string scan summary:');
    console.log('- files scanned:', RAW_FOLDERS.length);
    console.log('- candidates found:', finalCandidates.length);
    console.log('- mode:', isStrict ? 'strict' : 'warning');

    if (isStrict && finalCandidates.length > 0) {
      process.exit(1);
    }
  }

  process.exit(0);
}

main();