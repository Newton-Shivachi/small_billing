import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def load_sales_data():
    try:
        return pd.read_csv("sales_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Product', 'Category', 'Sales', 'Quantity'])

def load_inventory_data():
    try:
        return pd.read_csv("inventory_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=['Product', 'Category', 'Quantity'])

def save_data(data, filename):
    data.to_csv(filename, index=False)

def main():
    st.title("Sales and Inventory Management")
    
    # Load existing sales and inventory data or create empty DataFrames
    sales_data = load_sales_data()
    inventory_data = load_inventory_data()
    
    # Display the sales data
    st.subheader("Sales Data")
    st.write(sales_data)
    
    # Display the inventory data
    st.subheader("Inventory Data")
    st.write(inventory_data)
    
    # Input fields for new sales data
    date = st.date_input("Date")
    products = st.text_area("Products (separate by comma)", "Product1, Product2")
    products = [p.strip() for p in products.split(",")]
    
    # If inventory data contains 'Category' column, suggest categories as well
    if 'Category' in inventory_data.columns:
        categories = st.text_area("Categories (separate by comma)", "Category1, Category2")
        categories = [c.strip() for c in categories.split(",")]
    else:
        categories = []
    
    sales = st.text_area("Sales (separate by comma)", "10.0, 20.0")
    sales = [float(s.strip()) for s in sales.split(",")]
    
    quantities = st.text_area("Quantities (separate by comma)", "1, 1")
    quantities = [int(q.strip()) for q in quantities.split(",")]
    
    # Button to add sales data
    if st.button("Add Sales Data"):
        if len(products) == len(categories) == len(sales) == len(quantities):
            new_sales = pd.DataFrame({'Date': [date]*len(products), 'Product': products, 'Category': categories, 'Sales': sales, 'Quantity': quantities})
            sales_data = pd.concat([sales_data, new_sales], ignore_index=True)
            st.success("Sales data added successfully!")
            
            # Subtract quantity from inventory
            for product, category, quantity_sold in zip(products, categories, quantities):
                if product in inventory_data['Product'].values and category in inventory_data['Category'].values:
                    index = (inventory_data['Product'] == product) & (inventory_data['Category'] == category)
                    current_quantity = inventory_data.loc[index, 'Quantity'].values[0]
                    if current_quantity >= quantity_sold:
                        inventory_data.loc[index, 'Quantity'] -= quantity_sold
                    else:
                        st.error(f"Insufficient quantity in inventory for product {product} in category {category}!")
                else:
                    st.error(f"Product {product} or category {category} not available in inventory!")
            
            save_data(sales_data, "sales_data.csv")
            save_data(inventory_data, "inventory_data.csv")
        else:
            st.error("Number of products, categories, sales, and quantities must be the same!")
    
    # Input fields for inventory data
    inventory_product = st.text_input("Inventory Product Name")
    inventory_category = st.text_input("Inventory Category", "")
    inventory_quantity = st.number_input("Inventory Quantity", value=0, step=1)
    
    # Button to add or update inventory data
    if st.button("Add or Update Inventory"):
        if inventory_product in inventory_data['Product'].values and inventory_category in inventory_data['Category'].values:
            index = (inventory_data['Product'] == inventory_product) & (inventory_data['Category'] == inventory_category)
            inventory_data.loc[index, 'Quantity'] = inventory_quantity
            st.success("Inventory quantity updated successfully!")
        else:
            new_inventory = pd.DataFrame({'Product': [inventory_product], 'Category': [inventory_category], 'Quantity': [inventory_quantity]})
            inventory_data = pd.concat([inventory_data, new_inventory], ignore_index=True)
            st.success("Inventory data added successfully!")
        save_data(inventory_data, "inventory_data.csv")
    
    # Check if any products are out of stock
    out_of_stock_products = inventory_data[inventory_data['Quantity'] == 0]['Product']
    if not out_of_stock_products.empty:
        st.warning(f"Product/s {', '.join(out_of_stock_products)} not in stock. Please restock!")

    if st.button("Generate Plot and Products DataFrame"):
        # Generate bar graph for sales vs products
        st.subheader("Sales vs Products")
        sales_by_product = sales_data.groupby('Product')['Sales'].sum().sort_values()
        plt.bar(sales_by_product.index, sales_by_product.values)
        plt.xlabel("Product")
        plt.ylabel("Sales")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(plt)
        
        # Create dataframe for products and total quantity
        st.subheader("Products, Total Sales, and Total Quantity")
        product_sales_quantity = sales_data.groupby('Product').agg({'Sales': 'sum', 'Quantity': 'sum'}).sort_values(by='Sales', ascending=False)
        st.write(product_sales_quantity)

if __name__ == "__main__":
    main()
