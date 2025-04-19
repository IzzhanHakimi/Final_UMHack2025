import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

def prepare_data(shop, time):
    if shop == 'Bagel Bros':
        tr_data = pd.read_csv('processed_csv/transaction_bagel_data.csv')
        tr_items = pd.read_csv('processed_csv/transaction_bagel_items.csv')
    else:
        tr_data = pd.read_csv('processed_csv/transaction_noodle_data.csv')
        tr_items = pd.read_csv('processed_csv/transaction_noodle_items.csv')

    tr_data['order_time'] = pd.to_datetime(tr_data['order_time'])
    tr_data['driver_arrival_time'] = pd.to_datetime(tr_data['driver_arrival_time'])
    tr_data['driver_pickup_time'] = pd.to_datetime(tr_data['driver_pickup_time'])
    tr_data['delivery_time'] = pd.to_datetime(tr_data['delivery_time'])

    if time == 'Today':
        tr_data = tr_data[tr_data['order_time'] > pd.to_datetime('2023-06-17')]
    elif time == 'This Week':
        tr_data = tr_data[(tr_data['order_time'] >= pd.to_datetime('2023-06-11')) & (tr_data['order_time'] <= pd.to_datetime('2023-06-16'))]
    else:
        tr_data = tr_data[tr_data['order_time'] < pd.to_datetime('2023-06-17')]

    return tr_data, tr_items

def real_time_sim(tr_data, current):
    # Split data
    baseline = tr_data[tr_data['order_time'] <= current]
    upcoming = tr_data[tr_data['order_time'] > current]

    return baseline, upcoming  # return data left to stream

def sales_trend(revenue_record, time):
    sns.set(style="whitegrid")
    plt.figure(figsize=(5, 1))
    plt.grid(False)
    sns.lineplot(data=revenue_record, x="datetime", y="Total Revenue (RM)")

    ax = plt.gca()
    ax.set_xticklabels([])
    ax.set_ylabel('Total Rev')
    ax.set_xlabel(f'Revenue Trend of {time}')

    return plt

def orders_trend(revenue_record, time):
    sns.set(style="whitegrid")
    plt.figure(figsize=(5, 1))
    plt.grid(False)
    sns.lineplot(data=revenue_record, x="datetime", y="Total orders")

    ax = plt.gca()
    ax.set_xticklabels([])
    ax.set_xlabel(f'Orders Trend of {time}')

    return plt

def best_product(record, time):
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(7, 7))
    
    # Generate a green color palette based on number of items
    cmap = plt.cm.Greens
    colors = cmap(np.linspace(0.4, 0.8, len(record)))
    
    # Draw donut chart
    wedges, texts, autotexts = ax.pie(
        record['Total orders'].values,
        labels=record['item_name'].values,
        autopct='%1.1f%%',
        startangle=140,
        wedgeprops={'width': 0.4},
        colors=colors
    )
    
    # Ensure it’s a perfect circle
    ax.axis('equal')
    
    # Style the xlabel in a dark green
    ax.set_xlabel(f'Favorite Products of {time}', color='darkgreen')
    
    return fig

def predictions_graph(date_str, csv):
    # 1) Load and normalize dates
    csv_path = f"goal_{csv}.csv"
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    
    # 2) Locate the first matching row
    matches = df.index[df["Date"] == date_str].tolist()
    if not matches:
        raise ValueError(f"No data for date {date_str}")
    start_idx = matches[0]
    
    # 3) Slice out this row + next 6 rows (total 7)
    df_week = df.iloc[start_idx : start_idx + 7]
    
    # 4) Plot with custom bar color
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(
        df_week["Date"],
        df_week["Goal"],
        color="#08543c"           # <-- your custom green
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Predicted Order")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    st.pyplot(plt)