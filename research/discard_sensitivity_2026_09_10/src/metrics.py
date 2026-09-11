"""Independent strict totals and analytic controls for paired comparisons."""
import numpy as np


def fixed_support_ppr(coefficients, harvest, carbon_factor=9.):
    coefficients=coefficients.reindex(harvest.index)
    positive=harvest>0
    if not np.isfinite(harvest).all() or (harvest<0).any(): return None
    if not np.isfinite(coefficients[positive]).all(): return None
    if (coefficients[positive]<-1e-8).any(): return None
    return float((coefficients[positive]*harvest[positive]).sum()/carbon_factor)


def decompose(baseline_H, scenario_H, baseline_L, scenario_L):
    if any(v is None or not np.isfinite(v) for v in (baseline_H,scenario_H,baseline_L,scenario_L)):
        return {k:None for k in ['coefficient_effect','catch_effect','interaction','total_change','residual']}
    a=scenario_H-baseline_H; b=baseline_L-baseline_H
    c=scenario_L-scenario_H-baseline_L+baseline_H
    total=scenario_L-baseline_H
    return dict(coefficient_effect=a,catch_effect=b,interaction=c,total_change=total,
                residual=a+b+c-total)


def solve_recycling_control(a,b,c,d):
    if b*d>=1: raise ValueError('recycling diverges')
    # Independently solve simultaneous equations x=a+b*y, y=c+d*x.
    x,y=np.linalg.solve(np.array([[1.,-b],[-d,1.]]),np.array([a,c]))
    return dict(fish=float(x),detritus=float(y),loop_gain=b*d)
