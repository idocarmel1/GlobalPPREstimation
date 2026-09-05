import os
import re
import json
import logging
import argparse
import pandas as pd
import numpy as np


class EwEConverter:
    """
    A class to handle conversions between EwE (Ecopath with Ecosim)
    CSV/Excel input formats, JSON, and reconstructed Excel files.
    """

    # Sentinel written wherever the source states no value.
    NO_DATA = "-9999"

    # EwE's own default for unassimilated consumption: applied to blank cells on
    # import, so the respiration/detritus arithmetic has to use it too, or it
    # would test a model different from the one EwE will actually build.
    EWE_DEFAULT_GS = 0.2

    # Gross efficiency (P/Q) range that is normal for a consumer.
    PQ_LO, PQ_HI = 0.02, 0.5

    def __init__(self, log_file=None):
        self.logger = self._setup_logger(log_file)

    def _setup_logger(self, log_file):
        """Sets up a logger that outputs to both a file and the console."""
        logger = logging.getLogger("EwE_Converter")
        logger.setLevel(logging.INFO)

        if logger.hasHandlers():
            logger.handlers.clear()

        formatter = logging.Formatter('%(levelname)s - %(message)s')

        if log_file:
            fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger

    @staticmethod
    def _find_file(directory, keyword):
        """Finds a file in the given directory that contains the keyword in its name.

        Sorted so the choice is deterministic, and an exact stem match wins over
        a substring one: an extraction directory also holds REPORT.md, model.json
        and any *_reconstructed.xlsx from an earlier run, so a bare substring
        search can otherwise pick a different file on a different machine.
        """
        candidates = [
            f for f in sorted(os.listdir(directory))
            if not f.startswith('~$')
            and keyword.lower() in f.lower().replace('_', ' ')
        ]
        if not candidates:
            return None
        for f in candidates:
            stem = os.path.splitext(f)[0].lower().replace('_', ' ')
            if stem == keyword.lower():
                return os.path.join(directory, f)
        return os.path.join(directory, candidates[0])

    @staticmethod
    def _load_data(filepath, header='infer', dtype=None):
        """Loads a CSV or Excel file into a pandas DataFrame."""
        if not filepath:
            return None
        if filepath.endswith('.csv'):
            return pd.read_csv(filepath, header=header, dtype=dtype)
        elif filepath.endswith(('.xls', '.xlsx')):
            xl_header = 0 if header == 'infer' else header
            return pd.read_excel(filepath, header=xl_header, dtype=dtype)
        return None

    @staticmethod
    def _load_metadata(filepath):
        """Loads the metadata file and returns a dictionary of key-value pairs."""
        if not filepath: return {}
        try:
            df = EwEConverter._load_data(filepath, header=None)
            meta = {}
            for _, row in df.iterrows():
                if len(row) >= 2 and pd.notna(row.iloc[0]):
                    key = str(row.iloc[0]).strip().lower()
                    val = str(row.iloc[1]).strip()
                    meta[key] = val
            return meta
        except Exception:
            return {}

    @staticmethod
    def _fmt_derived(x):
        """A derived BA, at 6 significant figures.

        str(float) would print -0.2105263157894737 for a value that came from a
        two-digit source; six figures is more than the DB needs and stops the
        derived form from claiming a precision the stated one never had.
        """
        return f"{float(x):.6g}"

    @staticmethod
    def _fmt_float(f):
        """Safely formats floats to strings, removing trailing .0 if it's an integer."""
        try:
            if float(f) == int(float(f)):
                return str(int(float(f)))
            return str(float(f))
        except (ValueError, TypeError):
            return str(f)

    @classmethod
    def _num(cls, val):
        """JSON string -> float, or None when the field carries no value."""
        if val is None:
            return None
        s = str(val).strip()
        if s == "" or s == cls.NO_DATA:
            return None
        try:
            f = float(s)
        except ValueError:
            return None
        return None if np.isnan(f) else f

    @staticmethod
    def _cell_str(val):
        """A cell read with dtype=str -> its text, or None when blank."""
        if val is None:
            return None
        try:
            if pd.isna(val):
                return None
        except (TypeError, ValueError):
            pass
        s = str(val).strip()
        return s if s != "" else None

    @staticmethod
    def _parse_metadata_from_filename(filename):
        """Attempts to extract Metadata from the LME_Number_Name_(Year).json format."""
        sibling = os.path.join(os.path.dirname(filename), "Metadata.xlsx")
        if os.path.exists(sibling):
            meta = pd.read_excel(sibling, header=None, dtype=str)
            return dict(zip(meta.iloc[:, 0], meta.iloc[:, 1]))
        base = os.path.basename(filename).replace('.json', '')
        match = re.match(r"([^_]+)_(\d+)_([^_]+(?:_[^_]+)*)_\(([^)]+)\)", base)
        if match:
            return {
                'LME': match.group(1),
                'model_number': match.group(2),
                'model_name': match.group(3).replace('_', ' '),
                'model_year': match.group(4)
            }
        return {'Filename': base}

    # ------------------------------------------------------------------
    # Biomass accumulation
    # ------------------------------------------------------------------

    def _load_biomass_accumulation(self, filepath):
        """Reads Biomass_accumulation.csv into {key: (absolute, rate)} as text.

        Columns, per the extraction skill's template:
            ,Group name,Biomass accumulation (t/km^2/year),Biomass accumulation rate (/year)

        Cells are read as text (dtype=str) so a source's "0.10" keeps its
        trailing zero, the same reason write_outputs.py parses with
        parse_float=str. Rows are keyed both by group number and by lower-cased
        group name, so a group is found the same two ways detritus fate is.

        An entirely blank file means no numeric BA was extracted. It is reported
        as unknown, not treated as zero or as proof of steady state.
        """
        if not filepath:
            return {}, 0
        try:
            df = self._load_data(filepath, dtype=str)
        except Exception as exc:
            self.logger.warning(f"Could not read biomass accumulation file: {exc}")
            return {}, 0
        if df is None or df.empty:
            return {}, 0

        cols = [str(c).strip().lower() for c in df.columns]

        def col_index(fragment, fallback):
            for i, c in enumerate(cols):
                if fragment in c:
                    return i
            return fallback if fallback < len(df.columns) else None

        # Match on the header text first; fall back on the template positions.
        # "rate" has to be tested before the bare "biomass accumulation", since
        # the rate header contains it as a prefix.
        i_rate = col_index('accumulation rate', 3)
        i_abs = None
        for i, c in enumerate(cols):
            if 'accumulation' in c and i != i_rate:
                i_abs = i
                break
        if i_abs is None:
            i_abs = 2 if len(df.columns) > 2 else None

        lookup = {}
        filled = 0
        for _, row in df.iterrows():
            raw_seq = self._cell_str(row.iloc[0])
            name = self._cell_str(row.iloc[1]) if len(row) > 1 else None
            absolute = self._cell_str(row.iloc[i_abs]) if i_abs is not None else None
            rate = self._cell_str(row.iloc[i_rate]) if i_rate is not None else None
            if absolute is None and rate is None:
                continue
            filled += 1
            entry = (absolute, rate)
            if raw_seq:
                try:
                    seq = str(int(float(raw_seq)))
                except ValueError:
                    seq = raw_seq
                lookup[('seq', seq)] = entry
            if name:
                lookup[('name', name.lower())] = entry
        return lookup, filled

    def _biomass_accumulation_for(self, lookup, group_seq, group_name,
                                  b_hab_area, hab_area):
        """BA for one group, as (biomass_accum, biomass_accum_rate) JSON strings.

        A blank cell is UNKNOWN, not zero: both fields stay -9999 and nothing
        is derived from nothing. Only a value the source actually states is
        turned into the other form.

        The file states at most one of the two forms per group -- the skill
        forbids converting between them on the way *out*, because the
        conversion needs B and would put B's rounding into a number that then
        looks tabulated. Here we are going the other way, into a JSON that is
        already a derived artefact and that EwE loads as an absolute plus a
        rate, so the missing form is derived from B and the derivation is
        logged. Whichever form the paper stated is passed through verbatim.

        The absolute form is put on the same basis as the JSON's `biomass`
        field, i.e. multiplied by the habitat area, so that
        biomass_accum / biomass == biomass_accum_rate holds in the JSON the way
        it does in EwE. The file's own absolute column is per habitat area,
        matching Basic_input's B column -- that is the basis validate.py
        cross-checks the two columns on.
        """
        entry = lookup.get(('seq', group_seq)) or lookup.get(('name', group_name.lower()))
        if not entry:
            return self.NO_DATA, self.NO_DATA

        abs_txt, rate_txt = entry
        abs_val = self._num(abs_txt)
        rate_val = self._num(rate_txt)

        if abs_val is None and rate_val is None:
            return self.NO_DATA, self.NO_DATA

        b = self._num(b_hab_area)
        area = self._num(hab_area)
        area = 1.0 if area is None else area

        ba_abs, ba_rate = self.NO_DATA, self.NO_DATA

        if abs_val is not None:
            # verbatim when there is nothing to scale, computed otherwise
            ba_abs = abs_txt if area == 1.0 else self._fmt_derived(abs_val * area)
            if area != 1.0:
                self.logger.info(
                    f"    - BA {abs_txt} t/km^2/year is per habitat area; scaled by "
                    f"hab area {area} to {ba_abs} to match the 'biomass' field")
        if rate_val is not None:
            ba_rate = rate_txt

        # Derive whichever form the paper did not print. Needs B.
        if abs_val is not None and rate_val is None:
            if b:
                ba_rate = self._fmt_derived(abs_val / b)
                self.logger.info(
                    f"    - BA rate {ba_rate}/year derived from BA {abs_txt} / B {b} "
                    "(not stated by the source)")
            else:
                self.logger.warning(
                    f"    - BA {abs_txt} given but no biomass, so the BA rate cannot "
                    "be derived")
        elif rate_val is not None and abs_val is None:
            if b:
                ba_abs = self._fmt_derived(rate_val * b * area)
                self.logger.info(
                    f"    - BA {ba_abs} t/km^2/year derived from rate {rate_txt} * B {b}"
                    + (f" * hab area {area}" if area != 1.0 else "")
                    + " (not stated by the source)")
            else:
                self.logger.warning(
                    f"    - BA rate {rate_txt}/year given but no biomass, so the "
                    "absolute BA cannot be derived")
        elif abs_val is not None and rate_val is not None and b:
            # Both printed: they have to agree through B, or one was read from
            # the wrong column. Same cross-check validate.py runs on the file.
            implied = abs_val / b
            if abs(implied - rate_val) > abs(rate_val) * 0.1 + 0.005:
                self.logger.warning(
                    f"    - BA {abs_txt} over B {b} implies a rate of {implied:.4g}"
                    f"/year, but the rate column says {rate_txt}")

        if self._num(ba_abs) is not None or self._num(ba_rate) is not None:
            self.logger.info(
                f"    - Biomass accumulation: {ba_abs} t/km^2/year, {ba_rate} /year")
        return ba_abs, ba_rate

    # ------------------------------------------------------------------
    # Mass balance
    # ------------------------------------------------------------------

    def check_mass_balance(self, groups_json, discards_total=0.0, ee_tol=0.05):
        """Check the assembled model against the two Ecopath master equations.

            production:  B(P/B)EE = Y + BA + SUM_j B_j (Q/B)_j DC_ji
            energy:      Q        = P + R + GS*Q

        so EE can be recomputed from the diet matrix, the biomasses, the
        catches and the biomass accumulation, and compared with what the paper
        printed. Published models are balanced, so a group that comes out
        consuming more than it produces is usually a mis-parsed number, not a
        real imbalance -- a Q/B read from the neighbouring column, a catch left
        in absolute tonnes, a diet proportion under the wrong predator.

        A blank BA is UNKNOWN, not zero. Where BA is unknown the recomputation
        is run without it and the result is reported as INDETERMINATE rather
        than as a mismatch: the gap could be an extraction error or it could be
        exactly the BA the source never printed, and the check cannot tell
        which. Only where BA is known does a gap become a warning and an EE > 1
        an error. A group whose EE reconciles at BA = 0 is consistent with
        steady state, which is not the same as being shown to be steady state.

        Everything here reads the JSON's own `biomass` field, which is already
        B * habitat area, so biomass, catch and BA are all on the model-area
        basis the equation needs.

        Returns a findings dict; nothing is written back into the model.
        """
        errors, warnings, notes = [], [], []
        by_seq = {g["group_seq"]: g for g in groups_json}

        # consumption per consumer, and the diet matrix as {predator: {prey: dc}}
        Q, DC = {}, {}
        for g in groups_json:
            seq = g["group_seq"]
            b, qb = self._num(g.get("biomass")), self._num(g.get("qb"))
            if b is not None and qb is not None and qb > 0:
                Q[seq] = b * qb
            diet = (g.get("diet_descr") or {}).get("diet")
            if diet is None:
                diet = []
            elif isinstance(diet, dict):
                diet = [diet]
            entries = {}
            for item in diet:
                p = self._num(item.get("proportion"))
                if p:
                    entries[str(item.get("prey_seq"))] = p
            if entries:
                DC[seq] = entries

        for g in groups_json:
            seq, name = g["group_seq"], g["group_name"]
            qb = self._num(g.get("qb"))
            if qb and qb > 0 and seq not in DC:
                errors.append(
                    f"group {seq} ({name}) has Q/B={g['qb']} but no diet entries - "
                    "its consumption is missing from every prey's budget")

        missing_q = [c for c in DC if c not in Q]
        if missing_q:
            notes.append(
                f"{len(missing_q)} consumer(s) lack B or Q/B, so predation on their "
                "prey is under-counted and every recomputed EE below is a lower "
                "bound: " + ", ".join(
                    f"{c} ({by_seq[c]['group_name']})" for c in missing_q[:6]))

        detritus = {g["group_seq"] for g in groups_json if g.get("pp") == "2"}

        rows, ee_used, all_four = [], {}, []
        indeterminate = []
        for g in groups_json:
            seq, name = g["group_seq"], g["group_name"]
            b = self._num(g.get("biomass"))
            pb = self._num(g.get("pb"))
            qb = self._num(g.get("qb"))
            ee = self._num(g.get("ee"))
            gs = self._num(g.get("gs"))
            ba_val = self._num(g.get("biomass_accum"))
            ba_known = ba_val is not None
            ba = ba_val if ba_known else 0.0
            y = self._num(g.get("export")) or 0.0

            pred = sum(Q.get(c, 0.0) * DC.get(c, {}).get(seq, 0.0) for c in DC)
            prod = b * pb if (b is not None and pb is not None) else None
            ee_calc = (y + ba + pred) / prod if prod else None

            # What BA would reconcile the recomputation with the printed EE.
            # Reported, never written back: a number this check invented and
            # then validated itself against would be worthless.
            need = ((ee - ee_calc) * prod
                    if (ee_calc is not None and ee is not None and prod) else None)
            need_txt = ""
            if need is not None and abs(need) < abs(prod):
                need_txt = (f" - a BA of {need:+.4g} t/km^2/year "
                            f"({need / prod:+.2f} of production) would close it")

            over = ee_calc is not None and ee_calc > 1.0
            gap = (ee_calc is not None and ee is not None
                   and abs(ee_calc - ee) > ee_tol)

            if ba_known:
                if over:
                    errors.append(
                        f"group {seq} ({name}): recomputed EE = {ee_calc:.3f} > 1 - "
                        f"catch+BA+predation ({y + ba + pred:.4g}) exceeds production "
                        f"({prod:.4g})")
                if gap:
                    warnings.append(
                        f"group {seq} ({name}): printed EE {g['ee']} vs recomputed "
                        f"{ee_calc:.3f} (diff {abs(ee_calc - ee):.3f}), BA "
                        f"{g['biomass_accum']} carried")
            else:
                if over:
                    indeterminate.append(
                        f"group {seq} ({name}): recomputed EE = {ee_calc:.3f} > 1 "
                        "without BA, and BA is unknown"
                        + (need_txt or "") + " - undecidable until the source is "
                        "checked for biomass accumulation")
                elif gap:
                    indeterminate.append(
                        f"group {seq} ({name}): printed EE {g['ee']} vs recomputed "
                        f"{ee_calc:.3f} (diff {abs(ee_calc - ee):.3f}) with BA "
                        "unknown" + (need_txt or "")
                        + " - undecidable: this may be an extraction error or the "
                        "BA the source never printed")

            ee_used[seq] = ee if ee is not None else ee_calc

            pq = None
            if seq not in detritus:
                if pb and qb:
                    pq = pb / qb
                if pq is not None:
                    gs_eff = gs if gs is not None else self.EWE_DEFAULT_GS
                    if pq >= 1 - gs_eff:
                        errors.append(
                            f"group {seq} ({name}): P/Q = {pq:.3f} with GS = {gs_eff} "
                            f"implies non-positive respiration (needs P/Q < "
                            f"{1 - gs_eff:.2f})")
                    elif not (self.PQ_LO <= pq <= self.PQ_HI):
                        warnings.append(
                            f"group {seq} ({name}): P/Q = {pq:.3f} outside the usual "
                            f"{self.PQ_LO}-{self.PQ_HI} range - check the P/B and Q/B "
                            "columns")

                known = sum(1 for v in (b, pb, qb, ee) if v is not None)
                if known < 3:
                    have = [k for k, v in (("B", b), ("P/B", pb), ("Q/B", qb),
                                           ("EE", ee)) if v is not None]
                    warnings.append(
                        f"group {seq} ({name}): only {known} of B/P-B/Q-B/EE given "
                        f"({', '.join(have) or 'none'}) - Ecopath needs three")
                elif known == 4:
                    all_four.append(f"{seq} ({name})")

            rows.append({"seq": seq, "name": name, "B": b, "PB": pb, "QB": qb,
                         "EE": ee, "EE_calc": ee_calc, "PQ": pq, "catch": y,
                         "BA": ba_val, "BA_known": ba_known,
                         "detritus": seq in detritus})

        # One line, not one per group: in this corpus the source usually prints
        # all four, so the per-group form buries every other finding.
        if all_four:
            notes.append(
                f"{len(all_four)} group(s) carry all four of B/P-B/Q-B/EE - Ecopath "
                "needs three, so one of them is probably a published model estimate "
                "rather than an input; record which in REPORT.md: "
                + ", ".join(all_four[:8]) + (" ..." if len(all_four) > 8 else ""))

        # ---- detritus pools ----
        if detritus:
            inflow = 0.0
            for g in groups_json:
                seq = g["group_seq"]
                if seq in detritus:
                    continue
                b, pb = self._num(g.get("biomass")), self._num(g.get("pb"))
                ee = ee_used.get(seq)
                if b is not None and pb is not None and ee is not None and ee <= 1:
                    inflow += b * pb * (1 - ee)              # other mortality
                if seq in Q:
                    gs = self._num(g.get("gs"))
                    inflow += Q[seq] * (gs if gs is not None else self.EWE_DEFAULT_GS)
            for g in groups_json:                            # detritus import
                if g["group_seq"] in detritus:
                    inflow += self._num(g.get("detritus_import")) or 0.0
            inflow += discards_total                         # discarded catch
            outflow = sum(Q.get(c, 0.0) * DC.get(c, {}).get(dseq, 0.0)
                          for c in DC for dseq in detritus)
            if inflow > 0:
                notes.append(
                    f"detritus pools ({len(detritus)}): inflow ~{inflow:.4g}, "
                    f"consumption ~{outflow:.4g} t/km^2/year, implied EE "
                    f"~{outflow / inflow:.3f} (indicative - export is not separated, "
                    "it uses recomputed EE where the source gave none, and any "
                    "unknown BA is left out of the flows entirely)")
                if outflow > inflow:
                    errors.append(
                        f"detritus consumption ({outflow:.4g}) exceeds detritus "
                        f"inflow ({inflow:.4g}) - the pools cannot balance as "
                        "extracted")

        n_unknown = sum(1 for r in rows if not r["BA_known"])
        if errors:
            verdict = "NOT BALANCED"
        elif indeterminate:
            verdict = "INDETERMINATE"
        else:
            verdict = "BALANCED"
        return {"verdict": verdict, "balanced": verdict == "BALANCED",
                "ee_tol": ee_tol, "errors": errors, "warnings": warnings,
                "indeterminate": indeterminate, "notes": notes, "rows": rows,
                "ba_unknown": n_unknown, "n_groups": len(rows)}

    def report_mass_balance(self, findings, model_name, out_path=None):
        """Log the findings and write the REPORT.md 'Mass balance' section."""
        verdict = findings["verdict"]
        self.logger.info(f"\n--- Mass balance check: {verdict} ---")
        self.logger.info(
            f"BA is unknown (-9999) for {findings['ba_unknown']} of "
            f"{findings['n_groups']} group(s); those groups cannot be decided "
            "unless they reconcile without it.")
        for m in findings["notes"]:
            self.logger.info(f"NOTE  {m}")
        for m in findings["indeterminate"]:
            self.logger.warning(f"INDET {m}")
        for m in findings["warnings"]:
            self.logger.warning(f"WARN  {m}")
        for m in findings["errors"]:
            self.logger.error(f"ERROR {m}")
        self.logger.info(
            f"{len(findings['errors'])} error(s), "
            f"{len(findings['indeterminate'])} indeterminate, "
            f"{len(findings['warnings'])} warning(s), "
            f"{len(findings['notes'])} note(s)")
        if findings["errors"]:
            self.logger.info(
                "Check each error against a rendered image of the source page "
                "before changing anything. Do not adjust numbers to make this pass.")
        if findings["indeterminate"]:
            self.logger.info(
                "An indeterminate group is a prompt to go back to the source for "
                "biomass accumulation, not a BA to enter. A BA this check suggested "
                "and then validated itself against would prove nothing.")

        if not out_path:
            return None

        rows = findings["rows"]
        diffs = [(abs(r["EE_calc"] - r["EE"]), r) for r in rows
                 if r["EE_calc"] is not None and r["EE"] is not None]
        over = [r for r in rows if r["EE_calc"] is not None and r["EE_calc"] > 1]
        pq_out = [r for r in rows if r["PQ"] is not None
                  and not (self.PQ_LO <= r["PQ"] <= self.PQ_HI)]
        ba_rows = [r for r in rows if r["BA_known"]]

        L = ["## Mass balance", "",
             f"Checked by the source-preserving local copy of `database_json.py` on the assembled JSON for "
             f"{model_name}, EE tolerance {findings['ee_tol']}.", "",
             f"**Verdict: {verdict}** - {len(findings['errors'])} error(s), "
             f"{len(findings['indeterminate'])} indeterminate, "
             f"{len(findings['warnings'])} warning(s), "
             f"{len(findings['notes'])} note(s).", "",
             f"Biomass accumulation is unknown (-9999) for "
             f"{findings['ba_unknown']} of {findings['n_groups']} group(s). A blank "
             "BA cell is treated as unknown, never as zero, so a group whose EE "
             "reconciles without BA is *consistent with* steady state rather than "
             "shown to be steady state, and a group whose EE does not reconcile is "
             "undecidable rather than wrong.", ""]

        if diffs:
            d, r = max(diffs, key=lambda t: t[0])
            L.append(f"Recomputed vs printed EE: max difference {d:.3f}, "
                     f"group {r['seq']} ({r['name']}).")
        else:
            L.append("Recomputed vs printed EE: no group has both a printed EE and "
                     "enough inputs to recompute one.")
        L.append("")
        L.append("Groups with recomputed EE > 1: "
                 + (", ".join(f"{r['seq']} ({r['name']}, {r['EE_calc']:.3f})"
                              for r in over) if over else "none") + ".")
        L.append("")
        L.append("P/Q outside 0.02-0.5: "
                 + (", ".join(f"{r['seq']} ({r['name']}, {r['PQ']:.3f})"
                              for r in pq_out) if pq_out else "none") + ".")
        L.append("")
        if ba_rows:
            L.append(f"BA: carried for {len(ba_rows)} group(s) from "
                     "`Biomass_accumulation.csv`, so the check accounts for it - "
                     + ", ".join(f"{r['seq']} ({r['name']}, {r['BA']:+.4g})"
                                 for r in ba_rows) + ". The remaining "
                     f"{findings['ba_unknown']} group(s) carry -9999 and are "
                     "undecided where their EE does not reconcile without BA.")
        else:
            L.append("BA: not stated for any group. Every EE below is recomputed "
                     "without a BA term, which is a lower bound on what the model "
                     "may actually contain, not a steady-state result.")
        L.append("")
        L.append("Migration (E) reported by the source: not represented in these "
                 "files; where a source reports it the recomputed EE will "
                 "legitimately differ.")
        L.append("")

        for label, items in (("Errors", findings["errors"]),
                             ("Indeterminate (BA unknown)", findings["indeterminate"]),
                             ("Warnings", findings["warnings"]),
                             ("Notes", findings["notes"])):
            if items:
                L += [f"### {label}", ""] + [f"- {m}" for m in items] + [""]

        L += ["### Per-group recomputation", "",
              "`EE calc` is computed without a BA term wherever BA is unknown.", "",
              "| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        fm = lambda v, p=4: "-" if v is None else f"{v:.{p}g}"
        for r in rows:
            ba_txt = fm(r["BA"]) if r["BA_known"] else "unknown"
            L.append(f"| {r['seq']} | {r['name']} | {fm(r['B'])} | {fm(r['PB'])} | "
                     f"{fm(r['QB'])} | {fm(r['EE'])} | {fm(r['EE_calc'], 3)} | "
                     f"{fm(r['PQ'], 3)} | {fm(r['catch'])} | {ba_txt} |")
        L.append("")

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(L))
        self.logger.info(f"Mass balance section written to {out_path}")
        return out_path

    @staticmethod
    def update_report(report_path, section_path):
        """Replace the '## Mass balance' section of an existing REPORT.md."""
        if not (os.path.exists(report_path) and os.path.exists(section_path)):
            return False
        report = open(report_path, encoding='utf-8').read()
        section = open(section_path, encoding='utf-8').read().rstrip() + "\n"
        pattern = re.compile(r"^## Mass balance\b.*?(?=^## |\Z)", re.S | re.M)
        new = pattern.sub(section, report) if pattern.search(report) \
            else report.rstrip() + "\n\n" + section
        open(report_path, 'w', encoding='utf-8').write(new)
        return True

    # ------------------------------------------------------------------

    def csv_to_json(self, input_dir, ee_tol=0.05, update_report=False):
        """
        Reads CSV/Excel EwE input files from a directory and converts them into a JSON model.
        Returns the path to the generated JSON file.
        """
        # 1. Locate Files
        files = {
            'basic': self._find_file(input_dir, 'basic input'),
            'diet': self._find_file(input_dir, 'diet composition'),
            'detritus': self._find_file(input_dir, 'detritus fate'),
            'discards': self._find_file(input_dir, 'discards'),
            'landings': self._find_file(input_dir, 'landings'),
            'biomass_accum': self._find_file(input_dir, 'biomass accumulation'),
            'tl': self._find_file(input_dir, 'tl'),
            'taxonomy': self._find_file(input_dir, 'taxonomy'),
            'metadata': self._find_file(input_dir, 'metadata')
        }

        # Update logger file path to current directory
        log_file = os.path.join(input_dir, "ewe_conversion.log")
        self.logger = self._setup_logger(log_file)
        self.logger.info(f"Starting conversion for directory: {input_dir}")

        # Check Mandatory Files
        if not files['basic']:
            self.logger.error("Mandatory file 'Basic input' not found. Aborting.")
            return None
        if not files['diet']:
            self.logger.error("Mandatory file 'Diet composition' not found. Aborting.")
            return None
        if not files['metadata']:
            self.logger.error("Mandatory file 'metadata' not found. Aborting.")
            return None

        # Handle Output Filename via Metadata
        meta_dict = self._load_metadata(files['metadata'])
        if meta_dict:
            mod_year = meta_dict.get('model_year', 'Year')
            mod_num = meta_dict.get('model_number', '00000')
            mod_name = meta_dict.get('model_name', 'Model')
            # A year already trailing the model name is not repeated, and spaces
            # become underscores in the LME too -- the same two rules
            # write_outputs.py applies when it names the model directory, so a
            # metadata block of LME "22 North Sea" / model_name "North Sea 1981"
            # gives 22_North_Sea_680_North_Sea_(1981).json rather than
            # "22 North Sea_680_North_Sea_1981_(1981).json".
            if mod_year:
                mod_name = re.sub(r"[\s_(\[-]*" + re.escape(str(mod_year)) + r"[)\]]*\s*$",
                                  "", mod_name)
            lme = str(meta_dict.get('lme', 'LME')).strip().replace(' ', '_')
            mod_name = mod_name.strip().replace(' ', '_')
            out_filename = f"{lme}_{mod_num}_{mod_name}_({mod_year}).json"
        else:
            out_filename = "ewe_model_output.json"

        output_json = os.path.join(input_dir, out_filename)
        self.logger.info(f"Output will be saved as: {out_filename}")

        # 2. Load DataFrames
        dfs = {k: self._load_data(v) for k, v in files.items()
               if k not in ('metadata', 'biomass_accum')}

        df_basic = dfs['basic'].dropna(how='all')
        df_diet = dfs['diet'].fillna(0) if dfs['diet'] is not None else None
        df_detritus = dfs['detritus']

        df_landings = dfs['landings'].set_index(dfs['landings'].columns[1]) if dfs[
                                                                                   'landings'] is not None else pd.DataFrame()
        df_discards = dfs['discards'].set_index(dfs['discards'].columns[1]) if dfs[
                                                                                   'discards'] is not None else pd.DataFrame()
        df_tax = dfs['taxonomy'].set_index(dfs['taxonomy'].columns[1]) if dfs[
                                                                              'taxonomy'] is not None else pd.DataFrame()

        # Biomass accumulation. A missing or blank cell means UNKNOWN, never
        # zero: the mass balance check below reports those groups as
        # indeterminate rather than silently assuming steady state.
        ba_lookup, ba_filled = self._load_biomass_accumulation(files['biomass_accum'])
        if not files['biomass_accum']:
            self.logger.warning(
                "No 'Biomass accumulation' file found. BA is UNKNOWN for every "
                "group (-9999); the mass balance check below cannot decide any "
                "group whose EE does not already reconcile without it.")
        elif ba_filled == 0:
            self.logger.info(
                f"Biomass accumulation file {os.path.basename(files['biomass_accum'])} "
                "is entirely blank: BA is UNKNOWN for every group (-9999), not zero.")
        else:
            self.logger.info(
                f"Biomass accumulation loaded for {ba_filled} group(s) from "
                f"{os.path.basename(files['biomass_accum'])}")

        # Pre-build a Name-to-Seq mapping
        name_to_seq = {}
        for idx, row in df_basic.iterrows():
            g_name = str(row.iloc[1]).strip()
            if pd.isna(row.iloc[0]) or g_name == 'nan':
                continue

            # IDENTIFICATION FIX: Skip Fleets/Fisheries
            # If Biomass (3), P/B (5), Q/B (6), and EE (7) are ALL NaN, it is not a biological group.
            if pd.isna(row.iloc[3]) and pd.isna(row.iloc[5]) and pd.isna(row.iloc[6]) and pd.isna(row.iloc[7]):
                continue

            raw_gseq = str(row.iloc[0]).strip()
            try:
                g_seq = str(int(float(raw_gseq)))
            except ValueError:
                g_seq = raw_gseq
            name_to_seq[g_name.lower()] = g_seq

        groups_json = []

        # 3. Process Each Group
        for idx, row in df_basic.iterrows():
            raw_gseq = str(row.iloc[0]).strip()
            try:
                group_seq = str(int(float(raw_gseq)))
            except ValueError:
                group_seq = raw_gseq

            group_name = str(row.iloc[1]).strip()

            if pd.isna(row.iloc[0]) or group_name == 'nan':
                continue

            # IDENTIFICATION FIX: Skip Fleets/Fisheries
            if pd.isna(row.iloc[3]) and pd.isna(row.iloc[5]) and pd.isna(row.iloc[6]) and pd.isna(row.iloc[7]):
                continue

            self.logger.info(f"Processing group: {group_name} (ID: {group_seq})")

            def get_val(val):
                if pd.isna(val) or str(val).strip() == '':
                    return self.NO_DATA, "false"
                return str(val), "true"

            biomass_hab_area, b_input = get_val(row.iloc[3])
            pb, pb_input = get_val(row.iloc[5])
            qb, qb_input = get_val(row.iloc[6])
            ee, ee_input = get_val(row.iloc[7])
            other_mort, _ = get_val(row.iloc[8] if len(row) > 8 else np.nan)
            gs, _ = get_val(row.iloc[10] if len(row) > 10 else np.nan)
            det_import, _ = get_val(row.iloc[11] if len(row) > 11 else np.nan)
            hab_area = str(row.iloc[2]) if not pd.isna(row.iloc[2]) else "1"
            # -9999 is a sentinel, not a biomass: scaling it by the habitat area
            # would turn "no value" into a number (-2179.98 at hab area 0.218).
            if b_input == "false":
                biomass = self.NO_DATA
            else:
                biomass = str(float(biomass_hab_area) * float(hab_area))

            # Biomass accumulation for this group
            biomass_accum, biomass_accum_rate = self._biomass_accumulation_for(
                ba_lookup, group_seq, group_name, biomass_hab_area, hab_area)

            # A. Compile Real Diet FIRST
            raw_diet = []
            diet_sum = 0.0
            import_val = 0.0

            if df_diet is not None:
                df_diet_cols_str = [str(c).strip() for c in df_diet.columns]
                predator_col = None

                if group_seq in df_diet_cols_str:
                    predator_col = df_diet.columns[df_diet_cols_str.index(group_seq)]
                elif group_name in df_diet_cols_str:
                    predator_col = df_diet.columns[df_diet_cols_str.index(group_name)]

                if predator_col is not None:
                    for diet_idx, diet_row in df_diet.iterrows():
                        raw_prey_seq = str(diet_row.iloc[0]).strip()
                        prey_name = str(diet_row.iloc[1]).strip().lower() if len(diet_row) > 1 else ""

                        try:
                            proportion = float(diet_row[predator_col])
                        except (ValueError, TypeError, KeyError):
                            proportion = 0.0

                        try:
                            prey_seq = str(int(float(raw_prey_seq)))
                        except ValueError:
                            prey_seq = raw_prey_seq.lower()

                        if prey_seq == 'import' or prey_name == 'import':
                            import_val = proportion
                            continue

                        # The skill writes the trailing rows as 'Import', 'Sum'
                        # and '(1 - Sum)'. '(1 - sum)' has to be named here: it
                        # carries a positive value wherever a published column
                        # does not reach 1, and would otherwise be picked up as
                        # a prey item.
                        if prey_seq in ['sum', '1-sum', '(1 - sum)', '0'] or \
                                prey_name in ['sum', '1-sum', '(1 - sum)']:
                            continue

                        if proportion > 0:
                            raw_diet.append({
                                "prey_seq": prey_seq,
                                "proportion_val": proportion
                            })
                            diet_sum += proportion

            # B. Diet & Import Normalization
            total_diet_sum = diet_sum + import_val
            norm_factor = 1.0

            if total_diet_sum > 0:
                self.logger.info(f"    - Total Diet + Import sum for {group_name}: {total_diet_sum:.5f}")
                needs_normalization = not np.isclose(total_diet_sum, 1.0, atol=1e-6)
                if needs_normalization:
                    self.logger.warning(f"    - Diet Sum is not 1 ({total_diet_sum:.5f}). Preserving published fractions")
                norm_factor = 1.0  # Preserve published diet fractions; extraction rule.
                import_val = import_val * norm_factor

            # C. Merge Diet and Detritus Fate
            group_diet_map = {}

            # 1. Insert normalized real prey items
            for d in raw_diet:
                final_prop = d["proportion_val"] * norm_factor
                group_diet_map[d["prey_seq"]] = {
                    "proportion": final_prop,
                    "detritus_fate": 0.0
                }

            # 2. Insert Detritus Fate (Routing Proportions)
            export_fate = 0.0
            if df_detritus is not None:
                det_row = None
                match_by_seq = df_detritus[
                    df_detritus.iloc[:, 0].astype(str).str.strip().str.replace(r'\.0$', '', regex=True) == group_seq]
                if not match_by_seq.empty:
                    det_row = match_by_seq.iloc[0]
                else:
                    match_by_name = df_detritus[
                        df_detritus.iloc[:, 1].astype(str).str.strip().str.lower() == group_name.lower()]
                    if not match_by_name.empty:
                        det_row = match_by_name.iloc[0]

                if det_row is not None:
                    for col in df_detritus.columns:
                        col_str = str(col).strip().lower()
                        if col_str in name_to_seq:
                            try:
                                fate_val = float(det_row[col])
                            except:
                                fate_val = 0.0

                            if fate_val > 0:
                                p_seq = name_to_seq[col_str]
                                if p_seq not in group_diet_map:
                                    group_diet_map[p_seq] = {"proportion": 0.0, "detritus_fate": fate_val}
                                else:
                                    group_diet_map[p_seq]["detritus_fate"] = fate_val
                        elif col_str == 'export':
                            # Detritus routed out of the system has no prey_seq
                            # to hang off, but it is still part of the row's 1.0
                            # -- leaving it out would inflate the pool fates on
                            # normalization.
                            try:
                                export_fate = float(det_row[col]) or 0.0
                            except:
                                export_fate = 0.0
                            if np.isnan(export_fate):
                                export_fate = 0.0

            # 3. Validate and Normalize Detritus Fate sum
            if df_detritus is not None and len(group_diet_map) > 0:
                det_fate_sum = sum(vals["detritus_fate"] for vals in group_diet_map.values())
                total_fate = det_fate_sum + export_fate

                if export_fate > 0:
                    self.logger.info(
                        f"    - Detritus fate sum for {group_name}: {det_fate_sum:.5f} "
                        f"to pools + {export_fate:.5f} to Export = {total_fate:.5f}")
                else:
                    self.logger.info(f"    - Detritus fate sum for {group_name}: {det_fate_sum:.5f}")

                if det_fate_sum > 0 and not np.isclose(total_fate, 1.0, atol=1e-6):
                    self.logger.warning(
                        f"    - Detritus fate sum is not 1 ({total_fate:.5f}). Normalizing to 1.0")
                    det_norm_factor = 1.0 / total_fate
                    for p_seq in group_diet_map:
                        group_diet_map[p_seq]["detritus_fate"] *= det_norm_factor
                elif det_fate_sum == 0.0 and export_fate == 0.0:
                    self.logger.warning(f"    - Missing Detritus fate routing for {group_name} (Sum = 0.0)")

            # 4. Convert Map to JSON list
            diet_list = []
            for p_seq, vals in group_diet_map.items():
                diet_list.append({
                    "prey_seq": p_seq,
                    "proportion": self._fmt_float(vals["proportion"]),
                    "detritus_fate": self.NO_DATA if vals["detritus_fate"] == 0.0 else self._fmt_float(vals["detritus_fate"])
                })

            # D. Primary Producer & Detritus Identification
            is_detritus_group = False
            if df_detritus is not None:
                det_cols = [str(c).strip().lower() for c in df_detritus.columns]
                if group_name.lower() in det_cols:
                    is_detritus_group = True
            elif any(keyword in group_name.lower() for keyword in ["detritus", "offal", "discard", "carcass"]):
                is_detritus_group = True

            is_pp_candidate = (qb_input == "false") or (float(qb) == 0.0)
            has_diet = (total_diet_sum > 0)

            if is_detritus_group:
                pp_flag = "2"
                self.logger.info(f"    -> Identified as Detritus group (pp = 2).")
            elif is_pp_candidate and not has_diet:
                pp_flag = "1"
                self.logger.info(f"    -> Identified as Primary Producer (pp = 1).")
            elif is_pp_candidate and has_diet:
                pp_flag = "0"
                self.logger.warning(f"    -> VALIDATION CONFLICT: Missing Q/B value, but has diet inputs!")
            elif not is_pp_candidate and not has_diet:
                pp_flag = "0"
                self.logger.warning(f"    -> VALIDATION CONFLICT: Has Q/B value ({qb}), but diet is empty!")
            else:
                pp_flag = "0"

            # E. Log missing parameters
            if b_input == "false": self.logger.warning(f"    - Missing Biomass for {group_name}")
            if pb_input == "false" and pp_flag != "2": self.logger.warning(f"    - Missing P/B for {group_name}")
            if ee_input == "false": self.logger.warning(f"    - Missing EE for {group_name}")
            if qb_input == "false" and pp_flag == "0": self.logger.warning(f"    - Missing Q/B for {group_name}")

            # Calculate Export (Landings + Discards)
            # A blank Total is a group with no catch, not a NaN to propagate:
            # write_outputs.py leaves Total empty where a row has no fleet
            # entries, and float(nan or 0) is nan, which would reach the JSON
            # as the string "nan".
            def catch_total(df, name):
                if name not in df.index or 'Total' not in df.columns:
                    return 0.0
                v = df.loc[name, 'Total']
                if isinstance(v, pd.Series):
                    self.logger.warning(
                        f"    - Group name {name!r} appears more than once in a catch "
                        "file; summing the rows")
                    v = v.astype(float).sum()
                try:
                    v = float(v)
                except (TypeError, ValueError):
                    return 0.0
                return 0.0 if np.isnan(v) else v

            export_val = catch_total(df_landings, group_name) + \
                catch_total(df_discards, group_name)

            # Taxonomy Description
            taxon_descr = None
            if not df_tax.empty and group_name in df_tax.index:
                taxon_descr = str(df_tax.loc[group_name].iloc[-1])

            # Assemble Group JSON Object
            group_obj = {
                "group_name": group_name,
                "group_seq": group_seq,
                "habitat_area": str(row.iloc[2]) if not pd.isna(row.iloc[2]) else self.NO_DATA,
                "biomass_habitat_area": biomass_hab_area,
                "b_hab_area_input": b_input,
                "biomass": biomass,
                "vbk": self.NO_DATA,
                "pb": pb,
                "pb_input": pb_input,
                "ee": ee,
                "ee_input": ee_input,
                "biomass_accum": biomass_accum,
                "biomass_accum_rate": biomass_accum_rate,
                "qb": qb,
                "qb_input": qb_input,
                "pp": pp_flag,
                "detritus_import": det_import if det_import else "0",
                "respiration": self.NO_DATA,
                "immigration": self.NO_DATA,
                "emigration": self.NO_DATA,
                "emigration_rate": self.NO_DATA,
                "other_mort": other_mort,
                "export": self._fmt_float(export_val) if export_val else "0",
                "gs": gs if gs else self.NO_DATA,
                "shadow_price": self.NO_DATA,
                "ge": get_val(row.iloc[9])[0],
                "ge_input": get_val(row.iloc[9])[1],
                "diet_imp": self._fmt_float(import_val) if import_val else "0",
                "diet_descr": {"diet": diet_list if len(diet_list) > 1 else (diet_list[0] if diet_list else None)},
                "taxon_descr": taxon_descr,
                "pedigree_assignment_descr": None
            }

            if not group_obj["diet_descr"]["diet"]:
                group_obj["diet_descr"] = None

            groups_json.append(group_obj)

        # 4. Save to JSON
        final_json = {"group": groups_json}
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, indent=4)

        self.logger.info(f"\nSuccess: Output saved to {output_json}")

        # 5. Mass balance. The verdict stays out of the JSON: it is a property of
        # the extraction, not of the model EwE loads.
        discards_total = 0.0
        if not df_discards.empty and 'Total' in df_discards.columns:
            discards_total = float(
                pd.to_numeric(df_discards['Total'], errors='coerce').fillna(0).sum())
        findings = self.check_mass_balance(groups_json, discards_total, ee_tol)
        section = os.path.join(input_dir, "MASS_BALANCE.md")
        model_label = os.path.splitext(out_filename)[0]
        self.report_mass_balance(findings, model_label, section)
        if update_report:
            report_path = os.path.join(input_dir, "REPORT.md")
            if self.update_report(report_path, section):
                self.logger.info(f"Updated the 'Mass balance' section of {report_path}")
            else:
                self.logger.warning(
                    "--update-report was given but no REPORT.md was found here")

        self.logger.info(f"Log saved to {log_file}")
        return output_json

    def json_to_excel(self, json_path, output_excel=None):
        """
        Reads a JSON EwE model and reconstructs it into a multi-sheet Excel file.
        """
        if output_excel is None:
            output_excel = json_path.replace('.json', '_reconstructed.xlsx')

        self.logger.info(f"Reading JSON: {json_path}")
        with open(json_path, 'r') as f:
            data = json.load(f)

        groups = data.get('group', [])
        if not groups:
            self.logger.error("Error: No groups found in JSON.")
            return None

        # --- Prepare Trackers & Data Structures ---
        basic_rows = []
        tax_rows = []
        tl_rows = []
        landings_rows = []
        ba_rows = []

        group_ids = [g['group_seq'] for g in groups]
        group_names = {g['group_seq']: g['group_name'] for g in groups}

        # Matrices
        diet_matrix = pd.DataFrame(0.0, index=group_ids + ['Import'], columns=group_ids)
        det_fate_matrix = pd.DataFrame(np.nan, index=group_ids, columns=group_ids)

        has_tax = False
        has_tl = False
        has_export = False
        has_ba = False
        detritus_pools = set()

        def parse_val(val):
            """Converts -9999 back to a blank/None representation"""
            if pd.isna(val) or val == self.NO_DATA or val is None:
                return ""
            try:
                return float(val) if '.' in str(val) else int(val)
            except ValueError:
                return val

        # --- 1. Iterate through JSON to populate structures ---
        for g in groups:
            g_seq = g['group_seq']
            g_name = g['group_name']

            # Basic Input
            basic_rows.append({
                'Group seq': parse_val(g_seq),
                'Group name': g_name,
                'Hab area (proportion)': parse_val(g.get('habitat_area')),
                'Biomass in habitat area (t/km^2)': parse_val(g.get('biomass_habitat_area')),
                'Production / biomass (/year)': parse_val(g.get('pb')),
                'Consumption / biomass (/year)': parse_val(g.get('qb')),
                'Ecotrophic Efficiency': parse_val(g.get('ee')),
                'Production / consumption': parse_val(g.get('ge')),
                'Other mortality': parse_val(g.get('other_mort')),
                'Unassim. consumption': parse_val(g.get('gs')),
                'Detritus import (t/km^2/year)': parse_val(g.get('detritus_import'))
            })

            # Biomass accumulation
            ba_abs = parse_val(g.get('biomass_accum'))
            ba_rate = parse_val(g.get('biomass_accum_rate'))
            if ba_abs != "" or ba_rate != "":
                has_ba = True
            ba_rows.append({
                'Group seq': g_seq,
                'Group name': g_name,
                'Biomass accumulation (t/km^2/year)': ba_abs,
                'Biomass accumulation rate (/year)': ba_rate,
            })

            # Export (Represents Landings + Discards)
            exp_val = float(g.get('export', 0))
            if exp_val > 0:
                has_export = True
            landings_rows.append({'Group seq': g_seq, 'Group name': g_name, 'Total': parse_val(g.get('export', 0))})

            # Taxonomy
            td = g.get('taxon_descr')
            if td and td != "None":
                has_tax = True
                tax_rows.append({'Group seq': g_seq, 'Group name': g_name, 'Taxon Description': td})

            # TL (If available in the extended JSON)
            tl = g.get('tl')
            if tl and tl != self.NO_DATA:
                has_tl = True
                tl_rows.append({'Group seq': g_seq, 'Group name': g_name, 'TL': parse_val(tl)})

            # Detritus identification
            if g.get('pp') == "2":
                detritus_pools.add(g_seq)

            # Diet & Detritus Fate Mapping
            import_val = float(g.get('diet_imp', 0))
            if import_val > 0:
                diet_matrix.at['Import', g_seq] = import_val

            diet_info = g.get('diet_descr')
            if diet_info and diet_info.get('diet'):
                d_list = diet_info['diet']
                if isinstance(d_list, dict):  # Handle case where there's only one prey item
                    d_list = [d_list]

                for item in d_list:
                    prey = str(item['prey_seq'])
                    prop = float(item.get('proportion', 0))
                    fate = float(item.get('detritus_fate', 0))

                    # Assign Diet
                    if prop > 0 and prey in diet_matrix.index:
                        diet_matrix.at[prey, g_seq] = prop

                    # Assign Detritus Fate Routing
                    if fate > 0:
                        detritus_pools.add(prey)
                        if prey in det_fate_matrix.columns:
                            det_fate_matrix.at[g_seq, prey] = fate

        # --- 2. Build and Save DataFrames to Excel ---
        self.logger.info(f"Writing reconstructed files to: {output_excel}")
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:

            # 0. Metadata
            meta_dict = self._parse_metadata_from_filename(json_path)
            df_meta = pd.DataFrame(list(meta_dict.items()), columns=['Key', 'Value'])
            df_meta.to_excel(writer, sheet_name='Metadata', index=False, header=False)

            # 1. Basic input (Mandatory)
            df_basic = pd.DataFrame(basic_rows)
            df_basic.to_excel(writer, sheet_name='Basic input', index=False)

            # 2. Diet composition (Mandatory)
            df_diet = diet_matrix.copy()
            # Add Prey Names as the first column to match EwE format
            df_diet.insert(0, 'Prey \\ Predator', [group_names.get(str(idx), idx) for idx in df_diet.index])

            # Add a Sum row at the bottom
            df_diet.loc['Sum'] = df_diet.sum(numeric_only=True)
            df_diet.at['Sum', 'Prey \\ Predator'] = 'Sum'

            # Convert index back to column for output
            df_diet.reset_index(inplace=True)
            df_diet.rename(columns={'index': 'Prey ID'}, inplace=True)
            df_diet.to_excel(writer, sheet_name='Diet composition', index=False)

            # 3. Biomass accumulation
            if has_ba:
                pd.DataFrame(ba_rows).to_excel(
                    writer, sheet_name='Biomass accumulation', index=False)
                self.logger.info("  -> Included 'Biomass accumulation' sheet")

            # 4. Landings (Using the consolidated Export value)
            if has_export:
                df_landings = pd.DataFrame(landings_rows)
                # Filter out rows that are entirely 0 or empty to keep it clean
                df_landings = df_landings[df_landings['Total'] != ""]
                df_landings = df_landings[df_landings['Total'].astype(float) > 0.0]
                df_landings.to_excel(writer, sheet_name='Landings', index=False)
                self.logger.info("  -> Included 'Landings' sheet (calculated from 'export' param)")

            # 5. Taxonomy
            if has_tax:
                df_tax = pd.DataFrame(tax_rows)
                df_tax.to_excel(writer, sheet_name='Taxonomy', index=False)
                self.logger.info("  -> Included 'Taxonomy' sheet")

            # 6. TL
            if has_tl:
                df_tl = pd.DataFrame(tl_rows)
                df_tl.to_excel(writer, sheet_name='TL', index=False)
                self.logger.info("  -> Included 'TL' sheet")

            # 7. Detritus Fate
            if detritus_pools:
                det_cols = list(detritus_pools)
                df_det = det_fate_matrix[det_cols].copy()

                # Map column IDs back to names for readability
                df_det.columns = [group_names.get(str(c), c) for c in df_det.columns]

                # Insert Source Info
                df_det.insert(0, 'Source Name', [group_names.get(str(idx), idx) for idx in df_det.index])
                df_det.insert(0, 'Source ID', df_det.index)

                # Remove rows where a source routes 0.0 to all detritus pools (Living groups with no routing)
                # Actually, standard EwE format keeps all groups in the rows, so we'll leave them in for structural consistency
                df_det.to_excel(writer, sheet_name='Detritus fate', index=False)
                self.logger.info(f"  -> Included 'Detritus fate' sheet (Pools identified: {len(detritus_pools)})")

        self.logger.info("\nSuccess! Validation file generated.")
        return output_excel


