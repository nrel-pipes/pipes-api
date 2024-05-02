import json
import os
import sys
from pathlib import Path

import toml
import requests

root_dir = Path(__file__).parents[1].absolute()
templates_dir = root_dir.joinpath("scripts", "templates")
host = "http://127.0.0.1:8080"

cognito_access_token = os.getenv("PIPES_COGNITO_ACCESS_TOKEN", None)
if not cognito_access_token:
    print("Please set the PIPES_COGNITO_ACCESS_TOKEN environment variable.")
    sys.exit(1)

headers = {
    "Authorization": "Bearer " + cognito_access_token,
}


# Read template
p_template_file = templates_dir.joinpath("test_project.toml")
with open(p_template_file) as f:
    data = toml.load(f)

raw_project = data["project"]
raw_projectruns = data["project_runs"]
raw_teams = data["model_teams"]

# Create project
p_name = raw_project["name"]

clean_project = dict(
    name=p_name,
    title=raw_project["full_name"],
    description=raw_project["description"],
    assumptions=raw_project["assumptions"],
    requirements=raw_project["requirements"],
    scenarios=raw_project["scenarios"],
    sensitivities=raw_project["sensitivities"],
    milestones=raw_project["milestones"],
    scheduled_start=raw_project["scheduled_start"],
    scheduled_end=raw_project["scheduled_end"],
    owner=raw_project["owner"],
)

p_url = f"{host}/api/projects"
response = requests.post(p_url, data=json.dumps(clean_project), headers=headers)
if response.status_code != 201:
    print(p_url, response.text)
else:
    print(f"Project {p_name} created successfully.")


# Create project teams
t_url = f"{host}/api/teams?project={p_name}"
for team in raw_teams:
    t_name = team["name"]
    response = requests.post(t_url, data=json.dumps(team), headers=headers)
    if response.status_code != 201:
        print(t_url, response.text)
    else:
        print(f"Team {t_name} created successfully.")

# Create project runs
pr_url = f"{host}/api/projectruns?project={p_name}"
for projectrun in raw_projectruns:
    pr_name = projectrun["name"]
    response = requests.post(pr_url, data=json.dumps(projectrun), headers=headers)
    if response.status_code != 201:
        print(pr_url, response.text)
    else:
        print(f"Project run {pr_name} created successfully.")

    # Add models to project runs
    m_url = f"{host}/api/models?project={p_name}&projectrun={pr_name}"
    for raw_model in projectrun["models"]:
        clean_model = raw_model.copy()
        clean_model["name"] = raw_model["model"]
        m_name = clean_model["name"]
        if not clean_model.get("modeling_team", None):
            clean_model["modeling_team"] = raw_model["model"]

        response = requests.post(m_url, data=json.dumps(clean_model), headers=headers)
        if response.status_code != 201:
            print(m_url, response.text)
        else:
            print(f"Model {m_name} created successfully.")

    # Create handoff plans
    topology = projectrun["topology"]
    handoffs = []
    for topo in topology:
        for h in topo["handoffs"]:
            handoff = {
                "from_model": topo["from_model"],
                "to_model": topo["to_model"],
                "name": h["id"],
                "description": h["description"],
                "scheduled_start": h["scheduled_start"],
                "scheduled_end": h["scheduled_end"],
                "notes": h["notes"],
            }
            handoffs.append(handoff)
    h_url = f"{host}/api/handoffs?project={p_name}&projectrun={pr_name}"
    response = requests.post(h_url, data=json.dumps(handoffs), headers=headers)
    if response.status_code != 201:
        print(h_url, response.text)
    else:
        print(f"{len(handoffs)} Handoffs created successfully.")


# Model runs
mr_template_file = templates_dir.joinpath("test_model_run.toml")
with open(mr_template_file) as f:
    raw_modelrun = toml.load(f)

mr_name = raw_modelrun["name"]
clean_modelrun = {
    "name": mr_name,
    "description": raw_modelrun["description"],
    "version": raw_modelrun["version"],
    "assumptions": raw_modelrun["assumptions"],
    "notes": ";".join(raw_modelrun["notes"]),
    "source_code": raw_modelrun["source_code"],
    "config": raw_modelrun["config"],
    "env_deps": raw_modelrun["config"],
    "datasets": [],
}
mr_url = f"{host}/api/modelruns?project={p_name}&projectrun={pr_name}&model=dsgrid"
response = requests.post(mr_url, data=json.dumps(clean_modelrun), headers=headers)
if response.status_code != 201:
    print(mr_url, response.text)
else:
    print(f"Model run {mr_name} created successfully.")


# Checkin dataset
d_template_file = templates_dir.joinpath("test_dataset.toml")
with open(d_template_file) as f:
    data = toml.load(f)

raw_dataset = data["dataset"]
clean_dataset = raw_dataset.copy()
d_name = clean_dataset["name"]
d_url = f"{host}/api/datasets?project={p_name}&projectrun={pr_name}&model=dsgrid&modelrun={mr_name}"
response = requests.post(d_url, data=json.dumps(clean_dataset), headers=headers)
if response.status_code != 201:
    print(d_url, response.text)
else:
    print(f"Dataset {d_name} created successfully.")
