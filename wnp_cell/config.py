# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCENE_NAME = 'WNP Cell'
ASSET_SCRIPT = 'scripts/map_assets.py'

# %% Geographic frame and assets
REGION = {'extent': (115.0, 180.0, 0, 25.0), 'origin_lonlat': (150.0, 12.5), 'xy_scale': 0.1, 'y_stretch': 1.75}
ASSETS = {'terrain': 'assets/elevation.npz',
          'humidity': 'assets/humidity_map_with_colorbar.png',
          'wet_cloud': 'assets/cloud.vdb'}

# %% Terrain
TERRAIN = {'update_geometry': True,
 'grid_stride': 2,
 'land': {'enabled': True,
          'height_scale': 0.00017,
          'smoothing': {'enabled': True,
                        'iterations': 6,
                        'strength': 0.2,
                        'min_component_vertices': 3},
          'roughness': 0.8,
          'colors_m': [(0, (0.32, 0.42, 0.22, 1)),
                       (1000, (0.48, 0.4, 0.25, 1)),
                       (2500, (0.62, 0.56, 0.44, 1)),
                       (4000, (0.85, 0.83, 0.76, 1))]},
 'seabed': {'enabled': True,
            'depth_scale': 0.00017,
            'smoothing': {'enabled': True,
                          'iterations': 2,
                          'strength': 0.15,
                          'min_component_vertices': 3},
            'roughness': 0.85,
            'colors_m': [(0, (0.18, 0.48, 0.48, 1)),
                         (2000, (0.07, 0.28, 0.36, 1)),
                         (6000, (0.025, 0.12, 0.23, 1)),
                         (11000, (0.012, 0.035, 0.1, 1))]},
 'sea_level_scene': 0.0,
 'update_materials': True}

# %% Ocean
OCEAN = {'enabled': True,
 'update_geometry': True,
 'opacity': 0.65,
 'roughness': 0.28,
 'ior': 1.333,
 'body': {'enabled': True,
          'fit_seabed': True,
          'walls': {'opacity': 0.25,
                    'roughness': 0.18,
                    'colors_scene': [(0, (0.2, 0.62, 0.66, 1)), (0.4, (0.015, 0.1, 0.18, 1))]},
          'bottom': {'color': (0.055, 0.36, 0.37, 1.0), 'opacity': 0.35, 'roughness': 0.48},
          'min_depth_scene': 0.4,
          'bottom_clearance_scene': 0.03},
 'waves': {'direction_deg': 25.0,
           'phase': 0.0,
           'shore_fade_depth_m': 300.0,
           'amplitude_scene': 0.005,
           'wavelength_scene': 0.35},
 'colors_m': [(0, (0.25, 0.72, 0.65, 1)),
              (500, (0.04, 0.42, 0.55, 1)),
              (3000, (0.015, 0.13, 0.32, 1)),
              (11000, (0.006, 0.025, 0.11, 1))],
 'update_materials': True,
 'height_offset_scene': 0.008}

# %% Atmosphere
ATMOSPHERE = {'enabled': True,
 'humidity': {'enabled': True,
              'update_texture': True,
              'opacity': 0.5,
              'emission_strength': 1.0,
              'height_offset_scene': -0.001,
              'update_materials': True}}

