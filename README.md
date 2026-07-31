# cairn-lang (compatibility shim)

`cairn` was split into two packages in v0.9:

- **[deborah](https://github.com/gellsmore-svg/Deborah)** — the process language
  (spec, grammar, conformance, render).
- **[huldah](https://github.com/gellsmore-svg/Huldah)** — human-systems analysis
  (human factors, UI evidence, layout load, live observation, agent harness).

This package keeps `import cairn` working, re-exporting every pre-split name
from its new home with a `DeprecationWarning`. Submodules resolve too, including
deep paths (`cairn.grammar.parser`).

It depends only on `deborah`. If you used the analysis half, install
`huldah` as well (or `pip install 'cairn-lang[analysis]'`) — otherwise those
names raise an `ImportError` naming the package to install.

**The document format is unchanged**: `.cairn.md` files and ```cairn fences
still work exactly as before. Only the Python distributions were renamed.

Scheduled for removal one minor release after the last consumer migrates.
See [MIGRATING.md](https://github.com/gellsmore-svg/Deborah/blob/main/MIGRATING.md).
