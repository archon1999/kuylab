import { LAYERS } from 'smplr';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const root = new URL('../public/audio/splendid/', import.meta.url);
await mkdir(root, { recursive: true });
const base = 'https://smpldsnds.github.io/sfzinstruments-splendid-grand-piano/samples/';
const names = [...new Set(LAYERS.flatMap(layer => layer.samples.map(([, name]) => name)))].sort();
const queue = [...names], files = [];
await Promise.all(Array.from({length: 6}, async () => {
  for (let name = queue.shift(); name; name = queue.shift()) {
    const filename = name.toLowerCase().replaceAll(' ', '-').replaceAll('#', 's') + '.ogg';
    const url = new URL(encodeURIComponent(filename), root);
    let bytes;
    try { bytes = await readFile(url); } catch {
      const response = await fetch(base + encodeURIComponent(name + '.ogg'));
      if (!response.ok) throw new Error(`${filename}: ${response.status}`);
      bytes = Buffer.from(await response.arrayBuffer());
      if (bytes.toString('ascii', 0, 4) !== 'OggS') throw new Error(`Invalid OGG: ${filename}`);
      await writeFile(url, bytes);
    }
    files.push({path: '/audio/splendid/' + encodeURIComponent(filename), bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')});
  }
}));
const worklet = await readFile(new URL('../dattorro.worklet.js', root));
files.push({path: '/audio/dattorro.worklet.js', bytes: worklet.length, sha256: createHash('sha256').update(worklet).digest('hex')});
files.sort((a,b)=>a.path.localeCompare(b.path));
await writeFile(new URL('manifest.json', root), JSON.stringify({instrument: 'Splendid Grand Piano', sample_count: names.length, author: 'AKAI', license: 'Public Domain', source: base, mapping: 'smplr@1.1.0 LAYERS', total_bytes: files.reduce((n,f)=>n+f.bytes,0), files},null,2)+'\n');
console.log(`Downloaded and hashed ${files.length} samples, ${(files.reduce((n,f)=>n+f.bytes,0)/1e6).toFixed(1)} MB`);
