import re

def normalize_query(q: str) -> str:
    q = q.lower()

    # common misspellings
    corrections = {
        "employe": "employee",
        "employess": "employees",
        "emp": "employee",
        "nams": "names",
        "nam": "name",
        "ids": "id",
    }

    for wrong, right in corrections.items():
        q = q.replace(wrong, right)

    # remove junk chars
    q = re.sub(r"[^a-z0-9\s]", "", q)

    return q