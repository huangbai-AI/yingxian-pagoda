import {NodeIO} from '@gltf-transform/core';
import {KHRDracoMeshCompression} from '@gltf-transform/extensions';
import {weld, simplify, prune, dedup, textureCompress} from '@gltf-transform/functions';
import {MeshoptSimplifier} from 'meshoptimizer';
import sharp from 'sharp';
import draco3d from 'draco3dgltf';
import {statSync} from 'node:fs';

const input = 'dist/models/yingxian.glb';
const output = 'minitool-assets/models/yingxian.glb';

// Reader needs Draco to decode original
const reader = new NodeIO()
  .registerExtensions([KHRDracoMeshCompression])
  .registerDependencies({
    'draco3d.encoder': await draco3d.createEncoderModule(),
    'draco3d.decoder': await draco3d.createDecoderModule()
  });

// Writer does NOT register Draco - output will be uncompressed
const writer = new NodeIO();

console.log('Reading model...');
const doc = await reader.read(input);
const root = doc.getRoot();

let trisBefore = 0;
for (const mesh of root.listMeshes()) {
  for (const prim of mesh.listPrimitives()) {
    const idx = prim.getIndices();
    if (idx) trisBefore += idx.getCount() / 3;
  }
}
console.log('Before:', Math.round(trisBefore), 'tris');

// Remove Draco extension from the document after decode
const dracoExt = doc.getRoot().listExtensionsUsed().find(e => e.extensionName === 'KHR_draco_mesh_compression');
if (dracoExt) {
  dracoExt.dispose();
  console.log('Removed Draco extension declaration');
}

// Weld
console.log('Welding...');
await doc.transform(weld({tolerance: 0.001}));

// Aggressive simplify - single pass with high error tolerance
console.log('Simplifying (ratio=0.03, error=0.15)...');
await doc.transform(simplify({
  simplifier: MeshoptSimplifier,
  ratio: 0.03,
  error: 0.15,
  lockBorder: false,
}));

// Second pass to catch remaining dense meshes
console.log('Simplify pass 2 (ratio=0.5, error=0.25)...');
await doc.transform(simplify({
  simplifier: MeshoptSimplifier,
  ratio: 0.5,
  error: 0.25,
  lockBorder: false,
}));

// Cleanup
await doc.transform(dedup({textures: false}));
await doc.transform(prune({keepLeaves: true}));

// Compress textures to 1024 JPEG
console.log('Compressing textures...');
await doc.transform(
  textureCompress({
    encoder: sharp,
    targetFormat: 'jpeg',
    quality: 70,
    resize: [1024, 1024],
  })
);

let trisAfter = 0;
for (const mesh of root.listMeshes()) {
  for (const prim of mesh.listPrimitives()) {
    const idx = prim.getIndices();
    if (idx) trisAfter += idx.getCount() / 3;
  }
}
console.log('After:', Math.round(trisAfter), 'tris,', root.listMeshes().length, 'meshes');

console.log('Writing GLB (uncompressed geometry)...');
await writer.write(output, doc);

// Verify with clean reader
const verify = await new NodeIO().read(output);
let verifyTris = 0;
for (const mesh of verify.getRoot().listMeshes()) {
  for (const prim of mesh.listPrimitives()) {
    const idx = prim.getIndices();
    if (idx) verifyTris += idx.getCount() / 3;
  }
}
console.log('Output:', (statSync(output).size / 1024 / 1024).toFixed(2), 'MB');
console.log('Verified:', Math.round(verifyTris), 'tris,', verify.getRoot().listNodes().length, 'nodes');
console.log('Extensions used:', verify.getRoot().listExtensionsUsed().map(e => e.extensionName));
