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
template_file = templates_dir.joinpath("test_project.toml")
with open(template_file) as f:
    data = toml.load(f)


raw_project = data["project"]
raw_projectruns = data["project_runs"]
raw_teams = data["model_teams"]

# Create project
project_name = raw_project["name"]

clean_project = dict(
    name=project_name,
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

url = f"{host}/api/projects/"
response = requests.post(url, data=json.dumps(clean_project), headers=headers)
if response.status_code != 201:
    print(response.text)
else:
    print(json.dumps(response.json(), indent=2))


# Create project teams
url = f"{host}/api/teams/?project={project_name}"
for team in raw_teams:
    response = requests.post(url, data=json.dumps(team), headers=headers)
    if response.status_code != 201:
        print(response.text)
    else:
        print(response.status_code, url, response.json())


# Create project runs
url = f"{host}/api/projectruns/?project={project_name}"
for projectrun in raw_projectruns:
    response = requests.post(url, data=json.dumps(projectrun), headers=headers)
    if response.status_code != 201:
        print(response.text)
    else:
        print(response.status_code, url, response.json())
