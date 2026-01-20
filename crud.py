from db import get_connection
from fastapi import HTTPException

def read(payload):
    if "query" not in payload:
        query = "SELECT "
        # SELECT clause
        if "rows" not in payload:
            query += "* "
        else:
            query += ",".join(payload["rows"]) + " "
        # FROM clause
        query += f"FROM {payload['table']} "
        # WHERE clause
        if "where" in payload and payload["where"]:
            where = "WHERE "
            arr = []
            for col, op, val in payload["where"]:
                if isinstance(val, str):
                    val = f"'{val}'"
                arr.append(f"{col} {op} {val}")
            where += ' AND '.join(arr)
            query += where + " "
        # GROUP BY clause
        if "group_by" in payload:
            query += "GROUP BY " + ", ".join(payload["group_by"]) + " "
        # HAVING clause
        if "having" in payload:
            query += "HAVING " + " AND ".join(payload["having"]) + " "
        # ORDER BY clause
        if "order_by" in payload:
            # expected format: [("col", "ASC"), ("col2", "DESC")]
            order_parts = []
            for col, direction in payload["order_by"]:
                order_parts.append(f"{col} {direction}")
            query += "ORDER BY " + ", ".join(order_parts) + " "
        # LIMIT clause
        if "limit" in payload:
            query += f"LIMIT {payload['limit']}"
        #LIMIT offset
        if "offset" in payload:
            query += f"OFFSET {payload['offset']}"
    else:
        query = payload["query"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    print(query)
    # Get column names
    columns = [desc[0] for desc in cursor.description]

    # Fetch all rows
    rows = cursor.fetchall()

    # Convert rows to list of dicts
    data = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return data

def create(payload):
    if "query" not in payload:
        query = "INSERT INTO "

        # table
        query += f"{payload['table']} "

        # columns and values
        columns = []
        values = []

        for col, val in payload["data"].items():
            columns.append(col)
            if isinstance(val, str):
                val = f"'{val}'"
            values.append(str(val))

        query += f"({', '.join(columns)}) "
        query += f"VALUES ({', '.join(values)})"

    else:
        query = payload["query"]
    
    query += ' RETURNING *'
    print(query)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
 
    columns = [desc[0] for desc in cursor.description]

    # Fetch all rows
    rows = cursor.fetchall()

    # Convert rows to list of dicts
    data = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()
    return data

def update(payload):
    if "query" not in payload:
        table = payload.get("table")
        data = payload.get("data")
        where = payload.get("where")

        if not table or not data or not where:
            raise ValueError("Payload must contain 'table', 'data', and 'where'")

        # SET clause
        set_clause = []
        for col, val in data.items():
            if isinstance(val, str):
                val = f"'{val}'"
            set_clause.append(f"{col} = {val}")
        set_str = ", ".join(set_clause)

        # WHERE clause
        where_clause = []
        for col, op, val in where:
            if isinstance(val, str):
                val = f"'{val}'"
            where_clause.append(f"{col} {op} {val}")
        where_str = " AND ".join(where_clause)

        query = f"UPDATE {table} SET {set_str} WHERE {where_str} RETURNING *    "

    else:
        query = payload["query"]

    print(query)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
 
    columns = [desc[0] for desc in cursor.description]

    # Fetch all rows
    rows = cursor.fetchall()

    # Convert rows to list of dicts
    data = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()
    return data

def delete(payload):
    if "query" not in payload:
        table = payload.get("table")
        where = payload.get("where")

        if not table or not where:
            raise ValueError("Payload must contain 'table' and 'where'")

        # WHERE clause
        where_clause = []
        for col, op, val in where:
            if isinstance(val, str):
                val = f"'{val}'"
            where_clause.append(f"{col} {op} {val}")
        where_str = " AND ".join(where_clause)

        query = f"DELETE FROM {table} WHERE {where_str}"

    else:
        query = payload["query"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()

    try:
        data = cursor.fetchall()
    except:
        data = None

    cursor.close()
    conn.close()
    return data
