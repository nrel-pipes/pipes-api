# Workflows

This documentation shows the concepts of PIPES within workflows.

## Project
1. An authorized user could create a new project.
2. Project basic information vs detailed information

## Team
1. Team is a general group containing one or multiple users.
2. Team is under project context.
```json
{
    "project": "test1"
}
```
3. You create one or multiple teams within project.
4. Different projects can have teams with same name, but different team members.

## User
1. User registration, register by themselves or through invitation.
2. By default, user has `teams` attribute empty.
3. User does to have direct relation to project, build relations via Team.
