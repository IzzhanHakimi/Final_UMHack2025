import pandas as pd
import os
import streamlit as st
from filelock import FileLock

items = pd.read_csv("processed_csv/items_with_ingredients.csv")
transaction_items = pd.read_csv("crude_csv/transaction_items.csv")
transaction_items.drop(columns=["Unnamed: 0"],inplace=True)
merchant = pd.read_csv("crude_csv/merchant.csv")

def df_merger(merchant_name, tr_data, tr_items):
    merchant_row = merchant[merchant["merchant_name"] == merchant_name]
    if len(merchant_row) == 0:
        print("Merchant name does not exist")

    merchant_id = merchant_row.iloc[0]["merchant_id"]
    df_items = items[items["merchant_id"] == merchant_id]

    df_merged_transactions = pd.merge(tr_data, tr_items, on="order_id", how="inner")
    df_merged = pd.merge(df_merged_transactions, df_items, on="item_id", how="inner")
    df_merged.drop_duplicates(inplace=True)

    return df_merged

def merged_df(merchant_name, time, live=False, all=False):
    if live:
        path = f"simulated_stream_{merchant_name}.csv"
        lock = FileLock(f"{path}.lock")
        if not os.path.exists(path):
            st.warning(f"No real-time data yet for {merchant_name}")
            return pd.DataFrame()
        with lock:
            tr_data = pd.read_csv(path)

        tr_data["order_time"] = pd.to_datetime(tr_data["order_time"])
        if merchant_name == 'Bagel Bros':
            tr_items = pd.read_csv('processed_csv/transaction_bagel_items.csv')
        else:
            tr_items = pd.read_csv('processed_csv/transaction_noodle_items.csv')

        df_merged = df_merger(merchant_name, tr_data, tr_items)
        return df_merged

    # Static fallback (non-live)
    det = "" if all is False else "_all"

    if merchant_name == 'Bagel Bros':
        tr_data = pd.read_csv(f'processed_csv/transaction_bagel_data{det}.csv')
        tr_items = pd.read_csv('processed_csv/transaction_bagel_items.csv')
    else:
        tr_data = pd.read_csv(f'processed_csv/transaction_noodle_data{det}.csv')
        tr_items = pd.read_csv('processed_csv/transaction_noodle_items.csv')

    tr_data["order_time"] = pd.to_datetime(tr_data["order_time"])
    
    today = pd.to_datetime('2023-06-17')

    if time == 'Today':
        tr_data = tr_data[tr_data['order_time'].dt.date == today.date()]
    elif time == 'Yesterday':
        yesterday = today - pd.Timedelta(days=1)
        tr_data = tr_data[tr_data['order_time'].dt.date == yesterday.date()]
        print(f'yesterday: {tr_data}')
    elif time == 'This Week':
        start_of_week = today - pd.Timedelta(days=today.weekday())  # Monday
        tr_data = tr_data[tr_data['order_time'].dt.date >= start_of_week.date()]
    elif time == 'Last Week':
        start_of_week = today - pd.Timedelta(days=today.weekday())
        last_week_start = start_of_week - pd.Timedelta(weeks=1)
        last_week_end = start_of_week - pd.Timedelta(seconds=1)
        tr_data = tr_data[
            (tr_data['order_time'] >= last_week_start) &
            (tr_data['order_time'] <= last_week_end)
        ]
    elif time == 'This Month':
        start_of_month = today.replace(day=1)
        tr_data = tr_data[tr_data['order_time'] >= start_of_month]
    elif time == 'Last Month':
        start_of_this_month = today.replace(day=1)                       # 2023-06-01
        start_of_last_month = (start_of_this_month - pd.Timedelta(days=1)).replace(day=1)  # 2023-05-01
        end_of_last_month = start_of_this_month                         # 2023-06-01 (exclusive)


        # Filter the data safely using datetime comparisons
        tr_data = tr_data[
            (tr_data['order_time'] >= start_of_last_month) &
            (tr_data['order_time'] < end_of_last_month)
        ]


    # Optional: more ranges (e.g., last 7 days, etc.)

    df_merged = df_merger(merchant_name, tr_data, tr_items)
    return df_merged

