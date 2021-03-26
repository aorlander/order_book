from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#Your solution should be in a file called ‘order_book.py’ and it should 
#contain a method 'process_order(order)'. The function ‘process_order’ 
#takes a single argument, a dictionary object containing the 6 fields above.
def process_order(order):
    
    #1. Insert the order into the database. Insert the order into the “order” table. Make sure you set the following fields:
    current_order = Order( sender_pk=order['sender_pk'], receiver_pk=order['receiver_pk'], buy_currency=order['buy_currency'], sell_currency=order['sell_currency'], buy_amount=order['buy_amount'], sell_amount=order['sell_amount'])
    current_order.timestamp = datetime.now()
    session.add(current_order)
    session.commit()

    #2. Check if there are any existing orders that match. Given new_order and existing order, \
    #   to match all of the following requirements must be fulfilled:
    #      1) existing_order.filled must be None
    #      2) existing_order.expiration must be None or a time in the future
    #      3) existing_order.buy_currency == order.sell_currency
    #      4) existing_order.sell_currency == order.buy_currency
    #      5) The implied exchange rate of the new order must be at least that of the existing order (existing_order.sell_amount / existing_order.buy_amount >= order.buy_amount/order.sell_amount)
    #      6) The buy / sell amounts need not match exactly
    #      7) Each order should match at most one other
    #print("\n current: SELL " + str(current_order.sell_amount) + " " + current_order.sell_currency + " / BUY " + str(current_order.buy_amount) + " " + current_order.buy_currency)

    for existing_order in session.query(Order).filter(Order.filled == None):
        if(current_order.filled==None): 
            if(existing_order.buy_currency == current_order.sell_currency):
                if(existing_order.sell_currency == current_order.buy_currency):
                    if(existing_order.sell_amount / existing_order.buy_amount >= current_order.buy_amount/current_order.sell_amount):
                        if (existing_order.sell_amount < current_order.buy_amount):
                            #print("existing SELL " + str(existing_order.sell_amount) + " " + existing_order.sell_currency + " / current BUY " + str(current_order.buy_amount) + " " + current_order.buy_currency)
                            #print("existing BUY " + str(existing_order.buy_amount) + " " + existing_order.buy_currency + " / current SELL " + str(current_order.sell_amount) + " " + current_order.sell_currency)
                            remaining_sell_amount = current_order.sell_amount - existing_order.buy_amount
                            remaining_buy_amount = current_order.buy_amount - existing_order.sell_amount
                            child_order = Order (
                                creator_id=current_order.id, 
                                sender_pk=current_order.sender_pk,
                                receiver_pk=current_order.receiver_pk, 
                                buy_currency=current_order.buy_currency, 
                                sell_currency=current_order.sell_currency, 
                                buy_amount=remaining_buy_amount, 
                                sell_amount=remaining_sell_amount )
                            child_order.timestamp = datetime.now()
                            child_order.relationship = (child_order.id, current_order.id)
                            current_order.relationship = (child_order.id, current_order.id)
                            session.add(child_order)
                            session.commit()
                            #print("created: SELL " + str(child_order.sell_amount) + " " + child_order.sell_currency + " / BUY " + str(child_order.buy_amount) + " " + child_order.buy_currency)

                            existing_order.counterparty_id = current_order.id
                            existing_order.filled = current_order.timestamp #or does this mean NOW?
                            current_order.counterparty_id = existing_order.id
                            current_order.filled = current_order.timestamp

    #print("ALL: ")
    #for o in session.query(Order):
    #    print(str(o.id) + ": SELL " + str(o.sell_amount) + " " + o.sell_currency + " / BUY " + str(o.buy_amount) + " " + o.buy_currency + " ( " + str(o.creator_id) + " )")
    #print("FILLED: ")
    #for o in session.query(Order).filter(Order.filled != None):
    #    print(str(o.id) + ": SELL " + str(o.sell_amount) + " " + o.sell_currency + " / BUY " + str(o.buy_amount) + " " + o.buy_currency + " ( " + str(o.creator_id) + " )")

                        
                        

    #3. If a match is found between order and existing_order:
    #      – Set the filled field to be the current timestamp on both orders
    #      – Set counterparty_id to be the id of the other order
    #      – If one of the orders is not completely filled (i.e. the counterparty’s sell_amount is less than buy_amount):
    #            -Create a new order for remaining balance
    #            -The new order should have the created_by field set to the id of its parent order
    #            -The new order should have the same pk and platform as its parent order
    #            -The sell_amount of the new order can be any value such that the implied exchange rate of the new order is at least that of the old order
    #            -You can then try to fill the new order
    # If there are multiple ways to fill an order, you may choose any method such that:
    # -Each order matches at most one other (to match one order against multiple others create derivative orders, and set the “created_by” field as described above)
    # -Any derived orders must have an implied exchange rate that is at least the original exchange rate, i.e., buy_amount/sell_amount on the new order must be at least the buy_amount/sell_amount on the order that created it


    #DB should provide a complete history of all orders submitted and filled - do not delete filled orders; create derived orders with creator_id
    
    pass