def main():
    parser = argparse.ArgumentParser(
        description="EwE model directory -> database JSON, with a mass balance check",
        epilog="""
Usage Examples:
  Option 1: Convert a model directory to the database JSON, then rebuild the
            round-trip workbook from it:
      python database_json.py -d ./680_North_Sea_1981

  Option 2: Rebuild the workbook from a database JSON that already exists:
      python database_json.py -j ./680_North_Sea_1981/22_680_North_Sea_(1981).json
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--dir', type=str, help='Path to directory containing CSV/Excel EwE inputs.')
    group.add_argument('-j', '--json', type=str, help='Path to an existing JSON model file.')
    parser.add_argument('--ee-tol', type=float, default=0.05,
                        help='Allowed absolute difference between the printed EE and '
                             'the one recomputed from the diet matrix (default 0.05).')
    parser.add_argument('--update-report', action='store_true',
                        help="Replace the '## Mass balance' section of REPORT.md in "
                             "the input directory with the check's findings.")

    args = parser.parse_args()

    converter = EwEConverter()

    if args.dir:
        input_directory = os.path.abspath(args.dir)
        if not os.path.exists(input_directory) or not os.path.isdir(input_directory):
            print(f"Error: Directory '{input_directory}' does not exist.")
            return

        print(f"\n--- Running Pipeline Option 1 (Dir -> JSON -> Excel) ---")
        json_file = converter.csv_to_json(input_directory, ee_tol=args.ee_tol,
                                          update_report=args.update_report)
        if json_file:
            converter.json_to_excel(json_file)

    elif args.json:
        json_path = os.path.abspath(args.json)
        if not os.path.exists(json_path) or not os.path.isfile(json_path):
            print(f"Error: JSON file '{json_path}' does not exist.")
            return

        print(f"\n--- Running Pipeline Option 2 (JSON -> Excel) ---")
        converter.json_to_excel(json_path)


if __name__ == "__main__":
    main()
