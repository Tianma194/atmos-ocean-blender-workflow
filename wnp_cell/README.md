# Northwest Pacific circulation cell

An editable Blender project combining land relief, bathymetry, a transparent ocean,
clouds, circulation arrows and an optional humidity map. The project can be adapted
for other atmospheric and oceanic illustrations.

## Getting started

Copy this complete folder and open `scene.blend` in Blender 5.1. Select the
**WNP Cell** scene. Keep `scripts/` and `assets/` with the scene.

Run the entry scripts in Blender's Text Editor:

- Edit the external `config.py`, then run `load_scene.py` to apply your settings.
- After adjusting settings in Blender, run `sync_scene.py` to write supported
  values back to the configuration and save. Synchronize before loading again.
- Run `save_scene.py` to save geometry, node networks and the current composition.

To preserve hand-edited terrain or ocean geometry and materials, turn off the
corresponding `update_geometry` or `update_materials` switch before reloading.

## Adapting the scene

Explore `config.py` for terrain, ocean, atmosphere, object and rendering controls.
You can ask an AI assistant to read this README, the configuration and relevant
scripts, explain parameters, and help implement your intended changes.

The [cloud resource](../assets/convective_cloud/README.md) provides an editable
cloud source and volume export workflow. When changing the geographic region,
prepare matching terrain and map assets and adjust the composition.

## Data and references

The supplied humidity map shows the December–May, 1979–2020 ERA5 mean specific
humidity over 300–900 hPa. The scene covers 115–180°E and 0–25°N.

- [ERA5](https://doi.org/10.1002/qj.3803)
- [NOAA ETOPO 2022, 15 arc-second](https://doi.org/10.25921/fd45-gt74), identified
  as the terrain source in the manuscript; the supplied file's exact version is undocumented.
- [Zenodo reproduction package](https://doi.org/10.5281/zenodo.18083144), including
  the paper's figure-reproduction materials.

Scientific inputs and derived maps retain their source conditions; see
[licensing](../LICENSE.md). Tutorial acknowledgements are in the
[main README](../README.md#acknowledgements-and-learning-resources).
