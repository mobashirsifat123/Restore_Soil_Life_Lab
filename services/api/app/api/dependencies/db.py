from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import db_session


def get_db_session() -> Generator[Session, None, None]:
    yield from db_session()


DatabaseSession = Annotated[Session, Depends(get_db_session)]
