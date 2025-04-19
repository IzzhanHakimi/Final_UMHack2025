import pandas as pd
import threading
import time
import os
from visualisation import prepare_data, real_time_sim
import streamlit as st
from filelock import FileLock
import openai

# --- Utility: Safe read with lock ---
def safe_read_csv(path, retries=3, delay=0.2):
    lock = FileLock(f"{path}.lock")
    for _ in range(retries):
        try:
            with lock:
                return pd.read_csv(path)
        except pd.errors.EmptyDataError:
            time.sleep(delay)
    return pd.DataFrame()

# --- Utility: Safe write with lock ---
def write_csv_with_lock(df, path):
    lock = FileLock(f"{path}.lock")
    with lock:
        df = df.drop_duplicates(subset=["order_id"])
        df.to_csv(path, index=False)
        #shutil.move(tmp_path, path)

# --- Streaming Logic for a Shop ---
def stream_rows_from_upcoming(shop_name):
    tr_data, _ = prepare_data(shop_name, 'Today')
    baseline, upcoming = real_time_sim(tr_data, pd.to_datetime('2023-06-17 08:00:00'))

    simulated_csv_path = f"simulated_stream_{shop_name}.csv"

    # Initialize baseline file only once
    if not os.path.exists(simulated_csv_path) or os.path.getsize(simulated_csv_path) == 0:
        write_csv_with_lock(baseline.copy(), simulated_csv_path)

    idx = 0
    while idx < len(upcoming):
        next_row = upcoming.iloc[[idx]]
        order_id = next_row.iloc[0]["order_id"]

        # 🔒 Always read the latest file version before writing
        current_data = safe_read_csv(simulated_csv_path)

        # ✅ Only append if order_id doesn't already exist
        if order_id not in current_data["order_id"].values:
            updated_data = pd.concat([current_data, next_row], ignore_index=True)
            write_csv_with_lock(updated_data, simulated_csv_path)

        idx += 1
        time.sleep(22.5)


# --- Start Thread Only Once Per Shop ---
def start_streaming_thread(shop_name):
    key = f"replay_thread_started_{shop_name}"
    if key not in st.session_state:
        stream_thread = threading.Thread(
            target=stream_rows_from_upcoming,
            args=(shop_name,),
            daemon=True
        )
        stream_thread.start()
        st.session_state[key] = True

#seq = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
seq = [1, 0, 1, 0]

shared_state = {
    "inv_status": None
}

# Define a function to read elements from the list every 5 seconds
def read_list(seq):
    for element in seq:
        shared_state["inv_status"] = element
        time.sleep(25.5)
        
def start_inv_sim(sequence):
    if not shared_state.get("thread_started", False):
        thread_inv = threading.Thread(
            target=read_list,
            args=(sequence,),
            daemon=True
        )
        thread_inv.start()
        shared_state["thread_started"] = True

def format_history_tuples(history_tuples):
    formatted = []
    for role, content, _, _ in history_tuples:
        if role == "You":
            role_id = "user"
        elif role == "Bot":
            role_id = "assistant"
        else:
            continue  # skip if unknown
        formatted.append({"role": role_id, "content": content})
    return formatted

def get_chat_summary(summary_prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=summary_prompt,
            temperature=0.7
        )
        print("OpenAI response received")
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "[SUMMARY FAILED]"

def summarize_old_history(old_messages, current_summary):
    if "summary_thread_run" not in st.session_state:
        st.session_state.summary_thread_run = True
    print('this is inside old_hist')
    print(f'old :{old_messages}')
    #old_messages = st.session_state.chat_hist_summary_pool  # skip system + last 3 turns

    if old_messages:
        summary_prompt = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Summarize the following conversation history into a concise memory format, "
                    "retaining important facts, goals, and user preferences. You are updating an existing memory summary."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Current memory summary:\n{current_summary}\n\n"
                    f"New conversation:\n" +
                    "\n".join([f"{msg['role']}: {msg['content']}" for msg in old_messages])
                )
            }
        ]


        print(f'summary_p: {summary_prompt}')

        try:
            print('test')
            updated_summary = get_chat_summary(summary_prompt)
            print(f'updated:{updated_summary}')
            st.session_state.memory_summary = updated_summary
            print(f'updated:{updated_summary}')
        except Exception as e:
            st.warning(f"Summarization failed: {e}")
    
    st.session_state.summary_thread_running = False

def start_summary_thread():
    old_messages = st.session_state.get("chat_hist_summary_pool", []).copy()
    current_summary = st.session_state.get("memory_summary", "")

    print(f'old_message:{old_messages}')
    print(f'summary:{current_summary}')

    old_messages = format_history_tuples(old_messages)
    print(f'olds: {old_messages}')
    st.session_state.chat_hist_summary_pool = []
    summarize_old_history(old_messages, current_summary)
