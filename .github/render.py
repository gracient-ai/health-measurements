"""Turn the measurements file into the Markdown a doctor reads in a diff.

Writes to standard output. The workflow compares what this produces with what is committed,
so a rendered file that has drifted fails rather than a doctor approving a diff of something
that is not what the product will run.
"""
from __future__ import annotations

import sys

import yaml

HEAD = ("| Band | Up to | What the patient is told | The document's own sentence | Where |\n"
        "|---|---|---|---|---|")


def cell(value) -> str:
    """One table cell. A newline or a pipe inside one breaks the row it is in."""
    return " ".join(str(value or "").split()).replace("|", "\\|")


# Emitted by the renderer rather than typed into the file, so that what the workflow
# compares is the whole file rather than the whole file minus a header nobody regenerates.
HEADER = """<!-- Generated from measurements.yaml by .github/render.py. Do not edit by hand.

     It exists so that the diff a doctor reads in a pull request is clinical language
     rather than YAML. The checks refuse a pull request where the two have drifted. -->
"""


def render(loaded) -> str:
    out: list[str] = [HEADER]
    for m in loaded.get("measurements", []):
        out.append(f"\n## {m.get('measurement')}\n")
        out.append(f"`{m.get('code')}` · {m.get('unit')} · {m.get('applies_to')}\n")
        out.append(HEAD)
        for b in m.get("bands") or []:
            top = "no top" if b.get("upto") is None else f"{b['upto']} {m.get('unit')}"
            says = cell(b.get("means"))
            if b.get("action"):
                says += f" **{cell(b['action'])}**"
            out.append(f"| {cell(b.get('band'))} ({cell(b.get('severity'))}) | {cell(top)} "
                       f"| {says} | {cell(b.get('quote'))} "
                       f"| {cell(b.get('locator'))}, {cell(b.get('from'))} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "measurements.yaml"
    print(render(yaml.safe_load(open(path, "rb"))), end="")
