import bpy
import sys
import os

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

input_path = sys.argv[-2]
output_path = sys.argv[-1]

print(f"Importing: {input_path}")
bpy.ops.import_scene.gltf(filepath=input_path)

# Stats before
def count_tris():
    total = 0
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            total += sum(len(p.vertices) // 3 for p in obj.data.polygons)
    return total

before = count_tris()
print(f"Before decimate: {before} triangles, {len(bpy.data.meshes)} meshes")

# Apply Decimate to every mesh object
TARGET_RATIO = 0.06
MIN_TRIS = 200

decimated = 0
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    mesh = obj.data
    current_tris = len(mesh.polygons)
    if current_tris <= MIN_TRIS:
        continue

    # Add decimate modifier
    mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
    mod.decimate_type = 'COLLAPSE'
    mod.ratio = TARGET_RATIO
    mod.use_collapse_triangulate = True

    # Apply
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
        decimated += 1
    except Exception as e:
        print(f"  Failed on {obj.name}: {e}")
        obj.modifiers.remove(mod)

after = count_tris()
print(f"After decimate: {after} triangles (decimated {decimated} objects)")
print(f"Reduction: {100 * (1 - after / before):.1f}%")

# Export GLB without Draco
print(f"Exporting: {output_path}")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format='GLB',
    export_apply=True,
    export_draco_mesh_compression_enable=False,
)

size_mb = os.path.getsize(output_path) / 1024 / 1024
print(f"Output: {size_mb:.2f} MB")
