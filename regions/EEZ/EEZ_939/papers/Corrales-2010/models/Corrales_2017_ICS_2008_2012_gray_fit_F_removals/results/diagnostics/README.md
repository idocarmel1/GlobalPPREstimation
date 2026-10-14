# Direct SPPR diagnostics

GE, TE and With Egestion were executed with the settings in diagnostic_manifest.json. Complete arrays, masks, axes and names remain in each full_return.json. The group_sppr.csv is a convenience scope-sum view, with all scientific restrictions retained.

To reproduce with the required scientific Python environment, run `python run_sppr.py` from this directory, or pass the model folder explicitly. The script finds the project root and restores the explicit fate matrix on runtime nonfeeding rows. It does not use the engine’s forced balanced_model copy. Fresh execution replaces diagnostics in this exact candidate, so preserve researcher work first.

Fitted gray values are assumptions, not author-recovered diets. Source fields and inferred removals are distinguished in model_notes.md. `inner` excludes the synthetic imported-diet column; `PP` also excludes both detritus columns. All saved methods retain det_collapse_mode=never.
