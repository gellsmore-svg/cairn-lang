"""The `cairn` compatibility shim must keep pre-split code working."""

from __future__ import annotations

import builtins
import warnings

import pytest


def test_language_names_resolve_to_deborah():
    import cairn
    import deborah

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert cairn.validate_plan is deborah.validate_plan

    assert any("moved to deborah.validate_plan" in str(w.message) for w in caught)


def test_analysis_names_resolve_to_huldah():
    import cairn
    import huldah

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert cairn.analyze_human_factors is huldah.analyze_human_factors

    assert any("moved to huldah.analyze_human_factors" in str(w.message) for w in caught)


def test_submodules_resolve_including_deep_paths():
    from cairn.grammar import parse_document
    from cairn.human_factors import analyze_human_factors
    import cairn.grammar.parser

    assert parse_document.__module__.startswith("deborah.")
    assert analyze_human_factors.__module__.startswith("huldah.")
    assert cairn.grammar.parser.__name__ == "deborah.grammar.parser"


def test_unknown_attribute_still_raises_attribute_error():
    import cairn

    with pytest.raises(AttributeError):
        cairn.no_such_name


def test_missing_huldah_gives_an_actionable_import_error(monkeypatch):
    """A consumer that only installed the language gets told which package to add."""
    import cairn

    real_import = builtins.__import__

    def guard(name, *args, **kwargs):
        if name.split(".")[0] == "huldah":
            raise ImportError("simulated: huldah not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guard)
    # Bypass the one-warning-per-name cache so the lookup really re-runs.
    cairn._WARNED.discard("build_analysis_report")

    with pytest.raises(ImportError, match="pip install huldah"):
        cairn.build_analysis_report

    # the language half is unaffected
    assert cairn.validate_plan({}) is not None


def test_each_name_warns_only_once():
    import cairn

    cairn._WARNED.discard("render_plan")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        cairn.render_plan
        cairn.render_plan
        cairn.render_plan

    deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert len(deprecations) == 1


def test_dir_lists_every_pre_split_name():
    import cairn

    names = dir(cairn)
    assert "validate_plan" in names        # language
    assert "analyze_human_factors" in names  # analysis
    assert len(names) == 66
