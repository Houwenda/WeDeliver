#!/usr/bin/python3
import psycopg2

dbuser = 'postgres'
dbpasswd = 'postgres'
dbport = '6432'
dbdatabase = 'postgres'

# try connecting to database
def connectPostgresql():
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    print('connect succeeded')

# create 2 tables
def createTable():
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd,host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    print('connect succeeded')
    cursor.execute('''create table public.users(
UserId varchar(256) not null primary key,
Raddress varchar(512) not null,
Points integer not null

)''')
    conn.commit()
    cursor.execute('''create table public.orders(
OrderID varchar(256) not null primary key,
Status integer not null,
DID varchar(256),
RID varchar(256),
Time timestamp not null,
Cargo jsonb not null,
Reward integer not null,
PS varchar(256)
)''')
    conn.commit()
    conn.close()
    print('table users , orders created')

# insert a row into users
def insertUser(uid, radd, pnt):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("insert into public.users(UserID, Raddress, Points) \
values(%s, %s, %s)", (uid, radd, pnt))
    conn.commit()
    conn.close()

# insert a row into orders
def insertOrder(oid, sts, did, rid, tm, cg, rw, ps):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("insert into public.orders(OrderID, Status, DID, RID, Time, Cargo, Reward, PS) \
values(%s, %s, %s, %s, to_timestamp(%s, 'YYYY:MON:DD:HH24:MI:SS'), %s, %s, %s)",(oid, sts, did, rid,tm,cg, rw, ps))
    conn.commit()
    conn.close()

# select user data from users by id
def selectUserById(uid):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("select UserId, Raddress, Points from public.users where UserId=%s",(uid,))
    row = cursor.fetchall()
    conn.close()
    if row == []:
        print('no such user')
        return None, None, None
    print('UserID:', row[0][0],' Raddress:', row[0][1], ' Points:', row[0][2])
    return row[0][0], row[0][1], row[0][2]

# select order data by id 
def selectOrderById(oid):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("select OrderID, Status, DID, RID, Time, Cargo, Reward PS from public.orders where OrderID=%s", (oid,))
    row = cursor.fetchall()
    conn.close()
    if row == []:
        print('no such order')
        return None, None, None, None, None, None, None, None
    print('OrderID:', row[0][0],' Status:', row[0][1], ' DID:', row[0][2], ' RID:', row[0][3], 'Time', row[0][4],' Cargo:', row[0][5], ' Reward:',  row[0][6], ' PS:', row[0][7])
    return row[0][0], row[0][1], row[0][2], row[0][3], row[0][4], row[0][5], row[0][6], row[0][7]

# select order data by status, in order of time desc
def selectOrderByStatus(sts):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("select OrderID, Status, DID, RID, to_char(Time, 'YYYY:MON:DD:HH24:MI:SS'), Cargo, Reward, PS from public.orders where Status=%s order by Time desc", (sts,))
    rows = cursor.fetchall()
    conn.close()
    return rows # rows is possible to be empty

# select order data where time value is ealier than the given value
def selectOrderBeforeTime(tm):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("select OrderID, Status, DID, RID, to_char(Time, 'YYYY:MON:DD:HH24:MI:SS'), Cargo, Reward, PS from public.orders where Time<to_timestamp(%s, 'YYYY:MON:DD:HH24:MI:SS')", (tm,))
    rows = cursor.fetchall()
    conn.close()
    return rows # rows is possible to be empty

def selectOrderByStatusBeforeTime(tm, sts):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("select OrderID, Status, DID, RID, to_char(Time, 'YYYY:MON:DD:HH24:MI:SS'), Cargo, Reward, PS from public.orders where Time<to_timestamp(%s, 'YYYY:MON:DD:HH24:MI:SS') and Status=%s", (tm, sts))
    rows = cursor.fetchall()
    conn.close()
    return rows # rows is possible to be empty
def selectOrderByStatusBeforeTimeByCargo(cg):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("select OrderID, Status, DID, RID, to_char(Time, 'YYYY:MON:DD:HH24:MI:SS'), Cargo, Reward, PS from public.orders where Time<to_timestamp(%s, 'YYYY:MON:DD:HH24:MI:SS') and Status=%s", (tm, sts))
    rows = cursor.fetchall()
    conn.close()
    return rows # rows is possible to be empty
   




# update orders 
def updateOrdersStatusById(oid, sts):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("update public.orders set Status=%s where OrderID=%s", sts, oid)
    conn.commit()
    conn.close()
def updateOrdersCargoById(oid, cg):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("update public.orders set Cargo=%s where OrderID=%s", cg, oid)
    conn.commit()
    conn.close()
def updateOrdersDIDById(oid, did):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("update public.orders set DID=%s where OrderID=%s", did, oid)
    conn.commit()
    conn.close()
def updateOrdersRIDById(oid, rid):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("update public.orders set RID=%s where OrderID=%s", rid, oid)
    conn.commit()
    conn.close()
# update users
def updateUsersPointsById(uid, pnt):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("update public.orders set Points=%s where UserId=%s", pnt, uid)
    conn.commit()
    conn.close()

# delete orders by id
def deleteOrdersById(oid):
    conn = psycopg2.connect(database = dbdatabase, user = dbuser,password = dbpasswd, host = "127.0.0.1", port = dbport )
    cursor = conn.cursor()
    cursor.execute("select OrderID, Status, DID, RID, to_char(Time, 'YYYY:MON:DD:HH24:MI:SS'), Cargo, Reward, PS from public.orders where OrderID=%s", (oid,))
    row = cursor.fetchall()
    if row != []:
        cursor.execute("delete from public.orders where OrderId=%s", oid) 
        conn.commit()
        conn.close()
        return row
    else:
        return None, None, None, None, None, None, None, None


if __name__ == "__main__":
#    connectPostgresql()
#    createTable()
#    insertUser(str(123123), 'testtest', 100)
#    insertOrder(str(456456), 0, 'delivererid', 'recieverid', '2019:MAR:27:16:10:45', '{\"size\":\"big\", \"num\":3}', '10', 'remarks')
#    selectUserById(str(123123))
#    selectOrderById(str(456456))
#    print(selectOrderByStatus(0))
#    print(selectOrderBeforeTime('2019:MAR:28:16:10:45'))
#    print(selectOrderByStatusBeforeTime('2019:MAR:28:16:10:45',0))
#    updateOrdersStatusById(str(456456), 1)
#    updateOrdersCargoById(str(456456), '{}')
#    updateOrdersDIDById(str(456456), '789789')
#    updateOrdresRIDById(str(456456), '789789')
#    updateUsersPointsById(str(123123), 200)
#    deleteOrdersById(str(456456))
    pass
