# Editable convective cloud

Open `assets/convective_cloud/cloud.blend` in Blender 5.1 and select **Editable Cloud**.
The cloud contains its editable scaffold, control objects and geometry nodes.
Append the complete editable collection when transferring it to another scene;
make collection instances independent before editing their objects.

On **Full cloud / Block skeleton**, the **Structure volume preview** modifier
exposes Detail strength, Detail scale, Fine detail and Density multiplier.
Larger Detail scale produces finer features. Voxel size 0.04 is the supplied
setting; 0.06 or 0.08 reduces interactive cost. Disabling Volume preview exposes
the scaffold. Main billow structure's Guide only exposes the block structure.

## Export a changed shape

Save the edited cloud file, then run from the repository root, replacing `blender`
with your Blender executable if it is not on your command path:

```sh
blender --background assets/convective_cloud/cloud.blend --python assets/convective_cloud/scripts/export_volume.py
```

This exports `assets/convective_cloud/cache/cloud.vdb` from the saved source.
Copy the VDB into your project's `assets/` directory and select that local file in
its configuration. WNP uses its own `wnp_cell/assets/cloud.vdb`.

For a custom output location, add `-- --output /path/to/project/assets/cloud.vdb`.
Keep the project's placement and scale when replacing a cloud shape.

Changing only placement or material does not require a new VDB export.

The source's **Frozen Cloud** scene uses the cache through a relative path.
For advanced changes, `scripts/refine_density.py` replaces the final density nodes;
save a copy before using it. Ordinary shape editing uses the existing controls.
