from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from . import Base


class ProductStatus(PyEnum):
    draft = "draft"
    published = "published"
    archived = "archived"
    deprecated = "deprecated"


class Product(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[Decimal] = mapped_column()
    count: Mapped[int] = mapped_column()
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default="No description")
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus, name="product_status"),
        nullable=False,
        server_default=ProductStatus.draft.value,
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")


# product_status = sa.Enum('draft', 'published', 'archived', name='product_status')
# product_status.create(op.get_bind(), checkfirst=True)
# product_status = sa.Enum('draft', 'published', 'archived', name='product_status')
# product_status.drop(op.get_bind(), checkfirst=True)
