# SPDX-License-Identifier: GPL-3.0-or-later
import numpy as np


def smooth_elevation(source, config):
    iterations = config['iterations']
    strength = float(config['strength'])
    minimum = config['min_component_vertices']
    if not isinstance(iterations, int) or iterations < 0:
        raise ValueError('smoothing.iterations must be a nonnegative integer')
    if not 0 <= strength <= 1:
        raise ValueError('smoothing.strength must be between 0 and 1')
    if not isinstance(minimum, int) or minimum < 1:
        raise ValueError('smoothing.min_component_vertices must be positive')
    result = np.array(source, dtype=np.float64, copy=True)
    active = bool(config['enabled'] and iterations > 0 and strength > 0)
    if not active:
        return result, {'enabled': False, 'source_unchanged': True}

    land = np.isfinite(source) & (source > 0)
    ids = np.full(source.shape, -1, dtype=np.int32)
    count = int(land.sum())
    if not count:
        return result, {'enabled': True, 'components': 0, 'source_unchanged': True}
    ids[land] = np.arange(count, dtype=np.int32)
    finite = np.isfinite(source)
    degree = np.zeros(count, dtype=np.int32)
    edges = []
    for left, right in (
        ((slice(None), slice(None, -1)), (slice(None), slice(1, None))),
        ((slice(None, -1), slice(None)), (slice(1, None), slice(None))),
        ((slice(None, -1), slice(None, -1)), (slice(1, None), slice(1, None))),
    ):
        a, b = ids[left].ravel(), ids[right].ravel()
        valid = (finite[left] & finite[right]).ravel()
        degree += np.bincount(a[valid & (a >= 0)], minlength=count).astype(np.int32)
        degree += np.bincount(b[valid & (b >= 0)], minlength=count).astype(np.int32)
        both = valid & (a >= 0) & (b >= 0)
        edges.append(np.column_stack((a[both], b[both])))
    edges = np.concatenate(edges)
    a, b = edges[:, 0], edges[:, 1]
    parent = np.arange(count, dtype=np.int32)
    size = np.ones(count, dtype=np.int32)

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for first, second in edges:
        first, second = find(first), find(second)
        if first != second:
            if size[first] < size[second]:
                first, second = second, first
            parent[second] = first
            size[first] += size[second]
    roots = np.array([find(i) for i in range(count)])
    _, labels = np.unique(roots, return_inverse=True)
    sizes = np.bincount(labels)
    component_count = len(sizes)
    eligible = (sizes >= minimum) & (sizes > 1)
    selected = eligible[labels] & (degree > 0)
    original = source[land].astype(np.float64)
    original_peaks = np.zeros(component_count)
    np.maximum.at(original_peaks, labels, original)
    values = original.copy()
    denominator = np.maximum(degree, 1)

    def neighbor_mean(values):
        total = np.bincount(a, weights=values[b], minlength=count)
        total += np.bincount(b, weights=values[a], minlength=count)
        return total / denominator

    max_recovery_per_pass = 1.0
    for _ in range(iterations):
        mean = neighbor_mean(values)
        values[selected] = (1-strength)*values[selected] + strength*mean[selected]
        filtered_peaks = np.zeros(component_count)
        np.maximum.at(filtered_peaks, labels, values)
        gain = np.ones(component_count)
        gain[eligible] = original_peaks[eligible] / filtered_peaks[eligible]
        values *= gain[labels]
        max_recovery_per_pass = max(max_recovery_per_pass, float(gain.max()))
    result[land] = values
    final_peaks = np.zeros(component_count)
    np.maximum.at(final_peaks, labels, values)
    assert np.all(values > 0)
    assert np.allclose(final_peaks, original_peaks, rtol=1e-12, atol=1e-10)
    assert np.array_equal(result[~land], source[~land], equal_nan=True)
    before = original-neighbor_mean(original)
    after = values-neighbor_mean(values)
    rms_before = float(np.sqrt(np.mean(before[selected]**2))) if selected.any() else 0.0
    rms_after = float(np.sqrt(np.mean(after[selected]**2))) if selected.any() else 0.0
    report = {
        'enabled': True, 'iterations': iterations, 'strength': strength,
        'components': component_count, 'smoothed_components': int(eligible.sum()),
        'smoothed_vertices': int(selected.sum()),
        'small_components_unchanged': int((~eligible).sum()),
        'peak_max_error_source_units': float(np.max(np.abs(final_peaks-original_peaks))),
        'peak_recovery_max_factor_per_pass': max_recovery_per_pass,
        'neighbor_residual_rms_before': rms_before,
        'neighbor_residual_rms_after': rms_after,
        'sea_and_land_mask_unchanged': True, 'source_unchanged': True,
        'note': 'Display filter changes local heights and may shift peak locations and subcell coast intersections. All sampled landmass maxima are retained.',
    }
    return result, report
