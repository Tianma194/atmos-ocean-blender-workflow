# Start an independent project

Copy this folder and give it your project's name. Keep its scripts and assets together.

## Set up

1. Create or open a scene in Blender 5.1 and save it as `scene.blend` in this folder.
2. Set `SCENE_NAME` in the external `config.py` to the Blender scene's name.
3. Put external textures, volumes and scientific inputs in a local `assets/` folder.
4. Open this project's `save_scene.py` in Blender's Text Editor and run it.

The initial configuration supports saving a scene. Add object bindings when you
want loading and synchronization to manage selected parameters.

## Daily use

- Edit and save external `config.py`, then run `load_scene.py` to apply it.
- After manual edits to managed parameters, run `sync_scene.py` to update configuration
  and save the scene. Synchronize before loading configuration again.
- Run `save_scene.py` to save the scene and refresh embedded script and configuration copies.

Geometry, curve points, node networks and parenting are stored in the scene.
The external `config.py` is the working configuration.

## Extend the project

To register an object, add a string `workflow_id` in its Custom Properties and use
the same ID in `OBJECTS`. Start with the object's current transforms; parented
objects use local coordinates. See the [WNP configuration](../wnp_cell/config.py)
for examples of object, collection, material-color and scene settings.

Keep supporting code in `scripts/`. An optional `ASSET_SCRIPT` can provide
`validate(config)` and `refresh(config)` for project-specific asset updates;
see the [WNP implementation](../wnp_cell/scripts/map_assets.py). Copy any supporting
scripts needed when adapting these examples.
