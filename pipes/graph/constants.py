from enum import Enum


class VertexLabel(str, Enum):
    User = "User"
    Team = "Team"
    Project = "Project"
    ProjectRun = "ProjectRun"
    Model = "Model"
    ModelRun = "ModelRun"
    Task = "Task"


class EdgeLabel(str, Enum):
    owns = "owns"  # User owns project
    member = "member"  # User is member of team
    runs = "runs"  # Project runs projectrun
    requires = "requires"  # Project run requires model
    performs = "performs"  # Model performs model run
