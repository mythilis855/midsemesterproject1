import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time


if "page" not in st.session_state:
    st.session_state["page"] = "home"

if "messages" not in st.session_state:
    st.session_state["messages"]= [
        
        {
            "role": "assistant",
            "content": "Hi! How can I help you?"
        }
    ]

inventory = [
    {
        "id": 1,
        "name": "Bananas",
        "price": 1.5,
        "stock": 41
    },
    {
        "id": 2,
        "name": "Milk",
        "price": 4.25,
        "stock": 25
    },
    {
        "id": 3,
        "name": "Eggs",
        "price": 5.75,
        "stock": 20
    },
    {
        "id": 4,
        "name": "Bread",
        "price": 3.5,
        "stock": 20
    },
    {
        "id": 5,
        "name": "Meat",
        "price": 12.95,
        "stock": 18
    }
]

with st.sidebar:
   
    if st.button("Home",key="home_btn",type="primary",use_container_width=True):
       st.session_state["page"]="home"
       st.rerun()
    
    if st.button("Orders",key="orders_btn",type="primary", use_container_width=True):
        st.session_state["page"]= "orders"
        st.rerun()
    
    if st.button("Inventory",key="inventory_btn",type="primary",use_container_width=True):
        st.session_state["page"]="inventory"
        st.rerun()


json_path_inventory = Path("inventory.json")
if json_path_inventory.exists():
    with open(json_path_inventory, "r") as f:
        inventory = json.load(f)
json_path_orders = Path("order.json")
if json_path_orders.exists():
    with open(json_path_orders,"r") as f:
        orders = json.load(f)
else:
    orders=[]


if st.session_state["page"] == "home":
    st.markdown(" # Mythili and Annette's Grocery Store : Home Page")
    col1, col2 = st.columns([4,2])
    with col1:
        selected_category= st.radio("Select a List", ["Inventory", "Orders"], horizontal=True)
        if selected_category == "Inventory":
            if len(inventory)>0:
                st.dataframe(inventory)
            else: 
                st.warning("No item in the inventory")
        else:
            if len(orders)> 0:
                st.dataframe(orders)
            else:
                st.warning("No order is recorded yet")
    with col2:
        if selected_category == "Inventory":
            st.metric("Total Inventory", f"{len(inventory)}")
            st.markdown("** Total Invetory")
            st.divider()
        else:
            st.metric("Total Orders", f"{len(orders)}")

elif st.session_state["page"] == "orders":
    tab1, tab2 = st.tabs(["Add New Order", "Cancel Order"])
    with tab1:
        col1,col2= st.columns([3,3])


        with col1:
            st.subheader("Add New Order")
            with st.container(border= True): 

                selected_item= st.selectbox("Items",options=inventory,
                                        format_func= lambda x: f"{x["name"]}, Stock: {x["stock"]}")

                quantity = st.number_input("Quantity",min_value=1, step=1)

                if st.button("Create Order", key="create_order_btn",type="primary",use_container_width=True):
                    with st.spinner("Creating the order ... "):
                        total= quantity * selected_item["unit_price"]
                        for item in inventory:
                            if item["item_id"]==selected_item["item_id"]:
                                item["stock"]=item["stock"]- quantity 
                                break

                        orders.append(
                            {
                                "id": str(uuid.uuid4()),
                                "item_id": selected_item["item_id"],
                                "quantity":quantity,
                                "status": "placed",
                                "total": total
                            }
                        )
                        with open(json_path_inventory,"w") as f:
                            json.dump(inventory,f)

                        with open(json_path_orders, "w") as f:
                            json.dump(orders,f)

                        st.baloons()

                        time.sleep(5)
                        st.session_state["page"] = "home"
    with col2:
        st.subheader("Chatbot- Ai Assistant")
        col11,col22=st.columns([2,2])
        with col11:
            st.caption("Try Asking: How Can I Add a New Order?")
        with col2:
            if st.button("Clear", key="clear_chat_btn"):
                if "messages" not in st.session_state:
                    st.session_state["messages"]= [
                         {
            "role": "assistant",
            "content": "Hi! How can I help you?"
                        }
            ]



        with st.container(border=True, height=250):
            for message in st.session_state["messages"]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        user_input = st.chat_input("Ask a question...")
        if user_input:
            with st.spinner("Thinking..."):
                st.session_state["messages"].append(
                    {
                        "role": "user",
                        "content": user_input
                    }
                )

                ai_response="I could not find an answer for it, try again!"

                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": ai_response 
                    }
                )
    with tab2: 
        st.subheader("Cancel Order") 