def most_ordered_product(merchant_name, time):
    df_merged = merged_df(merchant_name, None, live=True)

    if time == 'This Week':
        df_week = merged_df(merchant_name, time)
        df = pd.concat([df_week, df_merged], ignore_index=True)
    elif time == "This Month":
        df_month = merged_df(merchant_name, time)
        df = pd.concat([df_month, df_merged], ignore_index=True)
    else:
        df = df_merged

    df_item_counts = df.groupby('item_name').size().reset_index(name = "Total orders")
    return df_item_counts

def order_per_hour(merchant_name, time):
    df_merged = merged_df(merchant_name, time)

    df_merged['order_hour'] = df_merged['order_time'].dt.hour
    df_order_per_hour = df_merged.groupby('order_hour').size().reset_index(name="Total orders")

    return df_order_per_hour

def order_per_date(merchant_name, time):
    df_merged = merged_df(merchant_name, None, live=True)

    df_merged['order_hour'] = df_merged['order_time'].dt.hour
    df_merged['order_date'] = df_merged['order_time'].dt.date

    df_order_per_date = df_merged.groupby(['order_date', 'order_hour']).size().reset_index(name="Total orders")
    df_order_per_date['hour_name'] = df_order_per_date['order_hour'].apply(lambda x: f"{x:02d}:00")

    if time == 'This Week':
        df_week = merged_df(merchant_name, time)
        df_week['order_hour'] = df_week['order_time'].dt.hour
        df_week['order_date'] = df_week['order_time'].dt.date

        df_order_week = df_week.groupby(['order_date', 'order_hour']).size().reset_index(name="Total orders")
        df_order_week['hour_name'] = df_order_week['order_hour'].apply(lambda x: f"{x:02d}:00")

        df_final = pd.concat([df_order_week, df_order_per_date], ignore_index=True)
    elif time == 'This Month':
        df_month = merged_df(merchant_name, time)        
        df_month['order_hour'] = df_month['order_time'].dt.hour
        df_month['order_date'] = df_month['order_time'].dt.date

        df_order_month = df_month.groupby(['order_date', 'order_hour']).size().reset_index(name="Total orders")
        df_order_month['hour_name'] = df_order_month['order_hour'].apply(lambda x: f"{x:02d}:00")

        df_final = pd.concat([df_order_month, df_order_per_date], ignore_index=True)
    else:
        df_final = df_order_per_date
    
    df_final['datetime'] = df_final['order_date'].astype(str) + " " + df_final['hour_name']
    
    return df_final

def revenue_per_date(merchant_name, time):
    df_merged = merged_df(merchant_name, None, live=True)

    df_merged['order_hour'] = df_merged['order_time'].dt.hour
    df_merged['order_date'] = df_merged['order_time'].dt.date

    df_revenue_per_date = df_merged.groupby(['order_date', 'order_hour'])['item_price'].sum().reset_index(name="Total Revenue (RM)")
    df_revenue_per_date['order_hour'] = df_revenue_per_date['order_hour'].apply(lambda x: f"{x:02d}:00")

    if time == 'This Week':
        df_week = merged_df(merchant_name, time)
        df_week['order_hour'] = df_week['order_time'].dt.hour
        df_week['order_date'] = df_week['order_time'].dt.date

        df_revenue_week = df_week.groupby(['order_date', 'order_hour'])['item_price'].sum().reset_index(name="Total Revenue (RM)")
        df_revenue_week['order_hour'] = df_revenue_week['order_hour'].apply(lambda x: f"{x:02d}:00")

        df_final = pd.concat([df_revenue_week, df_revenue_per_date], ignore_index=True)
    elif time == 'This Month':
        df_month = merged_df(merchant_name, time)        
        df_month['order_hour'] = df_month['order_time'].dt.hour
        df_month['order_date'] = df_month['order_time'].dt.date

        df_revenue_month = df_month.groupby(['order_date', 'order_hour'])['item_price'].sum().reset_index(name="Total Revenue (RM)")
        df_revenue_month['order_hour'] = df_revenue_month['order_hour'].apply(lambda x: f"{x:02d}:00")

        df_final = pd.concat([df_revenue_month, df_revenue_per_date], ignore_index=True)
    else:
        df_final = df_revenue_per_date
    
    df_final['datetime'] = df_final['order_date'].astype(str) + " " + df_final['order_hour']   

    return df_final

