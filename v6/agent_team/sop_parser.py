"""SOPParser - Markdown SOP document parser (Issue #5)

Reads Markdown-formatted SOP (Standard Operating Procedure) documents,
extracts structured steps, and converts them into executable instruction
sequences that agents can follow.

Expected SOP format:
    # SOP: {title}
    {description}

    ## Prerequisites
    - {prerequisite items}

    ## Steps
    1. {step description}
       - Action: {action to execute}
       - Tool: {tool_name}
       - Check: {verification condition}

    2. {step description}
       ...
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SOPStep:
    """A single step in an SOP."""
    number: int
    title: str
    description: str = ""
    action: Optional[str] = None
    tool: Optional[str] = None
    check: Optional[str] = None
    substeps: list[str] = field(default_factory=list)

    @property
    def is_actionable(self) -> bool:
        """Whether this step has a concrete action to execute."""
        return self.action is not None or self.tool is not None


@dataclass
class SOP:
    """A parsed Standard Operating Procedure document."""
    title: str
    description: str = ""
    prerequisites: list[str] = field(default_factory=list)
    steps: list[SOPStep] = field(default_factory=list)
    source_file: Optional[str] = None

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def actionable_steps(self) -> list[SOPStep]:
        return [s for s in self.steps if s.is_actionable]

    def get_step(self, number: int) -> Optional[SOPStep]:
        """Get a step by its number (1-indexed)."""
        for step in self.steps:
            if step.number == number:
                return step
        return None

    def to_instruction_text(self) -> str:
        """Convert SOP to a plain text instruction sequence for an agent."""
        lines = [f"SOP: {self.title}"]
        if self.description:
            lines.append(self.description)
        lines.append("")

        if self.prerequisites:
            lines.append("Prerequisites:")
            for p in self.prerequisites:
                lines.append(f"  - {p}")
            lines.append("")

        lines.append("Steps:")
        for step in self.steps:
            lines.append(f"  {step.number}. {step.title}")
            if step.action:
                lines.append(f"     Action: {step.action}")
            if step.tool:
                lines.append(f"     Tool: {step.tool}")
            if step.check:
                lines.append(f"     Check: {step.check}")
            for sub in step.substeps:
                lines.append(f"     - {sub}")

        return "\n".join(lines)


class SOPParser:
    """Reads Markdown SOP docs, extracts steps, converts to executable instructions."""

    def parse_file(self, filepath: str) -> SOP:
        """Parse a Markdown SOP file.

        Args:
            filepath: Path to the .md file

        Returns:
            Parsed SOP object
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"SOP file not found: {filepath}")

        text = path.read_text(encoding="utf-8")
        sop = self.parse_text(text)
        sop.source_file = str(path)
        return sop

    def parse_text(self, text: str) -> SOP:
        """Parse SOP from raw Markdown text.

        Args:
            text: Markdown content

        Returns:
            Parsed SOP object
        """
        lines = text.strip().split("\n")
        sop = SOP(title="")

        # Parse title from first H1
        section = None
        current_step = None
        step_number = 0
        description_lines = []

        for line in lines:
            stripped = line.strip()

            # H1: SOP title
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                # Remove "SOP:" prefix if present
                if title.lower().startswith("sop:"):
                    title = title[4:].strip()
                sop.title = title
                section = "header"
                continue

            # H2: Section headers
            if stripped.startswith("## "):
                section_name = stripped[3:].strip().lower()
                if "prerequisite" in section_name:
                    section = "prerequisites"
                elif "step" in section_name:
                    section = "steps"
                else:
                    section = section_name
                continue

            # Empty lines
            if not stripped:
                if section == "header" and description_lines:
                    sop.description = " ".join(description_lines)
                    description_lines = []
                continue

            # Header description
            if section == "header" and not stripped.startswith("#"):
                description_lines.append(stripped)
                continue

            # Prerequisites
            if section == "prerequisites":
                if stripped.startswith("- ") or stripped.startswith("* "):
                    sop.prerequisites.append(stripped[2:].strip())
                continue

            # Steps
            if section == "steps":
                # Numbered step (e.g., "1. Step title")
                num_match = re.match(r"^(\d+)\.\s+(.+)$", stripped)
                if num_match:
                    step_number = int(num_match.group(1))
                    step_title = num_match.group(2)
                    current_step = SOPStep(number=step_number, title=step_title)
                    sop.steps.append(current_step)
                    continue

                # Step metadata (indented - Action/Tool/Check)
                if current_step and stripped.startswith("- "):
                    item = stripped[2:].strip()
                    kv_match = re.match(r"^(Action|Tool|Check)\s*:\s*(.+)$", item, re.IGNORECASE)
                    if kv_match:
                        key = kv_match.group(1).lower()
                        value = kv_match.group(2).strip()
                        if key == "action":
                            current_step.action = value
                        elif key == "tool":
                            current_step.tool = value
                        elif key == "check":
                            current_step.check = value
                    else:
                        current_step.substeps.append(item)
                    continue

                # Description text under a step
                if current_step and stripped:
                    if current_step.description:
                        current_step.description += " " + stripped
                    else:
                        current_step.description = stripped

        # Handle remaining description
        if description_lines:
            sop.description = " ".join(description_lines)

        return sop

    def list_sops(self, sops_dir: str) -> list[str]:
        """List all SOP files in a directory.

        Args:
            sops_dir: Directory containing .md SOP files

        Returns:
            List of file paths
        """
        path = Path(sops_dir)
        if not path.exists():
            return []
        return sorted(str(f) for f in path.glob("*.md"))
