# Midsemester-Project
# midsemesterproject1
# midsemesterproject1



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