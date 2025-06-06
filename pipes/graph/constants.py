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
    feeds = "feeds"  # Model A feeds model B
    informs = "informs"  # Model B informs model A
    associated = "associated"  # Task is associated with user
    used = "used"  # Task used dataset as input
    output = "output"  # Task output dataset
    connected = "connected"  # Model run connected to dataset output from task
    consumed = "consumed"  # Model run consumed dataset
    relates = "relates"  # task relates to another task
