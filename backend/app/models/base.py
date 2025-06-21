# Import all the models, so that Base has them before being
# imported by Alembic
from .user_financials_model import UserFinancials  # noqa
from .user_profile import User  # noqa
from database import Base  # noqa 