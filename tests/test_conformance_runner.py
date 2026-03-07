"""Unit tests for reference.python.conformance_runner module."""

from __future__ import annotations

from reference.python.conformance_runner import (
    LEVEL_DIRS,
    build_pytest_args,
)


class TestBuildPytestArgs:
    def test_all_levels_includes_conformance_dir(self):
        args = build_pytest_args(level=None)
        assert any("conformance" in a for a in args)

    def test_level_1_includes_core(self):
        args = build_pytest_args(level=1)
        assert any("test_core_conformance" in a for a in args)

    def test_security_only(self):
        args = build_pytest_args(security_only=True)
        assert any("security" in a for a in args)

    def test_no_verbose(self):
        args = build_pytest_args(verbose=False)
        assert "-v" not in args

    def test_verbose_default(self):
        args = build_pytest_args()
        assert "-v" in args

    def test_level_dirs_has_five_levels(self):
        assert len(LEVEL_DIRS) == 5
