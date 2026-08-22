from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: type[ModelT]) -> None:
        self.model = model

    def get(self, db: Session, item_id: Any) -> ModelT | None:
        return db.get(self.model, item_id)

    def list(self, db: Session, statement: Select[tuple[ModelT]], page: int, size: int) -> tuple[list[ModelT], int]:
        total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
        items = list(db.scalars(statement.offset((page - 1) * size).limit(size)))
        return items, total

    def create(self, db: Session, data: dict[str, Any]) -> ModelT:
        item = self.model(**data)
        db.add(item); db.commit(); db.refresh(item)
        return item

    def update(self, db: Session, item: ModelT, data: dict[str, Any]) -> ModelT:
        for key, value in data.items():
            setattr(item, key, value)
        db.commit(); db.refresh(item)
        return item

    def delete(self, db: Session, item: ModelT) -> None:
        db.delete(item); db.commit()
