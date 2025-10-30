"""
Feature extraction for HT-STF cross-correlation shape.
Derives 16 scalar features around the detected peak, plus the external label in CSV files.

Reproducibility defaults:
- htstf_len = 160 samples (preamble length)
- htstf_period = 80 samples (repetition period)
"""
import numpy as np

def extract_corr_features(corr, lag, htstf_len=160, htstf_period=80):
    """
    Extract correlation-shape features around the detected peak.
    Returns (list) in this order of 16 features:
    [peak, psr, pnr, ratio_peak_to_median, periodic_sum, fwhm,
     w_peak_period, w_mean_period, w_std_period, w_energy_period, sharpness_period,
     w_peak_preamble, w_mean_preamble, w_std_preamble, w_energy_preamble, sharpness_preamble]

    Args:
        corr (np.ndarray): complex correlation sequence
        lag (int): index of detected peak (e.g., np.argmax(np.abs(corr)))
        htstf_len (int): preamble length (default 160)
        htstf_period (int): repetition period (default 80)

    Notes:
        - Magnitude uses np.abs(corr)
        - Noise floor uses median outside ±htstf_len around lag
        - PSR computed within ±htstf_len excluding a small guard around the peak
        - FWHM width counts samples above 0.5 * peak
    """
    mag = np.abs(corr)

    def safe_slice(a, s, e):
        s = max(0, s); e = min(len(a), e)
        return a[s:e]

    preamble_len = htstf_len
    period       = htstf_period
    win_sizes = sorted(set([period, preamble_len]))

    # Noise floor: exclude ±preamble_len around the peak
    guard = preamble_len
    left_noise  = safe_slice(mag, 0, lag - guard)
    right_noise = safe_slice(mag, lag + guard, len(mag))
    if (len(left_noise) + len(right_noise)) > 0:
        global_noise = np.median(np.concatenate([left_noise, right_noise]))
    else:
        global_noise = np.median(mag)

    peak = mag[lag]

    # PSR within ±guard, excluding a tiny guard around the peak
    local = safe_slice(mag, lag - guard, lag + guard)
    if len(local) > 0:
        g2 = max(8, period // 10)  # small exclusion around the peak
        left_loc  = safe_slice(mag, lag - guard, lag - g2)
        right_loc = safe_slice(mag, lag + g2, lag + guard)
        if (len(left_loc) + len(right_loc)) > 0:
            sidelobe_max = np.max(np.concatenate([left_loc, right_loc]))
        else:
            sidelobe_max = 1e-12
    else:
        sidelobe_max = 1e-12

    psr = float(peak / (sidelobe_max + 1e-12))
    pnr = float(peak / (global_noise + 1e-12))
    ratio_peak_to_median = pnr  # alias for clarity

    # Periodicity at 'period' samples
    harmonics = []
    max_k = guard // period if period > 0 else 0
    for k in range(1, max_k + 1):
        for sign in (-1, +1):
            idx = lag + sign * k * period
            if 0 <= idx < len(mag):
                harmonics.append(mag[idx])
    periodic_sum = float((np.sum(harmonics) / (peak + 1e-12)) if harmonics else 0.0)

    # FWHM within ±guard
    half = 0.5 * peak
    left_i = lag
    while left_i > 0 and mag[left_i] >= half:
        left_i -= 1
    right_i = lag
    while right_i < len(mag) and mag[right_i] >= half:
        right_i += 1
    fwhm = int(right_i - left_i)

    feats = [float(peak), float(psr), float(pnr), float(ratio_peak_to_median), float(periodic_sum), int(fwhm)]

    # Multi-scale stats (period, preamble)
    for W in win_sizes:
        w = safe_slice(mag, lag, lag + W)
        if len(w) == 0:
            feats.extend([0.0, 0.0, 0.0, 0.0, 0.0])
            continue
        w_peak = float(np.max(w))
        w_mean = float(np.mean(w))
        w_std  = float(np.std(w))
        w_energy = float(np.sum(w**2))
        sharpness = float((w_peak - w_mean) / (w_std + 1e-6))
        feats.extend([w_peak, w_mean, w_std, w_energy, sharpness])

    return feats
