# Workflows

This documentation shows the concepts of PIPES within workflows.

## Context
* project
* projectrun
* model
* modelrun

## Project
1. An authorized user could create a new project.
2. Project basic information vs detailed information

## Team
1. Team is a general group containing one or multiple users.
2. Team is under project context.
3. You create one or multiple teams within project.
4. Different projects can have teams with same name, but different team members.

## User
1. User registration, register by themselves or through invitation.
2. By default, user has `teams` attribute empty.
3. User does to have direct relation to project, build relations via Team.

## Project Run

1. Operate under `project` context
2. Project run requires models

## Model
1. Operate under `projectrun` context
2. Model has one or multiple modelruns
3. Model to model has handoffs.

## Model Run
1. Operate under `model` context
2. Model run produces datasets

## Dataset
1. Operate under `modelrun` context
2. Apply tasks on datasets for QAQC, transformation, visualzation, etc.

## Task
1. Create task node first in place with status unknown.
2. Contains sub-tasks which are a series of task action items.
3. Operate under `modelrun` context.

## Handoff
1. Under `projectrun`, handoffs are defined between models in high level.
2. Under `modelrun`, handoffs are defined with concret information.
