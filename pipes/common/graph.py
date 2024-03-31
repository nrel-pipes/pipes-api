from enum import Enum


class VertexLabel(str, Enum):
    User = "User"
    Team = "Team"
    Project = "Project"
    ProjectRun = "ProjectRun"
    Model = "Model"
    ModelRun = "ModelRun"
    Task = "Task"
