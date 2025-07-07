from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from pipes.common.exceptions import (
    ContextValidationError,
    DomainValidationError,
    UserPermissionDenied,
)
from pipes.common.validators import ContextValidator, DomainValidator
from pipes.db.document import DocumentDB
from pipes.projects.contexts import ProjectSimpleContext, ProjectDocumentContext
from pipes.projects.schemas import ProjectCreate, ProjectDocument, ProjectUpdate
from pipes.users.schemas import UserDocument
from pipes.projectruns.schemas import ProjectRunRead


class ProjectContextValidator(ContextValidator):
    """Project context validator class"""

    async def validate_document(
        self,
        context: ProjectSimpleContext,
    ) -> ProjectDocumentContext:
        """Get project document through validation"""
        p_name = context.project
        docdb = DocumentDB()
        p_doc = await docdb.find_one(collection=ProjectDocument, query={"name": p_name})

        if not p_doc:
            raise ContextValidationError(
                f"Invalid context, project '{p_name}' does not exist",
            )

        validated_context = ProjectDocumentContext(project=p_doc)
        self._validated_context = validated_context

        return validated_context

    async def validate_permission(self, user: UserDocument) -> bool:
        """Check user permission in context through validation"""
        await super().validate_permission(user)

        if not self._validated_context:
            raise ContextValidationError("Context document not been validated.")

        p_doc = self._validated_context.project

        # TODO: Hardcoded granting PIPES test projects to all PIPES users
        if p_doc.name in ["test1", "pipes101"]:
            return True

        is_superuser = user.is_superuser
        is_owner = user.id == p_doc.owner
        is_lead = user.id in p_doc.leads
        is_creator = user.id == p_doc.created_by

        if not (is_superuser or is_owner or is_lead or is_creator):
            raise UserPermissionDenied(
                f"User has no access to project '{p_doc.name}'.",
            )

        return True


class ProjectDomainValidator(DomainValidator):
    """Project run domain validator class"""

    async def validate_scheduled_start(self, p_create: ProjectCreate) -> ProjectCreate:
        """Project scheduled start <= scheduled_end"""

        if p_create.scheduled_start > p_create.scheduled_end:
            raise DomainValidationError(
                "Project 'scheduled_start' could not be larger than 'scheduled_end'.",
            )

        return p_create

    async def validate_scheduled_end(self, p_create: ProjectCreate) -> ProjectCreate:
        """Project scheduled start <= scheduled_end"""

        if p_create.scheduled_end < p_create.scheduled_start:
            raise DomainValidationError(
                "Project 'scheduled_end' could not be smaller than 'scheduled_start'.",
            )

        return p_create


class ProjectUpdateDomainValidator(DomainValidator):
    """Project run domain validator class"""

    # TODO: Check and refactor this class for project update logic validation later.

    def get_dependency_data(self, projectrun_docs: list[ProjectRunRead]):
        dependency_data = {
            "scenarios": [],
            "scheduled_start": datetime.max,
            "scheduled_end": datetime.min,
        }

        # Create a set to collect unique scenarios
        scenarios_set = set()

        for projectrun in projectrun_docs:
            # Add scenarios to set
            if projectrun.scenarios:
                scenarios_set.update(projectrun.scenarios)

            # Update earliest start time
            if projectrun.scheduled_start:
                if dependency_data["scheduled_start"] is None or (
                    isinstance(dependency_data["scheduled_start"], datetime)
                    and projectrun.scheduled_start < dependency_data["scheduled_start"]
                ):
                    dependency_data["scheduled_start"] = projectrun.scheduled_start

            # Update latest end time
            if projectrun.scheduled_end:
                if dependency_data["scheduled_end"] is None or (
                    isinstance(dependency_data["scheduled_end"], datetime)
                    and projectrun.scheduled_end > dependency_data["scheduled_end"]
                ):
                    dependency_data["scheduled_end"] = projectrun.scheduled_end

        # Convert scenarios set to list
        dependency_data["scenarios"] = list(scenarios_set)

        return dependency_data

    async def project_validate(
        self,
        instance: BaseModel,
        projectrun_docs: list[ProjectRunRead],
    ) -> BaseModel:
        """Call validation methods with names starting with validate_"""

        dependency_data = self.get_dependency_data(projectrun_docs)
        for attr_name in dir(self):
            if attr_name.startswith("validate_dependency_"):
                validate_method = getattr(self, attr_name)
                instance = await validate_method(instance, dependency_data)
            elif attr_name.startswith("validate_"):
                validate_method = getattr(self, attr_name)
                instance = await validate_method(instance)
            else:
                continue

        # return instance
        return instance

    async def validate_name(self, p_update: ProjectUpdate) -> ProjectUpdate:
        """Validates name no none or empty string. Make sure document does not already exist"""
        if p_update.name in ["", None]:
            raise DomainValidationError(
                "Project must have nonempty name.",
            )
        return p_update

    async def validate_dependency_scheduled_start(
        self,
        p_update: ProjectUpdate,
        dependency_data: dict,
    ) -> ProjectUpdate:
        """Project scheduled start <= scheduled_end. Also, should be less than or equal to dependency_data[start]."""
        if p_update.scheduled_start > p_update.scheduled_end:
            raise DomainValidationError(
                "Project 'scheduled_start' could not be larger than 'scheduled_end'.",
            )

        # Check if the new start time would conflict with dependent runs
        if p_update.scheduled_start > dependency_data["scheduled_start"]:
            raise DomainValidationError(
                "Project 'scheduled_start' cannot be later than the earliest dependent run start time.",
            )

        return p_update

    async def validate_dependency_project_scheduled_end(
        self,
        p_update: ProjectUpdate,
        dependency_data: dict,
    ) -> ProjectUpdate:
        """
        Project scheduled start <= scheduled_end. Also, time should be greater than or equal to dependency_data[end].
        """
        if p_update.scheduled_end < p_update.scheduled_start:
            raise DomainValidationError(
                "Project 'scheduled_end' could not be smaller than 'scheduled_start'.",
            )

        # Check if the new end time would conflict with dependent runs
        if p_update.scheduled_end < dependency_data["scheduled_end"]:
            raise DomainValidationError(
                "Project 'scheduled_end' cannot be earlier than the latest dependent run end time.",
            )

        return p_update

    async def validate_dependency_project_scenarios(
        self,
        p_update: ProjectUpdate,
        dependency_data: dict,
    ) -> ProjectUpdate:
        """Validates that p_update.scenarios contains all scenarios from dependency_data['scenarios']"""
        if not hasattr(p_update, "scenarios"):
            return p_update

        # Extract just the names from p_update.scenarios
        update_scenario_names = (
            {scenario.name for scenario in p_update.scenarios}
            if p_update.scenarios
            else set()
        )
        dependent_scenario_names = set(dependency_data["scenarios"])

        # Check if update_scenario_names is a superset of dependent_scenario_names
        missing_scenarios = dependent_scenario_names - update_scenario_names
        if missing_scenarios:
            raise DomainValidationError(
                f"Project update must contain all dependent scenarios. Missing: {', '.join(missing_scenarios)}",
            )

        return p_update
