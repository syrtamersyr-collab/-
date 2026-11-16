// Samples evenly spaced points on the sphere and keeps the ones on land → assets/land.json
import { readFileSync, writeFileSync } from 'fs';
import { feature } from 'topojson-client';
import { geoContains } from 'd3-geo';
const topo = JSON.parse(readFileSync('node_modules/world-atlas/land-110m.json'));
const land = feature(topo, topo.objects.land);
const N = 42000, out = [];
for (let i = 0; i < N; i++) {
  const y = 1 - (i + .5) / N * 2, lat = Math.asin(y) * 180 / Math.PI, lon = ((i * 137.50776405) % 360) - 180;
  if (lat < -60) continue;
  if (geoContains(land, [lon, lat])) out.push(+lon.toFixed(2), +lat.toFixed(2));
}
writeFileSync('assets/land.json', JSON.stringify(out));
console.log('land points', out.length / 2);
