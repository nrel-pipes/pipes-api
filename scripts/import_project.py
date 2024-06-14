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

url1 = f"{host}/api/projects/"
response = requests.post(url1, data=json.dumps(clean_project), headers=headers)
if response.status_code != 201:
    print(url1, response.text)


# Create project teams
url2 = f"{host}/api/teams/?project={p_name}"
for team in raw_teams:
    response = requests.post(url2, data=json.dumps(team), headers=headers)
    if response.status_code != 201:
        print(url2, response.text)


# Create project runs
url3 = f"{host}/api/projectruns/?project={p_name}"
for projectrun in raw_projectruns:
    response = requests.post(url3, data=json.dumps(projectrun), headers=headers)
    if response.status_code != 201:
        print(url3, response.text)

    # Add models to project runs
    pr_name = projectrun["name"]
    url4 = f"{host}/api/models/?project={p_name}&projectrun={pr_name}"
    for raw_model in projectrun["models"]:
        clean_model = raw_model.copy()
        clean_model["name"] = raw_model["model"]
        if not clean_model.get("modeling_team", None):
            clean_model["modeling_team"] = raw_model["model"]

        response = requests.post(url4, data=json.dumps(clean_model), headers=headers)
        if response.status_code != 201:
            print(url4, response.text)


# Model runs
mr_template_file = templates_dir.joinpath("test_model_run.toml")
with open(mr_template_file) as f:
    raw_modelrun = toml.load(f)

modelrun_name = raw_modelrun["name"]
clean_modelrun = {
    "name": modelrun_name,
    "description": raw_modelrun["description"],
    "version": raw_modelrun["version"],
    "assumptions": raw_modelrun["assumptions"],
    "notes": ";".join(raw_modelrun["notes"]),
    "source_code": raw_modelrun["source_code"],
    "config": raw_modelrun["config"],
    "env_deps": raw_modelrun["config"],
    "datasets": [],
}
url5 = f"{host}/api/modelruns/?project={p_name}&projectrun={pr_name}&model=dsgrid"
response = requests.post(url5, data=json.dumps(clean_modelrun), headers=headers)
if response.status_code != 201:
    print(url5, response.text)


# Checkin dataset
d_template_file = templates_dir.joinpath("test_dataset.toml")
with open(d_template_file) as f:
    data = toml.load(f)

raw_dataset = data["dataset"]
clean_dataset = raw_dataset.copy()

url6 = f"{host}/api/datasets/?project={p_name}&projectrun={pr_name}&model=dsgrid&modelrun={modelrun_name}"
response = requests.post(url6, data=json.dumps(clean_dataset), headers=headers)
if response.status_code != 201:
    print(url6, response.text)
