# cairn-lang (compatibility shim)

**If `import cairn` now warns you, switch to the new packages:**

```bash
pip install deborah            # the process language: spec, grammar, conformance, render
pip install huldah             # only if you used the analysis half
```

Then replace `cairn` imports with `deborah` (language) or `huldah` (human
factors, UI evidence, layout load, live observation, agent harness). The full
name mapping is in [MIGRATING.md](https://github.com/gellsmore-svg/Deborah/blob/main/MIGRATING.md).

**Your documents need no changes.** `.cairn.md` files and ```cairn fences keep
the Cairn name and work exactly as before. Only the Python distributions were
renamed.

## What this package does meanwhile

Nothing breaks on day one. `cairn` was split into
[deborah](https://github.com/gellsmore-svg/Deborah) and
[huldah](https://github.com/gellsmore-svg/Huldah) in v0.9, and this shim keeps
`import cairn` working. It re-exports every pre-split name from its new home
with a `DeprecationWarning`, including deep submodule paths
(`cairn.grammar.parser`).

It depends only on `deborah`. Analysis names raise an `ImportError` naming the
package to install unless you also install `huldah` (or
`pip install 'cairn-lang[analysis]'`).

The shim will be removed one minor release after the last consumer migrates.

Apache 2.0, see [LICENSE](LICENSE).
