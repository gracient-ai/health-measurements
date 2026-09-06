"""What must hold before a measurements file can merge.

Run by `.github/workflows/checks.yml` as a required status check. Every failure names the
band it is about, because a check that says "invalid" makes somebody read the whole file.
"""
from __future__ import annotations

import sys

import yaml


def problems(loaded) -> list[str]:
    bad: list[str] = []
    if not isinstance(loaded, dict) or not isinstance(loaded.get("measurements"), list):
        return ["this file has no `measurements:` list at the top"]

    for m in loaded["measurements"]:
        name = m.get("measurement", "?")
        for field in ("measurement", "code", "unit", "applies_to"):
            if not m.get(field):
                bad.append(f"{name}: no {field}")
        bands = m.get("bands") or []
        if not bands:
            bad.append(f"{name}: no bands, so nothing can be answered about it")
            continue

        for b in bands:
            at = f"{name} · {b.get('band', '?')}"
            if not b.get("band"):
                bad.append(f"{name}: a band with no name")
            if not b.get("severity"):
                bad.append(f"{at}: no severity")
            if "upto" not in b:
                bad.append(f"{at}: no ceiling. Write `upto: null` for the open one")
            # A band with nothing behind it cannot be checked by whoever approves it.
            if not b.get("quote"):
                bad.append(f"{at}: no sentence from the document behind it")
            if not b.get("locator"):
                bad.append(f"{at}: no locator, so nobody can find that sentence")
            if not b.get("from"):
                bad.append(f"{at}: does not say which document")

        ceilings = [b.get("upto") for b in bands]
        if ceilings and ceilings[-1] is not None:
            bad.append(f"{name}: the last band has a ceiling, so a reading above it "
                       f"falls through and is answered by nothing")
        closed = [c for c in ceilings[:-1] if c is not None]
        if closed != sorted(closed):
            bad.append(f"{name}: the bands do not run upwards")
        if len(set(closed)) != len(closed):
            bad.append(f"{name}: two bands share a ceiling")
        if any(c is None for c in ceilings[:-1]):
            bad.append(f"{name}: a band with no ceiling before the last one")
    return bad


def main(path: str) -> int:
    bad = problems(yaml.safe_load(open(path, "rb")))
    for line in bad:
        print(f"  {line}")
    print(f"  {len(bad)} problem{'' if len(bad) == 1 else 's'} in {path}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "measurements.yaml"))
