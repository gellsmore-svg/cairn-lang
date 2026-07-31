"""Compatibility shim: `cairn` was split into `deborah` + `huldah`.

Importing this package still works and re-exports every name the pre-split
`cairn` package exposed, but emits a :class:`DeprecationWarning` pointing at the
new home. It exists so family consumers migrate over one or two normal release
cycles instead of all at once; it is scheduled for removal one minor after the
last consumer moves.

    cairn.validate_plan       -> deborah.validate_plan      (the language)
    cairn.analyze_human_factors -> huldah.analyze_human_factors (the analysis)

The *language* was not renamed: `.cairn.md` documents and ```cairn fences are
unchanged. Only the Python distributions were.

`huldah` is optional here. If only `deborah` is installed, the language names
resolve and the analysis names raise a clear ImportError explaining which
package to install, rather than failing with a bare AttributeError.
"""

from __future__ import annotations

import importlib
import sys
import warnings
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any

# Submodule -> new home. `import cairn.grammar` and `from cairn.human_factors
# import ...` keep working, resolved through the finder installed below.
_SUBMODULES = {
    # the language
    "conformance": "deborah.conformance",
    "grammar": "deborah.grammar",
    "render": "deborah.render",
    "manifest": "deborah.manifest",
    "web": "deborah.web",
    "cli": "deborah.cli",
    "validate_cli": "deborah.validate_cli",
    # the analysis
    **{
        name: f"huldah.{name}"
        for name in (
            "agent_harness", "agent_harness_cli", "galeed_adapter", "galeed_observe_cli",
            "human_factors", "human_factors_cli", "interface_recommendations",
            "interface_recommendations_cli", "layout_load", "layout_load_cli",
            "live_observer", "live_observer_cli", "llm_adapters", "llm_wrappers",
            "observation_contract", "reporting", "reporting_cli", "system_discovery",
            "system_discovery_cli", "ui_annotations_cli", "ui_evidence", "ui_evidence_cli",
            "ui_pipeline_cli", "ui_roleplay_cli", "ui_scenario_validate_cli",
            "ui_scenarios", "ui_sim_cli",
        )
    },
}


class _AliasLoader(Loader):
    """Load `cairn.X` by importing its replacement and aliasing the module."""

    def __init__(self, target: str) -> None:
        self._target = target

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        package = self._target.split(".", 1)[0]
        try:
            module = importlib.import_module(self._target)
        except ImportError as exc:
            raise ImportError(
                f"{spec.name} moved to {self._target}, but `{package}` is not "
                f"installed. Install it with `pip install {package}`."
            ) from exc
        _warn(spec.name.split(".", 1)[1], package)
        return module

    def exec_module(self, module: ModuleType) -> None:
        """No-op: create_module returned an already-executed module."""


class _CairnCompatFinder(MetaPathFinder):
    def find_spec(self, fullname: str, path: Any = None, target: Any = None) -> ModuleSpec | None:
        if not fullname.startswith("cairn."):
            return None
        head = fullname.split(".", 2)[1]
        moved = _SUBMODULES.get(head)
        if moved is None:
            return None
        # Preserve any deeper path: cairn.grammar.parser -> deborah.grammar.parser
        rest = fullname.split(".", 2)[2:]
        full_target = ".".join([moved, *rest])
        return ModuleSpec(fullname, _AliasLoader(full_target))


if not any(isinstance(f, _CairnCompatFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _CairnCompatFinder())

_MOVED_TO_DEBORAH = {
    "CANONICAL_PLAN", "CONFORMANCE_VERSION", "CairnDocument", "PLAN_CONSTRUCTS",
    "PLAN_STATUSES", "REQUIRED_PLAN_FIELDS", "REQUIRED_STEP_FIELDS",
    "REVISION_DECISIONS", "STEP_STATUSES", "document_to_dict", "document_to_plan",
    "export_view", "extract_cairn_source", "is_conformant", "parse_document",
    "register_exporter", "registered_exporters", "registered_profiles",
    "render_plan", "validate_document", "validate_plan",
}

_MOVED_TO_HULDAH = {
    "AgentHarnessPlan", "AgentHarnessStep", "CommandLLMProvider", "HoglahLLMProvider",
    "HostedLLMConfig", "HostedLLMProvider", "LLMRequest", "LLMResponse",
    "analyze_functional_layout", "analyze_human_factors", "analyze_live_observations",
    "analyze_ui_simulation_report", "build_agent_harness_plan", "build_analysis_report",
    "build_human_factors_prompt", "build_ui_roleplay_prompt", "claude_provider",
    "discover_system", "format_agent_harness_plan", "format_analysis_report",
    "format_cairn_annotation_snippet", "format_functional_layout_report",
    "format_human_factors_report", "format_interface_recommendations",
    "format_live_observation_report", "format_scenario_validation_report",
    "format_system_discovery_report", "format_ui_human_load_report",
    "format_ui_layout_overlay_index", "format_ui_layout_overlay_manifest",
    "future_state_svg", "galeed_event_to_observation", "galeed_llm_call_to_observation",
    "gemini_provider", "grok_provider", "interpret_human_factors",
    "interpret_ui_experience", "observation_event", "observation_to_galeed_trace_event",
    "openai_provider", "recommend_interface_changes", "render_layout_svg",
    "render_ui_layout_overlay", "render_ui_layout_overlays", "validate_ui_scenario",
}

__all__ = sorted(_MOVED_TO_DEBORAH | _MOVED_TO_HULDAH)

_WARNED: set[str] = set()


def _warn(name: str, package: str) -> None:
    # One warning per name: a loop over cairn.validate_plan should not emit
    # thousands of identical warnings.
    if name in _WARNED:
        return
    _WARNED.add(name)
    warnings.warn(
        f"cairn.{name} has moved to {package}.{name}. The `cairn` package is a "
        f"compatibility shim and will be removed a minor release after the last "
        f"consumer migrates; import from `{package}` instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def __getattr__(name: str) -> Any:
    """Resolve a pre-split `cairn` name from its new package, lazily.

    Lazy on purpose: importing `cairn` must not drag in `huldah` (and its
    heavier optional surface) for a consumer that only wants the language.
    """
    if name in _MOVED_TO_DEBORAH:
        import deborah

        _warn(name, "deborah")
        return getattr(deborah, name)

    if name in _MOVED_TO_HULDAH:
        try:
            import huldah
        except ImportError as exc:  # pragma: no cover - depends on install set
            raise ImportError(
                f"cairn.{name} moved to huldah.{name}, which is not installed. "
                f"Install it with `pip install huldah` (the human-systems analysis "
                f"half of the old cairn package)."
            ) from exc

        _warn(name, "huldah")
        return getattr(huldah, name)

    raise AttributeError(f"module 'cairn' has no attribute {name!r}")


def __dir__() -> list[str]:
    return __all__
