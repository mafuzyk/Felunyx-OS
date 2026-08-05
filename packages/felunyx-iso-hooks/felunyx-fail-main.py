#!/usr/bin/env python3
"""Deterministic failure used only by the Phase 2 installer harness."""


def pretty_name():
    return "Felunyx Phase 2 failure injection"


def run():
    return (
        "FelunyxInjectedFailure",
        "Intentional Phase 2 installer failure injection",
    )
