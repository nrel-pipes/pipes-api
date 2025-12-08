from enum import Enum


class NodeLabel(str, Enum):
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


DNS_ORG_MAPPING = {
    "lbl.gov": "Lawrence Berkeley National Laboratory (LBNL)",
    "ornl.gov": "Oak Ridge National Laboratory (ORNL)",
    "anl.gov": "Argonne National Laboratory (ANL)",
    "ameslab.gov": "Ames National Laboratory",
    "bnl.gov": "Brookhaven National Laboratory (BNL)",
    "www.pppl.gov": "Princeton Plasma Physics Laboratory (PPPL)",
    "slac.stanford.edu": "SLAC National Accelerator Laboratory",
    "pnnl.gov": "Pacific Northwest National Laboratory (PNNL)",
    "fnal.gov": "Fermi National Accelerator Laboratory (FNAL)",
    "jlab.org": "Thomas Jefferson National Accelerator Facility (TJNAF)",
    "lanl.gov": "Los Alamos National Laboratory (LANL)",
    "sandia.gov": "Sandia National Laboratories (SNL)",
    "llnl.gov": "Lawrence Livermore National Laboratory (LLNL)",
    "nrel.gov": "National Laboratory of the Rockies (NLR)",
    "srnl.doe.gov": "Savannah River National Laboratory (SRNL)",
    "netl.doe.gov": "National Energy Technology Laboratory (NETL)",
    "inl.gov": "Idaho National Laboratory (INL)",
}
