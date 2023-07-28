def json_build_object_columns(t):
    """
    return list of table colums in the format of
    ["col1". t.c.col1, "col2", t.c.col2, ...]
    """
    key_colum_tups: list[tuple] = [(c.key, c) for c in t.c]
    key_col: list = [obj for tup_list_obj in key_colum_tups for obj in tup_list_obj]
    return key_col
