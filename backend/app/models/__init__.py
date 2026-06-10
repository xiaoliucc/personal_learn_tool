"""
数据库基类和模型注册

所有 ORM 模型必须在此导入，否则 create_all 不会创建对应表。
每个新模型文件创建后，需要在此添加 import。
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy ORM 基类"""
    pass


# ---- 模型导入（注册到 Base.metadata） ----
from .material import Material, Tag, MaterialTag  # noqa: F401, E402
from .summary import Summary                      # noqa: F401, E402
from .connection import MaterialConnection        # noqa: F401, E402
from .review import ReviewItem                    # noqa: F401, E402
