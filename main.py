from fastapi import FastAPI, Request
import db_helper,generic_helper
from fastapi.responses import JSONResponse

app=FastAPI()

inprogress_orders = {}

@app.post('/')
async def handle_request(request:Request):
    payload=await request.json()

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    if intent=="track.order - context: ongoing-tracking":
        return track_order(parameters)

    if intent=="new.order":
        if session_id in inprogress_orders:
            del inprogress_orders[session_id]
        return
    
    if intent=="order.complete - context: ongoing-order":
        return complete_order(parameters,session_id)
    
    if intent=="order.add - context: ongoing-order":
        return add_to_order(parameters,session_id)

    if intent=="order.remove - context: ongoing-order":
        return remove_from_order(parameters,session_id)

def complete_order(parameter:dict, session_id:str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order=inprogress_orders[session_id]
        order_id=save_to_db(order)

        if order_id==-1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                               "Please place a new order again"
        else:
            order_total=db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome. We have placed your order. " \
                           f"Here is your order id # {order_id}. " \
                           f"Your order total is {order_total} which you can pay at the time of delivery!"
            
        del inprogress_orders[session_id]

    return JSONResponse(content={
    "fulfillmentText": fulfillment_text
    })


def save_to_db(order:dict):
    next_order_id=db_helper.get_next_order_id()

    for food_item,quantity in order.items():
        response=db_helper.add_order_details(next_order_id,food_item,quantity)

        if response==-1:
            return -1
        
    db_helper.add_order_tracking(next_order_id,"in progress")

    return next_order_id

def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def remove_from_order(parameter:dict,session_id:str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        })
    
    food_items=parameter["food-item"]
    current_order=inprogress_orders[session_id]

    removed_items=[]
    not_present=[]

    for item in food_items:
        if item not in current_order:
            not_present.append(item)
        else:
            del current_order[item]
            removed_items.append(item)
    
    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

    if len(not_present) > 0:
        fulfillment_text = f' Your current order does not have {",".join(not_present)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def track_order(parameter:dict):
    order_id=int(parameter['order_id'])
    order_status=db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })



