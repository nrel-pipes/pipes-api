
from pipes.common.validators import DomainValidator
from pipes.users.schemas import UserPasswordUpdate, UserCreate
from pipes.common.utilities import parse_organization, DNS_ORG_MAPPING


class UserPasswordUpdateValidator(DomainValidator):
    """Validates that user exists in cognito and mongo"""
    def __init__(self, user: UserPasswordUpdate) -> None:
        self.user = user

    async def validate_user_passsword_update(
            self,
            data: UserPasswordUpdate
    ) -> UserPasswordUpdate:
        """User password update validation."""
        if not data.email:
            raise ValueError("Email is required")
        if not data.old_password or not data.new_password or not data.confirm_password:
            raise ValueError("All password fields are required")
        if data.new_password != data.confirm_password:
            raise ValueError("New password and confirm password do not match")
        return data
