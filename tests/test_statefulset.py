"""
Lightweight unit tests for the StatefulSet manifest.

These run in the GitHub Actions `test` job BEFORE any cluster login/apply.
If any assertion fails, the build goes red and the deploy stage is skipped -
so a malformed manifest can never reach the cluster.

Add your own domain-specific checks here (image registry allow-lists,
required labels, replica bounds, etc.).
"""
import os
import pathlib

import pytest
import yaml

MANIFEST = pathlib.Path(__file__).resolve().parents[1] / "manifests" / "statefulset.yaml"


@pytest.fixture(scope="module")
def manifest():
    assert MANIFEST.exists(), f"Manifest not found at {MANIFEST}"
    with open(MANIFEST) as fh:
        docs = [d for d in yaml.safe_load_all(fh) if d]
    assert docs, "Manifest is empty"
    return docs[0]


def test_is_valid_yaml(manifest):
    assert isinstance(manifest, dict)


def test_kind_is_statefulset(manifest):
    assert manifest.get("kind") == "StatefulSet", "Manifest must be a StatefulSet"


def test_api_version(manifest):
    assert manifest.get("apiVersion") == "apps/v1"


def test_has_name(manifest):
    name = manifest.get("metadata", {}).get("name")
    assert name, "StatefulSet must have metadata.name"


def test_has_service_name(manifest):
    # A StatefulSet requires a governing headless Service via spec.serviceName
    assert manifest["spec"].get("serviceName"), "spec.serviceName is required for a StatefulSet"


def test_replicas_positive(manifest):
    replicas = manifest["spec"].get("replicas", 1)
    assert isinstance(replicas, int) and replicas >= 1, "replicas must be a positive integer"


def test_selector_matches_template_labels(manifest):
    sel = manifest["spec"]["selector"]["matchLabels"]
    tmpl = manifest["spec"]["template"]["metadata"]["labels"]
    for k, v in sel.items():
        assert tmpl.get(k) == v, f"selector label {k}={v} must match pod template labels"


def test_containers_have_image(manifest):
    containers = manifest["spec"]["template"]["spec"]["containers"]
    assert containers, "At least one container is required"
    for c in containers:
        assert c.get("image"), f"container {c.get('name')} must specify an image"
        assert c.get("name"), "every container must have a name"