# %% Objects grouped as in the Outliner
OBJECTS = {
    'Scene Setup': {
        'camera': {
            'position': (-0.337072462, -13.7919464, 3.28241587),
            'rotation_deg': (80.8700545, 6.92277517e-06, -0.399998716),
            'scale': (1.0, 1.0, 1.0),
            'visible': True, 'viewport': True, 'render': True,
            'camera': {'lens': 55.0, 'ortho_scale': 6.0, 'shift_x': 0.0, 'shift_y': 0.0},
        },
        'key_light': {
            'position': (-0.404280186, 0.0270595551, 10.0),
            'rotation_deg': (2.36531479, -7.40927566, -0.782508413),
            'scale': (0.99999994, 1.0, 0.99999994),
            'visible': True, 'viewport': True, 'render': True,
            'light': {'energy': 4.0, 'color': (1.0, 1.0, 1.0), 'angle': 0.00918043219},
        },
        'cloud_front_fill': {
            'position': (0.0316008329, -6.15830135, 2.79999995),
            'rotation_deg': (61.2796786, -0.0, 0.0),
            'scale': (1.68693161, 1.68693161, 1.68693161),
            'visible': True, 'viewport': True, 'render': True,
            'light': {'energy': 50.0, 'color': (1.0, 1.0, 1.0), 'size': 3.0, 'size_y': 0.25},
        },
        'cloud_top_fill': {
            'position': (-1.79999995, 0.0, 4.0),
            'rotation_deg': (7.72862286, -1.16345576e-06, -179.999991),
            'scale': (1.0, 0.99999994, 0.99999994),
            'visible': True, 'viewport': True, 'render': True,
            'light': {'energy': 50.0, 'color': (1.0, 1.0, 1.0), 'size': 2.0, 'size_y': 0.25},
        },
        'cloud_interior_fill': {
            'position': (-1.71925688, -0.380745411, 1.15715885),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.0, 1.0, 1.0),
            'visible': True, 'viewport': True, 'render': True,
            'light': {'energy': 10.0, 'color': (1.0, 1.0, 1.0), 'shadow_soft_size': 0.400000006},
        },
    },
    'WNP cell': {
        'wnp_cell_control': {
            'position_lonlat_height': (146.408386, 11.4683931, 1.79399121),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.77628577, 1.4988749, 1.4988749),
            'visible': True, 'viewport': True, 'render': True,
        },
        'wnp_cell_arrows': {
            'position': (-0.164386004, 0.160810739, 0.920152366),
            'rotation_deg': (89.9999957, -0.0, 0.0),
            'scale': (-0.0728790835, -0.0552812517, -0.0477557853),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.547562659, 0.210192516, 0.800132453, 1.0), '1': (0.0, 0.0, 0.0, 1.0)},
        },
        'wnp_cell_path': {
            'position': (-0.232160509, 0.160810739, 0.920152366),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.17683768, 1.0, 1.0),
            'visible': True, 'viewport': True, 'render': False,
        },
    },
    'Circulation': {
        'circulation_control': {
            'position_lonlat_height': (132.357157, 10.3571429, 2.04114056),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.49887502, 1.49887502, 1.49887502),
            'visible': True, 'viewport': True, 'render': True,
        },
        'wet_circulation_arrows': {
            'position': (-1.4924469, 0.163396686, 1.13175201),
            'rotation_deg': (95.1453206, -0.0, 0.0),
            'scale': (-0.0643043593, -0.0643043816, -0.0523506589),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.138430342, 0.254152179, 0.57112515, 1.0), '1': (0.0, 0.0, 0.0, 1.0)},
        },
        'wet_circulation_path': {
            'position': (-0.889397025, 0.163396686, 1.13175201),
            'rotation_deg': (5.14532109, -0.0, 0.0),
            'scale': (1.36160338, 1.1084913, 1.36160314),
            'visible': True, 'viewport': True, 'render': False,
        },
    },
    'Ascent': {
        'ascent_control': {
            'position_lonlat_height': (132.0, 10.3571429, 0.344598264),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.87359381, 1.87359381, 1.87359381),
            'visible': True, 'viewport': True, 'render': True,
        },
        'wet_ascent_arrows': {
            'position': (-0.510567546, -0.00439283252, 0.542943478),
            'rotation_deg': (90.0000162, -89.9999957, 0.0),
            'scale': (-0.0538255908, -0.0538255908, -0.0538255908),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.138430342, 0.254152179, 0.57112515, 1.0), '1': (0.0, 0.0, 0.0, 1.0)},
        },
        'wet_ascent_path': {
            'position': (-0.510567546, -0.00439283252, 0.661366582),
            'rotation_deg': (-90.0000025, 89.9999957, 0.0),
            'scale': (0.212449729, 0.212449729, 0.212449729),
            'visible': True, 'viewport': True, 'render': False,
        },
        'wet_mirror_pivot': {
            'position': (-1.01094329, -0.00439283252, 0.661366582),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.0, 1.0, 1.0),
            'visible': True, 'viewport': True, 'render': False,
        },
    },
    'Wet Clouds': {
        'wet_cloud_control': {
            'position_lonlat_height': (146.769655, 15.4408251, 0.201727629),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.0, 1.0, 1.0),
            'visible': True, 'viewport': True, 'render': True,
        },
        'wet_cloud': {
            'position': (-1.43180418, -0.725496054, 0.219458014),
            'rotation_deg': (0.0, -0.0, 20.6378213),
            'scale': (0.219809756, 0.261400104, 0.294787318),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.40959239, 0.507557631, 0.620020509, 1.0)},
        },
    },
    'Wet Rain': {
        'wet_rain': {
            'position_lonlat_height': (130.94546, 9.93868794, 0.0663952529),
            'rotation_deg': (0.0, 0.0, 0.0),
            'scale': (1.06802917, 1.06802917, 1.06802917),
            'visible': True, 'viewport': True, 'render': True,
            'rain_color': (0.189999998, 0.25999999, 0.330000013, 1.0),
            'rain': {'count': 1000, 'width': 1.04221773, 'depth': 0.959687948, 'height': 0.299088866, 'length': 0.0450000018, 'radius': 0.0013, 'seed': 17},
        },
    },
    'Descent': {
        'descent_control': {
            'position_lonlat_height': (168.0, 10.3571429, 0.454017371),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.87359381, 1.87359381, 1.87359381),
            'visible': True, 'viewport': True, 'render': True,
        },
        'dry_descent_arrows': {
            'position': (1.42651463, -0.00439283252, 0.364137471),
            'rotation_deg': (90.0000162, -89.9999957, 0.0),
            'scale': (-0.0538255908, -0.0538255908, -0.0538255908),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.254150569, 0.171441317, 0.130136564, 1.0), '1': (0.0, 0.0, 0.0, 1.0)},
        },
        'dry_descent_path': {
            'position': (1.42651463, -0.00439283252, 0.568407416),
            'rotation_deg': (-90.0000025, 89.9999957, 0.0),
            'scale': (0.212449729, 0.212449729, 0.212449729),
            'visible': True, 'viewport': True, 'render': False,
        },
        'dry_mirror_pivot': {
            'position': (0.945058823, -0.0539107323, 0.755711734),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.0, 1.0, 1.0),
            'visible': True, 'viewport': True, 'render': False,
        },
    },
    'Dry Clouds': {
        'dry_cloud': {
            'position': (1.86537933, -0.229081631, -3.72682333),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.0, 1.0, 1.0),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (1.0, 0.873416483, 0.725761354, 1.0)},
        },
        'dry_cloud_shape_edit_points': {
            'position': (0.0, 0.0, 0.0),
            'rotation_deg': (0.0, 0.0, 0.0),
            'scale': (1.0, 1.0, 1.0),
            'visible': False, 'viewport': True, 'render': False,
        },
        'dry_cloud_control': {
            'position_lonlat_height': (168.0, 12.3285714, 1.54999995),
            'rotation_deg': (0.0, 0.0, 0.0),
            'scale': (0.128703862, 0.128703862, 0.128703862),
            'visible': True, 'viewport': True, 'render': True,
        },
    },
    'Background Flow': {
        'background_flow_control': {
            'position_lonlat_height': (148.459147, 10.1651629, 0.659296274),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.87359381, 1.87359381, 1.87359381),
            'visible': True, 'viewport': True, 'render': True,
        },
        'background_flow_arrow': {
            'position': (-0.302068651, -0.003482125, 0.351888388),
            'rotation_deg': (60.0000085, -0.0, 0.0),
            'scale': (0.105732821, 0.105732828, 0.105732828),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (1.0, 1.0, 1.0, 1.0), '1': (0.0, 0.0, 0.0, 1.0)},
        },
    },
    'Legend': {
        'legend_control': {
            'position_lonlat_height': (147.599902, 10.1791428, 2.74958277),
            'rotation_deg': (0.0, -0.0, 0.0),
            'scale': (1.59255469, 1.59255469, 1.59255469),
            'visible': True, 'viewport': True, 'render': True,
        },
        'wnp_cell_legend_arrow': {
            'position': (-1.54918194, 0.0, 1.72296083),
            'rotation_deg': (89.9999957, -0.0, 0.0),
            'scale': (-0.0566623397, -0.0566623397, -0.0566623397),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.547562659, 0.210192516, 0.800132453, 1.0), '1': (0.0, 0.0, 0.0, 1.0)},
        },
        'background_flow_legend_arrow': {
            'position': (1.43604469, -0.00361901056, 1.72296083),
            'rotation_deg': (-89.9999957, -8.65142384e-06, 179.999991),
            'scale': (0.0551811531, 0.0551811531, 0.0551811531),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (1.0, 1.0, 1.0, 1.0), '1': (0.0, 0.0, 0.0, 1.0)},
        },
        'dry_legend_arrow': {
            'position': (0.48982808, 0.0, 1.72296083),
            'rotation_deg': (89.9999957, -0.0, 0.0),
            'scale': (-0.0566623397, -0.0566623397, -0.0566623397),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.254150569, 0.171441317, 0.130136564, 1.0), '1': (0.0, 0.0, 0.0, 1.0)},
        },
        'wet_legend_arrow': {
            'position': (-0.470603824, 0.0, 1.72296083),
            'rotation_deg': (89.9999957, -0.0, 0.0),
            'scale': (-0.0566623397, -0.0566623397, -0.0566623397),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.138430342, 0.254152179, 0.57112515, 1.0), '1': (0.0, 0.0, 0.0, 1.0)},
        },
        'wet_label': {
            'position': (-0.477856308, 0.0, 1.57163823),
            'rotation_deg': (89.9999957, -0.0, 0.0),
            'scale': (0.0595086589, 0.112043798, 0.112043798),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.0, 0.0, 0.0, 1.0)},
            'text': 'Wet QBWO anomaly',
        },
        'dry_label': {
            'position': (0.488564819, 0.0, 1.57163823),
            'rotation_deg': (89.9999957, -0.0, 0.0),
            'scale': (0.0595086589, 0.112043798, 0.112043798),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.0, 0.0, 0.0, 1.0)},
            'text': 'Dry QBWO anomaly',
        },
        'background_flow_label': {
            'position': (1.44090796, 0.0, 1.57163823),
            'rotation_deg': (89.9999957, -0.0, 0.0),
            'scale': (0.070667319, 0.112043798, 0.112043798),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.0, 0.0, 0.0, 1.0)},
            'text': 'Seasonal-mean easterly flow',
        },
        'wnp_cell_label': {
            'position': (-1.55335093, 0.0, 1.57163823),
            'rotation_deg': (89.9999957, -0.0, 0.0),
            'scale': (0.0656825379, 0.112043798, 0.112043798),
            'visible': True, 'viewport': True, 'render': True,
            'colors': {'0': (0.0, 0.0, 0.0, 1.0)},
            'text': 'WNP-cell circulation response',
        },
    },
}