def orders_and_revenue_per_date(merchant_name, time):
    df_merged = merged_df(merchant_name, time)

    # Convert order_time to date
    df_merged['order_date'] = df_merged['order_time'].dt.date

    # Group by date to get total orders and total revenue
    df_summary = df_merged.groupby('order_date').agg(
        **{
            "Total orders": ("order_id", "nunique"),
            "Total Revenue (RM)": ("item_price", "sum")
        }
    ).reset_index()

    # Add day name
    df_summary['day_name'] = df_summary['order_date'].apply(lambda x: x.strftime('%A'))

    return df_summary

def total_revenue(merchant_name, time, live=False):
    df_merged = merged_df(merchant_name, live=live, time=time)
    if df_merged.empty:
        return 0, 0, 0

    base_rev = df_merged["item_price"].sum()

    if time == "Today":
        past_rev = 0
    elif time == 'This Week':
        df_merged_week = merged_df(merchant_name, time=time)
        past_rev = df_merged_week["item_price"].sum()
    elif time == 'This Month':
        df_merged_month = merged_df(merchant_name, time=time)
        past_rev = df_merged_month["item_price"].sum()
    elif time == 'Yesterday':
        df_past = merged_df(merchant_name, time="Yesterday")
        past_rev = df_past["item_price"].sum()
    elif time == 'Last Week':
        df_past = merged_df(merchant_name, time="Last Week")
        past_rev = df_past["item_price"].sum()
        _, base_rev, _ = total_revenue(merchant_name, live=True, time='This Week')
    else:
        df_past = merged_df(merchant_name, time="Last Month", all=True)
        past_rev = df_past["item_price"].sum()
        _, base_rev, _ = total_revenue(merchant_name, live=True, time='This Month')
        
    return base_rev, base_rev + past_rev, base_rev - past_rev

def total_orders(merchant_name, time, live=False) :
    df_merged = merged_df(merchant_name, live=live, time=time)
    if df_merged.empty:
        return 0, 0, 0

    base_orders = df_merged["order_id"].size

    if time == "Today":
        past_orders = 0
    elif time == 'This Week':
        df_merged_week = merged_df(merchant_name, time=time)
        past_orders = df_merged_week["order_id"].size
    elif time == 'This Month':
        df_merged_month = merged_df(merchant_name, time=time)
        past_orders = df_merged_month["order_id"].size
    elif time == 'Yesterday':
        df_past = merged_df(merchant_name, time="Yesterday")
        past_orders = df_past["order_id"].size
    elif time == 'Last Week':
        df_past = merged_df(merchant_name, time="Last Week")
        past_orders = df_past["order_id"].size
        _, base_orders, _ = total_orders(merchant_name, 'This Week', live=True)  
    else:
        df_past = merged_df(merchant_name, time="Last Month", all=True)
        past_orders = df_past["order_id"].size
        _, base_orders, _ = total_orders(merchant_name, 'This Month', live=True)  
        
    return base_orders, base_orders + past_orders, base_orders - past_orders

def average_driver_waiting_time(merchant_name, time):
    df_merged = merged_df(merchant_name, time)

    df_merged['order_hour'] = df_merged['order_time'].dt.hour
    df_avg_waiting =  df_merged.groupby('order_hour')['driver_waiting_time'].mean().reset_index(name="Driver Waiting Time (minutes)")

    return df_avg_waiting

def average_meal_ready_time(merchant_name, time):
    df_merged = merged_df(merchant_name, time)

    df_merged['order_hour'] = df_merged['order_time'].dt.hour
    df_avg_ready =  df_merged.groupby('order_ready')['driver_waiting_time'].mean().reset_index(name="Time to prepare order (minutes)")

    return df_avg_ready

def avg_wait_and_ready_time(merchant_name):
    df_merged = merged_df(merchant_name, None, live=True)

    # Create hour column for grouping
    df_merged["order_time"] = pd.to_datetime(df_merged['order_time']).dt.hour

    last_hour = df_merged['order_time'].tail(1).values[0]
    hour = last_hour - 1 if last_hour != 22 else last_hour

    idx = df_merged[df_merged['order_time'] == hour].index.min()
    driver_wait = df_merged['driver_waiting_time'].iloc[:idx+1].mean()
    order_prep = df_merged['order_ready'].iloc[:idx+1].mean()

    return driver_wait, order_prep
