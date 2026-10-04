from pathlib import Path
h=Path(__file__).resolve().parent;p=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts/database_json.py');s=p.read_text(encoding='utf-8')
guard='''        # Source completeness is distinct from an equation check on known cells.
        for source_group in groups_json:
            seq = source_group["group_seq"]
            source_diet = (source_group.get("diet_descr") or {}).get("diet") or []
            if isinstance(source_diet, dict): source_diet = [source_diet]
            if source_diet:
                missing_cells = [x.get("prey_seq") for x in source_diet if self._num(x.get("proportion")) is None]
                known_total = sum(self._num(x.get("proportion")) or 0.0 for x in source_diet)
                imported = self._num(source_group.get("diet_imp"))
                known_total += imported or 0.0
                if known_total > 1.01:
                    errors.append(f"group {seq}: known source diet plus import subtotal {known_total:.8g} exceeds one; no normalization applied")
                if missing_cells or imported is None:
                    indeterminate.append(f"group {seq}: diet/import has unknown cells; known subtotal {known_total:.8g} is not a complete composition")
                elif known_total < 0.99:
                    errors.append(f"group {seq}: complete source diet plus import sum {known_total:.8g} is below one")
            if source_group.get("pp") == "0" and (self._num(source_group.get("pb")) or 0.0) <= 0:
                indeterminate.append(f"group {seq}: source P/B is missing or nonpositive; native/stanza production cannot be verified")
            if source_group.get("pp") == "0" and self._num(source_group.get("gs")) is None:
                indeterminate.append(f"group {seq}: unassimilated fraction unknown; indicative checks use a software assumption")
            if source_group.get("discards_total") == self.NO_DATA:
                indeterminate.append(f"group {seq}: discard removals unknown; reported catch does not establish complete removals")
        n_unknown = sum(1 for r in rows if not r["BA_known"])
'''
needle='        n_unknown = sum(1 for r in rows if not r["BA_known"])\n'
assert needle in s and 'Source completeness is distinct' not in s
s=s.replace(needle,guard);p.write_text(s,encoding='utf-8');(h/'skill_update/scripts/database_json.py').write_bytes(p.read_bytes());print('Source completeness guard installed')
