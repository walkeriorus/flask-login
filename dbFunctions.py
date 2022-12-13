def connectDb( dbObj ):
    '''Param: dbObj, base de datos
    return: connection, type: connection object;
    return: cursor, type: cursor object'''
    connection = dbObj.connect()
    cursor = connection.cursor()

    return connection, cursor

def searchById( dbObj,dbName, dbTable, fieldId , idToSearch ):
    conn, curr = connectDb(dbObj)
    """param: dbName, type: string;
    param: dbTable, type:string;
    param: fieldId, type:string"""
    sql = f"""SELECT * FROM `{dbName}`.`{dbTable}`
    WHERE {fieldId} = {idToSearch}"""
    curr.execute(sql)
    results = curr.fetchone()

    conn.commit()

    return results

def searchUserById(dbObj,dbName, dbTable, fieldId , idToSearch):
    user = searchById(dbObj,dbName, dbTable, fieldId , idToSearch)
    return user
