"""Top-of-atmosphere insolation and daylight, per latitude row and month.

Two things in the gap-fill depend on astronomy rather than on data:

*dark*   A pixel-month in which the sun never rises has essentially zero primary
         production. A missing satellite retrieval there is a true zero, not a gap, and
         filling it from anywhere else would invent production that cannot exist.

*Q_toa*  When a value has to be borrowed from another pixel, it is scaled by the ratio of
         top-of-atmosphere daily insolation so that light is never imported from a
         brighter latitude than the target. This keeps the nearest-neighbour fill from
         pushing mid-latitude productivity into the polar twilight.

Declination and the Earth-Sun distance factor follow Spencer (1971) Fourier fits, which
are accurate to a few arc-minutes -- far tighter than the monthly aggregation needs.
"""

from __future__ import annotations

import calendar

import numpy as np

SOLAR_CONSTANT_W_M2 = 1361.0


def _declination_and_eccentricity(doy: np.ndarray | int):
    """Solar declination (rad) and the (d0/d)^2 eccentricity factor for a day of year."""
    gamma = 2.0 * np.pi * (np.asarray(doy, dtype="float64") - 1.0) / 365.0
    dec = (
        0.006918
        - 0.399912 * np.cos(gamma)
        + 0.070257 * np.sin(gamma)
        - 0.006758 * np.cos(2 * gamma)
        + 0.000907 * np.sin(2 * gamma)
        - 0.002697 * np.cos(3 * gamma)
        + 0.001480 * np.sin(3 * gamma)
    )
    ecc = (
        1.000110
        + 0.034221 * np.cos(gamma)
        + 0.001280 * np.sin(gamma)
        + 0.000719 * np.cos(2 * gamma)
        + 0.000077 * np.sin(2 * gamma)
    )
    return dec, ecc


def monthly_tables(year: int, ny: int) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(q_toa, lit_days)``, each shaped ``(12, ny)``.

    ``q_toa``     monthly mean of daily-mean TOA insolation, W m-2.
    ``lit_days``  number of days in the month on which the sun rises at all.
    """
    lat = np.deg2rad(90.0 - (np.arange(ny) + 0.5) * (180.0 / ny))
    q = np.zeros((12, ny))
    lit = np.zeros((12, ny))
    for month in range(1, 13):
        first = sum(calendar.monthrange(year, m)[1] for m in range(1, month)) + 1
        ndays = calendar.monthrange(year, month)[1]
        acc = np.zeros(ny)
        nlit = np.zeros(ny)
        for doy in range(first, first + ndays):
            dec, ecc = _declination_and_eccentricity(doy)
            # cos of the sunset hour angle; >= 1 means the sun never rises
            cos_omega = -np.tan(lat) * np.tan(dec)
            omega = np.arccos(np.clip(cos_omega, -1.0, 1.0))
            acc += (SOLAR_CONSTANT_W_M2 / np.pi) * ecc * (
                omega * np.sin(lat) * np.sin(dec) + np.cos(lat) * np.cos(dec) * np.sin(omega)
            )
            nlit += cos_omega < 1.0
        q[month - 1] = np.maximum(acc / ndays, 0.0)
        lit[month - 1] = nlit
    return q, lit


def days_in_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def month_start_doy(year: int, month: int) -> int:
    """Day-of-year of the first day of ``month`` -- OSU encodes months this way."""
    return sum(calendar.monthrange(year, m)[1] for m in range(1, month)) + 1
