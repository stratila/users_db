import pytest
import math
from users_db.users import get_users


def test_pagination(users_data):
    user_ids = [user["id"] for user in users_data]
    PAGE_SIZE = 10
    PAGES = math.ceil(len(user_ids) / PAGE_SIZE)

    for page in range(1, PAGES + 1):
        users = get_users(
            user_ids=user_ids, is_paginated=True, page=page, page_size=PAGE_SIZE
        )
        print(users)
        assert users["page_size"] >= len(users["items"])
        assert users["items_count"] == len(user_ids)
        assert users["page"] == page
        assert users["pages"] == PAGES


def test_pagination_miss_arguments():
    with pytest.raises(ValueError):
        get_users(is_paginated=True, page=1)
    with pytest.raises(ValueError):
        get_users(is_paginated=True, page_size=10)