# %% Collection visibility
COLLECTIONS = {
    'scene_content': {'viewport': True, 'render': True},
    'scene_setup': {'viewport': True, 'render': True},
    'map': {'viewport': True, 'render': True},
    'terrain': {'viewport': True, 'render': True},
    'specific_humidity': {'viewport': True, 'render': True},
    'wnp_cell': {'viewport': True, 'render': True},
    'qbwo_wet': {'viewport': True, 'render': True},
    'circulation': {'viewport': True, 'render': True},
    'ascent': {'viewport': True, 'render': True},
    'wet_clouds': {'viewport': True, 'render': True},
    'wet_rain': {'viewport': True, 'render': True},
    'qbwo_dry': {'viewport': True, 'render': True},
    'descent': {'viewport': True, 'render': True},
    'dry_clouds': {'viewport': True, 'render': True},
    'background_flow': {'viewport': True, 'render': True},
    'legend': {'viewport': True, 'render': True},
    'custom_elements': {'viewport': True, 'render': True},
}

# %% Render and color management
SCENE = {
    'render': {'resolution_x': 2050, 'resolution_y': 1000, 'resolution_percentage': 100, 'film_transparent': True},
    'cycles': {'samples': 4096, 'preview_samples': 256, 'use_denoising': True},
    'view': {'view_transform': 'Filmic', 'look': 'None', 'exposure': 0.0, 'gamma': 1.0},
}
