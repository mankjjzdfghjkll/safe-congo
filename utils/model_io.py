"""Utilities for loading saved ML artifacts across NumPy versions."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

import joblib


def _install_numpy_core_aliases() -> None:
    """Allow pickles created with NumPy 2.x to load under NumPy 1.x."""
    module_aliases = {
        "numpy._core": "numpy.core",
        "numpy._core.multiarray": "numpy.core.multiarray",
        "numpy._core.numeric": "numpy.core.numeric",
        "numpy._core.umath": "numpy.core.umath",
        "numpy._core._multiarray_umath": "numpy.core._multiarray_umath",
    }

    for alias, target in module_aliases.items():
        if alias in sys.modules:
            continue
        try:
            sys.modules[alias] = importlib.import_module(target)
        except Exception:
            continue

    try:
        random_pickle = importlib.import_module("numpy.random._pickle")
        original_ctor = random_pickle.__bit_generator_ctor

        if not getattr(original_ctor, "_safe_congo_patched", False):
            def _compatible_bit_generator_ctor(bit_generator_name="MT19937"):
                if isinstance(bit_generator_name, type):
                    return bit_generator_name()
                return original_ctor(bit_generator_name)

            _compatible_bit_generator_ctor._safe_congo_patched = True
            random_pickle.__bit_generator_ctor = _compatible_bit_generator_ctor
    except Exception:
        pass


def _install_sklearn_aliases() -> None:
    """Allow pickles created by newer scikit-learn releases to resolve aliases."""
    module_aliases = {
        "_loss": "sklearn._loss",
        "_loss.loss": "sklearn._loss.loss",
        "_loss.link": "sklearn._loss.link",
    }

    for alias, target in module_aliases.items():
        if alias in sys.modules:
            continue
        try:
            sys.modules[alias] = importlib.import_module(target)
        except Exception:
            continue

    try:
        sklearn_loss = importlib.import_module("sklearn._loss")
        loss_module = importlib.import_module("sklearn._loss.loss")
        link_module = importlib.import_module("sklearn._loss.link")
        for module in (loss_module, link_module):
            for name in dir(module):
                if name.startswith(("Cy", "Half", "Interval", "Identity")) and not hasattr(sklearn_loss, name):
                    setattr(sklearn_loss, name, getattr(module, name))
    except Exception:
        pass


def load_joblib_compatible(path: str | Path) -> Any:
    """Load a joblib artifact with a small NumPy compatibility shim."""
    _install_numpy_core_aliases()
    _install_sklearn_aliases()
    return joblib.load(path)
