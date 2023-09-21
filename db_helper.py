import pyodbc

server_name = 'DESKTOP-4A1KN01'
database_name = 'FoodBuddyChatBot'
username = 'foodBuddy'
password = 'foodBuddy1'

connection_string = f"DRIVER=SQL Server;SERVER={server_name};DATABASE={database_name};UID={username};PWD={password}"
#connection_string = "Data Source=DESKTOP-4A1KN01;Initial Catalog=InventoryManagementSystem;Integrated Security=True"
conn = pyodbc.connect(connection_string)

def add_order_details(order_id,food_item,quantity):
    try:
        cursor = conn.cursor()
        cursor.execute("EXEC sp_AddOrderDetails ?, ?, ?", (order_id,food_item,quantity))
        #cursor.callproc('add_order_details',(order_id,food_item,quantity))
        conn.commit()
        cursor.close()

        print("Order item inserted successfully!")
        return 1
    except Exception as e:
        print(f"Error adding order details{e}")
        return -1

def get_total_order_price(order_id):
    cursor = conn.cursor()
    query = f"SELECT SUM(total_price) FROM orders WHERE order_id = {order_id}"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    print(result)
    cursor.close()
    return result

# Function to get the next available order_id
def get_next_order_id():
    cursor = conn.cursor()

    # Executing the SQL query to get the next available order_id
    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    # Returning the next available order_id
    if result is None:
        return 1
    else:
        return result + 1

def add_order_tracking(order_id, status):
    cursor = conn.cursor()
    query = f"INSERT INTO order_tracking VALUES({order_id},'{status}')"
    cursor.execute(query)
    conn.commit()
    cursor.close()

def get_order_status(order_id:int):
    
    cursor = conn.cursor()
    query = f"SELECT status FROM order_tracking WHERE order_id = {order_id}"
    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    if result:
        return result[0]
    else:
        return None
    

    

