"""Tests for the SOP parser (Issue #5)"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_team.sop_parser import SOPParser, SOP, SOPStep


SAMPLE_SOP = """# SOP: Deploy New Service

Follow these steps to deploy a new microservice.

## Prerequisites

- Docker installed
- kubectl configured

## Steps

1. Build Docker image
   - Action: Run docker build with the project Dockerfile
   - Tool: run_bash
   - Check: Image builds without errors

2. Push to registry
   - Action: Tag and push the image to container registry
   - Tool: run_bash
   - Check: Image is available in the registry

3. Update Kubernetes manifest
   - Action: Update the deployment YAML with new image tag
   - Tool: edit_file
   - Check: YAML is valid and references correct image

4. Apply deployment
   - Action: Run kubectl apply to deploy the new version
   - Tool: run_bash
   - Check: Pods are running and healthy
"""


class TestSOPStep:
    def test_actionable(self):
        step = SOPStep(number=1, title="Test", action="do something")
        assert step.is_actionable is True

    def test_not_actionable(self):
        step = SOPStep(number=1, title="Note")
        assert step.is_actionable is False

    def test_tool_makes_actionable(self):
        step = SOPStep(number=1, title="Test", tool="run_bash")
        assert step.is_actionable is True


class TestSOPParser:
    def test_parse_text(self):
        parser = SOPParser()
        sop = parser.parse_text(SAMPLE_SOP)

        assert sop.title == "Deploy New Service"
        assert "microservice" in sop.description
        assert len(sop.prerequisites) == 2
        assert "Docker installed" in sop.prerequisites

    def test_steps_parsed(self):
        parser = SOPParser()
        sop = parser.parse_text(SAMPLE_SOP)

        assert sop.step_count == 4
        assert sop.steps[0].title == "Build Docker image"
        assert sop.steps[0].action == "Run docker build with the project Dockerfile"
        assert sop.steps[0].tool == "run_bash"
        assert sop.steps[0].check == "Image builds without errors"

    def test_get_step(self):
        parser = SOPParser()
        sop = parser.parse_text(SAMPLE_SOP)

        step = sop.get_step(3)
        assert step is not None
        assert step.title == "Update Kubernetes manifest"
        assert step.tool == "edit_file"

        assert sop.get_step(99) is None

    def test_actionable_steps(self):
        parser = SOPParser()
        sop = parser.parse_text(SAMPLE_SOP)
        assert len(sop.actionable_steps) == 4

    def test_to_instruction_text(self):
        parser = SOPParser()
        sop = parser.parse_text(SAMPLE_SOP)
        text = sop.to_instruction_text()

        assert "SOP: Deploy New Service" in text
        assert "Action:" in text
        assert "Tool: run_bash" in text

    def test_parse_file(self, tmp_path):
        sop_file = tmp_path / "test.md"
        sop_file.write_text(SAMPLE_SOP, encoding="utf-8")

        parser = SOPParser()
        sop = parser.parse_file(str(sop_file))
        assert sop.title == "Deploy New Service"
        assert sop.source_file == str(sop_file)

    def test_parse_file_not_found(self):
        parser = SOPParser()
        try:
            parser.parse_file("/nonexistent/path.md")
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_list_sops(self, tmp_path):
        (tmp_path / "sop1.md").write_text("# SOP: One\n## Steps\n1. Do thing")
        (tmp_path / "sop2.md").write_text("# SOP: Two\n## Steps\n1. Do other")
        (tmp_path / "notes.txt").write_text("not an sop")

        parser = SOPParser()
        sops = parser.list_sops(str(tmp_path))
        assert len(sops) == 2

    def test_list_sops_empty_dir(self, tmp_path):
        parser = SOPParser()
        assert parser.list_sops(str(tmp_path / "nonexistent")) == []

    def test_minimal_sop(self):
        parser = SOPParser()
        sop = parser.parse_text("# SOP: Minimal\n\n## Steps\n\n1. Do the thing")
        assert sop.title == "Minimal"
        assert sop.step_count == 1
