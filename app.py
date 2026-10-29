import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Restaurant Management System", page_icon="🍽️", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:1.5rem}
[data-testid="stMetric"]{background:#ffffff;border:1px solid #e7eaf0;padding:14px;border-radius:12px}
div.stButton>button{border-radius:8px}
</style>
""", unsafe_allow_html=True)

def init_state():
    defaults = {
        "menu": [
            {"id": 1, "name": "Paneer Butter Masala", "category": "Main Course", "price": 240.0},
            {"id": 2, "name": "Veg Biryani", "category": "Main Course", "price": 180.0},
            {"id": 3, "name": "Masala Dosa", "category": "Main Course", "price": 130.0},
            {"id": 4, "name": "Paneer Tikka", "category": "Starter", "price": 190.0},
            {"id": 5, "name": "Fresh Lime Soda", "category": "Beverage", "price": 70.0},
            {"id": 6, "name": "Gulab Jamun", "category": "Dessert", "price": 60.0},
        ],
        "inventory": [
            {"id": 1, "item": "Paneer (kg)", "quantity": 2, "reorder_level": 3},
            {"id": 2, "item": "Rice (kg)", "quantity": 12, "reorder_level": 5},
            {"id": 3, "item": "Cooking oil (L)", "quantity": 3, "reorder_level": 4},
            {"id": 4, "item": "Soft drink bottles", "quantity": 18, "reorder_level": 6},
        ],
        "staff": [
            {"id": 1, "name": "Aarav Shah", "role": "Waiter"},
            {"id": 2, "name": "Meera Patel", "role": "Chef"},
            {"id": 3, "name": "Rohan Mehta", "role": "Cashier"},
            {"id": 4, "name": "Nisha Desai", "role": "Manager"},
        ],
        "orders": [
            {"id": 1001, "customer": "Walk-in", "table": 2, "items": [{"name":"Paneer Butter Masala","price":240.0,"qty":1},{"name":"Fresh Lime Soda","price":70.0,"qty":1}], "status":"Preparing", "created": "Demo data"},
            {"id": 1002, "customer": "Priya", "table": 4, "items": [{"name":"Veg Biryani","price":180.0,"qty":2}], "status":"Ready", "created": "Demo data"},
            {"id": 1003, "customer": "Walk-in", "table": 6, "items": [{"name":"Masala Dosa","price":130.0,"qty":1}], "status":"Served", "created": "Demo data"},
        ],
        "invoices": [
            {"id": 5001, "order_id": 1001, "subtotal": 310.0, "tax": 15.5, "discount": 0.0, "total": 325.5, "payment": "Unpaid"},
            {"id": 5002, "order_id": 1002, "subtotal": 360.0, "tax": 18.0, "discount": 0.0, "total": 378.0, "payment": "Paid"},
            {"id": 5003, "order_id": 1003, "subtotal": 130.0, "tax": 6.5, "discount": 0.0, "total": 136.5, "payment": "Paid"},
        ],
        "next_order": 1004, "next_invoice": 5004
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

def money(x):
    return f"₹{float(x):,.2f}".replace(".00", "")

def order_total(order):
    return sum(item["price"] * item["qty"] for item in order["items"])

st.title("🍽️ Restaurant Management System")
st.caption("Local academic demonstration · Single-branch restaurant · Sample data only")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choose module", [
        "Overview", "Orders & Tables", "Menu Management", "Billing & Invoices",
        "Inventory", "Staff & Roles", "Sales & Reports", "Objectives & Scope"
    ])
    st.divider()
    st.caption("RMS · Streamlit demo")
    if st.button("Reset demo data", use_container_width=True):
        for k in ["menu","inventory","staff","orders","invoices","next_order","next_invoice"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

orders = st.session_state.orders
invoices = st.session_state.invoices
menu = st.session_state.menu
inventory = st.session_state.inventory
staff = st.session_state.staff

if page == "Overview":
    st.subheader("Restaurant overview")
    paid_total = sum(i["total"] for i in invoices if i["payment"] == "Paid")
    active_orders = [o for o in orders if o["status"] not in ("Served", "Cancelled")]
    low_stock = [x for x in inventory if x["quantity"] <= x["reorder_level"]]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Paid revenue", money(paid_total))
    c2.metric("Active orders", len(active_orders))
    c3.metric("Occupied tables", f"{len(set(o['table'] for o in active_orders))} / 8")
    c4.metric("Low-stock items", len(low_stock))
    left,right = st.columns(2)
    with left:
        st.markdown("#### Table status")
        table_rows = []
        for t in range(1,9):
            order = next((o for o in active_orders if o["table"] == t), None)
            table_rows.append({"Table": f"Table {t}", "Status": order["status"] if order else "Available", "Order": f"#{order['id']}" if order else "—"})
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
    with right:
        st.markdown("#### Recent orders")
        st.dataframe(pd.DataFrame([{"Order":f"#{o['id']}","Customer":o["customer"],"Table":o["table"],"Items":len(o["items"]),"Status":o["status"]} for o in orders[-5:][::-1]]), use_container_width=True, hide_index=True)
    if low_stock:
        st.warning("Low stock alert: " + ", ".join(x["item"] for x in low_stock))
    st.info("Use the sidebar to demonstrate each module. All records are sample data stored in the current Streamlit session.")

elif page == "Orders & Tables":
    st.subheader("Orders and table reservations")
    a,b = st.columns([1,1.4])
    with a:
        st.markdown("#### Create an order")
        active_tables = {o["table"] for o in orders if o["status"] not in ("Served","Cancelled")}
        available_tables = [t for t in range(1,9) if t not in active_tables]
        with st.form("create_order_form", clear_on_submit=True):
            customer = st.text_input("Customer name", placeholder="Walk-in customer")
            table_num = st.selectbox("Available table", available_tables or [1], disabled=not available_tables)
            chosen = st.multiselect("Menu items", options=[m["id"] for m in menu],
                format_func=lambda mid: next((f"{m['name']} — {money(m['price'])}" for m in menu if m["id"]==mid), str(mid)))
            submitted = st.form_submit_button("Create order", type="primary", disabled=not available_tables)
        if submitted:
            if not chosen:
                st.error("Select at least one menu item.")
            else:
                items = []
                for mid in chosen:
                    m = next(m for m in menu if m["id"] == mid)
                    items.append({"name":m["name"],"price":m["price"],"qty":1})
                new_id = st.session_state.next_order
                st.session_state.orders.append({"id":new_id,"customer":customer.strip() or "Walk-in","table":table_num,"items":items,"status":"New","created":datetime.now().strftime("%Y-%m-%d %H:%M")})
                st.session_state.next_order += 1
                st.success(f"Order #{new_id} created.")
                st.rerun()
    with b:
        st.markdown("#### Manage order status")
        if orders:
            ids = [o["id"] for o in orders]
            chosen_order = st.selectbox("Select order", ids, format_func=lambda oid: next(f"#{o['id']} · Table {o['table']} · {o['customer']}" for o in orders if o["id"]==oid))
            selected_order = next(o for o in orders if o["id"] == chosen_order)
            st.write("Items:", ", ".join(f"{i['name']} × {i['qty']}" for i in selected_order["items"]))
            st.write("Order total:", money(order_total(selected_order)))
            new_status = st.selectbox("Update status", ["New","Preparing","Ready","Served","Cancelled"], index=["New","Preparing","Ready","Served","Cancelled"].index(selected_order["status"]))
            if st.button("Save order status"):
                selected_order["status"] = new_status
                st.success("Order status updated.")
                st.rerun()
        st.markdown("#### All orders")
        st.dataframe(pd.DataFrame([{"Order":o["id"],"Customer":o["customer"],"Table":o["table"],"Items":", ".join(i["name"] for i in o["items"]),"Total":order_total(o),"Status":o["status"]} for o in orders]), use_container_width=True, hide_index=True)

elif page == "Menu Management":
    st.subheader("Menu management")
    with st.expander("Add menu item", expanded=True):
        with st.form("add_menu_form", clear_on_submit=True):
            n1,n2,n3 = st.columns([2,1,1])
            item_name = n1.text_input("Item name")
            category = n2.selectbox("Category", ["Starter","Main Course","Beverage","Dessert"])
            price = n3.number_input("Price (₹)", min_value=1.0, value=100.0, step=10.0)
            add_item = st.form_submit_button("Add item", type="primary")
        if add_item:
            if not item_name.strip():
                st.error("Enter an item name.")
            else:
                st.session_state.menu.append({"id":max([m["id"] for m in menu], default=0)+1,"name":item_name.strip(),"category":category,"price":price})
                st.success("Menu item added.")
                st.rerun()
    st.markdown("#### Existing menu items")
    for m in list(menu):
        with st.container(border=True):
            col1,col2,col3,col4,col5 = st.columns([2,1.2,1,1.2,1])
            col1.write(f"**{m['name']}**")
            col2.write(m["category"])
            with col3:
                st.write(money(m["price"]))
            with col4:
                new_price = st.number_input("Price", min_value=1.0, value=float(m["price"]), step=10.0, key=f"price_{m['id']}", label_visibility="collapsed")
                if st.button("Update", key=f"upd_{m['id']}"):
                    m["price"] = new_price
                    st.success("Price updated.")
                    st.rerun()
            with col5:
                if st.button("Remove", key=f"del_{m['id']}"):
                    st.session_state.menu = [x for x in menu if x["id"] != m["id"]]
                    st.rerun()

elif page == "Billing & Invoices":
    st.subheader("Billing and invoice generation")
    uninvoiced = [o for o in orders if not any(i["order_id"] == o["id"] for i in invoices)]
    if not uninvoiced:
        st.info("Every current order already has an invoice. Create a new order to demonstrate a new bill.")
    else:
        with st.form("bill_form"):
            selected_id = st.selectbox("Order to bill", [o["id"] for o in uninvoiced], format_func=lambda oid: next(f"#{o['id']} · Table {o['table']} · {money(order_total(o))}" for o in uninvoiced if o["id"]==oid))
            tax_rate = st.number_input("Tax (%)", min_value=0.0, max_value=30.0, value=5.0, step=0.5)
            discount_rate = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
            create_bill = st.form_submit_button("Generate invoice", type="primary")
        if create_bill:
            order = next(o for o in orders if o["id"] == selected_id)
            subtotal = order_total(order)
            tax = subtotal * tax_rate / 100
            discount = subtotal * discount_rate / 100
            total = max(0, subtotal + tax - discount)
            inv_id = st.session_state.next_invoice
            st.session_state.invoices.append({"id":inv_id,"order_id":selected_id,"subtotal":subtotal,"tax":tax,"discount":discount,"total":total,"payment":"Unpaid"})
            st.session_state.next_invoice += 1
            st.success(f"Invoice #{inv_id} generated. Total: {money(total)}")
            st.rerun()
    st.markdown("#### Invoice history")
    if invoices:
        for inv in invoices:
            with st.container(border=True):
                c1,c2,c3,c4,c5 = st.columns([1,1,1,1,1.5])
                c1.write(f"**Invoice #{inv['id']}**")
                c2.write(f"Order #{inv['order_id']}")
                c3.write(f"Subtotal: {money(inv['subtotal'])}")
                c4.write(f"Total: **{money(inv['total'])}**")
                with c5:
                    st.write(f"Payment: **{inv['payment']}**")
                    if inv["payment"] != "Paid" and st.button("Mark demo payment received", key=f"paid_{inv['id']}"):
                        inv["payment"] = "Paid"
                        st.success("Marked paid in demo mode. No real payment was processed.")
                        st.rerun()
                st.caption(f"Tax {money(inv['tax'])} · Discount {money(inv['discount'])}")
    else:
        st.info("No invoices yet.")

elif page == "Inventory":
    st.subheader("Inventory and stock tracking")
    with st.expander("Add inventory item", expanded=True):
        with st.form("stock_form", clear_on_submit=True):
            c1,c2,c3 = st.columns(3)
            item = c1.text_input("Item name")
            qty = c2.number_input("Available quantity", min_value=0, value=1, step=1)
            reorder = c3.number_input("Reorder level", min_value=0, value=5, step=1)
            add_stock = st.form_submit_button("Add inventory item", type="primary")
        if add_stock:
            if not item.strip():
                st.error("Enter an inventory item name.")
            else:
                st.session_state.inventory.append({"id":max([x["id"] for x in inventory], default=0)+1,"item":item.strip(),"quantity":qty,"reorder_level":reorder})
                st.rerun()
    low = [x for x in inventory if x["quantity"] <= x["reorder_level"]]
    if low:
        st.warning("Low-stock alert: " + ", ".join(x["item"] for x in low))
    for item in list(inventory):
        with st.container(border=True):
            c1,c2,c3,c4,c5 = st.columns([2,1,1,1,1])
            c1.write(f"**{item['item']}**")
            c2.write(f"Qty: {item['quantity']}")
            c3.write(f"Reorder at: {item['reorder_level']}")
            c4.write("⚠️ Low" if item["quantity"] <= item["reorder_level"] else "✅ In stock")
            with c5:
                x,y = st.columns(2)
                if x.button("−1", key=f"minus_{item['id']}"):
                    item["quantity"] = max(0,item["quantity"]-1)
                    st.rerun()
                if y.button("+1", key=f"plus_{item['id']}"):
                    item["quantity"] += 1
                    st.rerun()

elif page == "Staff & Roles":
    st.subheader("Staff and user role management")
    with st.form("staff_form", clear_on_submit=True):
        c1,c2 = st.columns(2)
        staff_name = c1.text_input("Staff name")
        role = c2.selectbox("Role", ["Waiter","Chef","Cashier","Manager"])
        add_staff = st.form_submit_button("Add staff member", type="primary")
    if add_staff:
        if not staff_name.strip():
            st.error("Enter staff name.")
        else:
            st.session_state.staff.append({"id":max([s["id"] for s in staff], default=0)+1,"name":staff_name.strip(),"role":role})
            st.success("Staff member added.")
            st.rerun()
    st.markdown("#### Role permissions (demonstration)")
    roles = {
        "Waiter":"Create orders and update table/order status.",
        "Chef":"View kitchen orders and update preparation status.",
        "Cashier":"Generate invoices and record payment status.",
        "Manager":"Manage menu, inventory, staff and sales reports."
    }
    cols = st.columns(4)
    for col,(r,desc) in zip(cols,roles.items()):
        col.markdown(f"**{r}**")
        col.caption(desc)
    st.info("This prototype demonstrates staff records and role descriptions. Secure login and enforced permissions are not implemented.")
    st.dataframe(pd.DataFrame(staff), use_container_width=True, hide_index=True)
    remove_id = st.selectbox("Select staff member to remove", [s["id"] for s in staff], format_func=lambda sid: next(f"{s['name']} — {s['role']}" for s in staff if s["id"]==sid)) if staff else None
    if remove_id is not None and st.button("Remove selected staff member"):
        st.session_state.staff = [s for s in staff if s["id"] != remove_id]
        st.rerun()

elif page == "Sales & Reports":
    st.subheader("Sales and reporting dashboard")
    gross = sum(i["total"] for i in invoices)
    paid = sum(i["total"] for i in invoices if i["payment"] == "Paid")
    a,b,c,d = st.columns(4)
    a.metric("Gross billed", money(gross))
    b.metric("Payments received", money(paid))
    c.metric("Invoices", len(invoices))
    d.metric("Total orders", len(orders))
    if invoices:
        df = pd.DataFrame([{"Invoice":i["id"],"Order":i["order_id"],"Subtotal":i["subtotal"],"Tax":i["tax"],"Discount":i["discount"],"Total":i["total"],"Payment":i["payment"]} for i in invoices])
        st.markdown("#### Invoice report")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("#### Revenue by invoice")
        st.bar_chart(df.set_index("Invoice")["Total"])
        st.download_button("Download sales report (CSV)", df.to_csv(index=False).encode("utf-8"), file_name="rms_sales_report.csv", mime="text/csv")
    else:
        st.info("Generate invoices to populate reports.")
    st.caption("These are demo figures calculated from the current session's sample records.")

elif page == "Objectives & Scope":
    st.subheader("Project objectives and scope")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("#### Objectives")
        st.markdown("""
1. Automate order taking and billing to reduce errors and processing time.
2. Enable table and reservation management.
3. Maintain accurate inventory records to prevent stock-outs or wastage.
4. Generate sales, revenue and performance reports.
5. Improve customer experience through faster service and accurate order tracking.
6. Provide role-based access examples for waiters, chefs, cashiers and managers.
""")
        st.markdown("#### Stakeholders")
        st.markdown("- Restaurant owner / manager\n- Waitstaff\n- Kitchen staff / chefs\n- Cashier / billing staff\n- Customers\n- Inventory / store manager\n- System administrator / developer")
    with col2:
        st.markdown("#### In scope")
        st.markdown("""
- Table reservation and order management
- Menu management: add, edit, remove items and prices
- Billing and invoice generation
- Inventory and stock tracking
- Staff / user role management
- Sales and reporting dashboard
""")
        st.markdown("#### Out of scope")
        st.markdown("""
- Online food delivery or third-party aggregator integration
- Multi-branch / franchise management
- Full accounting or payroll systems
""")
    st.markdown("#### Suggested live demonstration sequence")
    st.markdown("1. Add a menu item → 2. Create an order and assign a table → 3. Update order status → 4. Generate invoice with tax/discount → 5. Mark demo payment received → 6. Adjust stock and show low-stock warning → 7. Add staff and explain roles → 8. Export sales CSV.")
    st.info("Technology: Python + Streamlit + Pandas. This is a local academic prototype with sample data, not a production deployment.")
