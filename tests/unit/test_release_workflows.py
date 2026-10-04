from pathlib import Path

import pytest


@pytest.mark.parametrize("name", ["release.yml", "unsigned-preview-release.yml"])
def test_release_inputs_are_data_and_releases_target_checkout(name):
    workflow = (Path(__file__).resolve().parents[2] / ".github/workflows" / name).read_text()
    assert "RELEASE_TAG: ${{ inputs.tag }}" in workflow
    assert "RELEASE_SHA: ${{ github.sha }}" in workflow
    assert 'gh release create "$env:RELEASE_TAG"' in workflow
    assert '--target "$env:RELEASE_SHA"' in workflow
    for line in workflow.splitlines():
        if "${{ inputs.tag }}" in line:
            assert line.strip().startswith("RELEASE_TAG:")
