"""Team Orchestrator - Agent lifecycle manager (Issue #10)"""


class TeamOrchestrator:
    """Manages lifecycle of PM/Engineer/Strategist agents.

    Responsibilities:
    - Start/stop agent heartbeats
    - Handle exceptions and recovery
    - Coordinate team initialization
    """

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.agents = {}
