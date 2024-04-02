from enum import Enum


class VertexLabel(str, Enum):
    User = "User"
    Team = "Team"
    Project = "Project"
    ProjectRun = "ProjectRun"
    Model = "Model"
    ModelRun = "ModelRun"
    Dataset = "Dataset"
    Task = "Task"


class EdgeLabel(str, Enum):
    owns = "owns"  # User owns project
    member = "member"  # User is member of team
    runs = "runs"  # Project runs projectrun
    requires = "requires"  # Project run requires model
    affiliated = "affiliated"  # Model is affiliated to team
    performs = "performs"  # Model performs model run
    attributed = "attributed"  # User is attributed to Dataset
    produced = "produced"  # Model run produces dataset
