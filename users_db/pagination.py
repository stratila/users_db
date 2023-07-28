from math import ceil
from functools import wraps

from sqlalchemy import Select, func, select, literal


from users_db.db import db_execute
from users_db.utils import json_build_object_columns


def paginate(f):
    """wrapper kwargs should contain page and page_size"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        db_conn = kwargs.pop("db_conn", None)
        is_paginated = kwargs.pop("is_paginated", False)
        page = kwargs.pop("page", None)
        page_size = kwargs.pop("page_size", None)

        query = f(*args, **kwargs)

        if not is_paginated:
            return db_execute(query, db_conn=db_conn)

        if not page or not page_size:
            raise ValueError("page and page_size must be provided")

        if not isinstance(query, Select):
            raise TypeError("f must return a sqlalchemy.sql.selectable.Select object")

        # calcualate limit and offset
        limit = page_size
        offset = (page - 1) * page_size

        # Get full count of items
        subq_1 = query.alias("subq_1")
        items_count = db_conn.execute(
            select(
                func.count().label("count"),
                # func.json_agg(func.json_build_object(*key_col_list)).label("items"),
            ).select_from(subq_1)
        ).scalar()

        # Get items for the current page
        subq_2 = query.limit(limit).offset(offset).alias("subq_2")

        select_stmt = select(
            literal(items_count).label("items_count"),
            literal(page).label("page"),
            literal(page_size).label("page_size"),
            literal(ceil(items_count / page_size)).label("pages"),
            func.json_agg(
                func.json_build_object(*json_build_object_columns(subq_2))
            ).label("items"),
        ).select_from(subq_2)

        return db_execute(select_stmt, db_conn=db_conn)

    return wrapper
