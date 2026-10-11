# Atmosphere and ocean Blender workflow

Editable three-dimensional visualization projects for atmospheric and ocean sciences.
The workflow combines scientific data, Blender scene editing and Python configuration.

## Projects and resources

| Folder | Contents |
| --- | --- |
| [wnp_cell](wnp_cell/README.md) | Complete Northwest Pacific circulation project |
| [template](template/README.md) | Starting files for an independent project |
| [assets/convective_cloud](assets/convective_cloud/README.md) | Editable cloud and volume export workflow |

Each project contains its own scene, scripts and runtime assets. Copy a project
folder anywhere and keep its contents together. Start another project by copying
`template/`, or adapt `wnp_cell/` for a map-based composition. Projects can evolve
independently; template updates can be adopted when useful.

## How it works

The Blender scene holds authored geometry, curves, node networks and parenting.
Python configuration holds selected transforms, appearance and rendering controls.
Edit either side, then use the project's loading or synchronization entry to carry
the changes across.

Blender 5.1 was used for the current projects. Its bundled Python and NumPy support
the supplied scene scripts. Project READMEs describe the operations and data sources.

## Related article

The WNP project originated from Fig. 3a of *A three-dimensional circulation pathway
reinforces successive winter–spring quasi-biweekly oscillations over the Northwest
Pacific*, by Tian Ma and colleagues. Figure-reproduction materials are deposited on
[Zenodo](https://doi.org/10.5281/zenodo.18083144). This repository shares an editable
workflow that can develop further and support other scientific illustrations.

Please cite the associated article and identify the release or commit used when
using this work in research.

## Reuse

Python code is GPL-3.0-or-later; original artwork and documentation are CC BY 4.0.
Scientific inputs retain their source conditions. See [licensing](LICENSE.md)
and each project's README for attribution and source information.

## Acknowledgements and learning resources

We thank the following creators for sharing tutorials and example projects
that provided learning references for this project:

- **阿顾cg屋**, [blender 风格化地形高度视觉](https://www.bilibili.com/video/BV1Zv4y117DZ/) (Bilibili, 18 November 2022).
- **高小晟_**, [Blender教程-捏自由形状的体积云](https://www.bilibili.com/video/BV1sY4y1Q7zj/) (Bilibili, 24 March 2023).
- **Nello Fontani**, [Geometry nodes Clouds](https://nello_fontani.artstation.com/projects/oblGVq)
  ([Gumroad project](https://nellofontani.gumroad.com/l/bqnar)).
- **-时光之刃-**, [在Blender中实现箭头沿路径移动](https://www.bilibili.com/video/BV1Ss4y1X7At/) (Bilibili, 5 May 2023).
