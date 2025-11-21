import streamlit as st
import pandas as pd
import plotly.express as px
import random
import time

# =====================================================
#                Algorithm Implementations
# =====================================================

def greedy_allocation(total_bandwidth, demands):
    allocation = []
    remaining = total_bandwidth
    for d in sorted(demands, reverse=True):
        alloc = min(d, remaining)
        allocation.append(alloc)
        remaining -= alloc
        if remaining <= 0:
            break
    return allocation, total_bandwidth - remaining


def random_allocation(total_bandwidth, demands):
    allocation = []
    remaining = total_bandwidth
    for _ in demands:
        alloc = random.randint(0, remaining if remaining > 0 else 0)
        allocation.append(alloc)
        remaining -= alloc
        if remaining <= 0:
            break
    return allocation, total_bandwidth - remaining


def dynamic_allocation(total_bandwidth, demands):
    n = len(demands)
    dp = [[0]*(total_bandwidth+1) for _ in range(n+1)]

    for i in range(1, n+1):
        for w in range(1, total_bandwidth+1):
            if demands[i-1] <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-demands[i-1]] + demands[i-1])
            else:
                dp[i][w] = dp[i-1][w]

    result = dp[n][total_bandwidth]
    w = total_bandwidth
    allocation = []
    for i in range(n, 0, -1):
        if result <= 0:
            break
        if result == dp[i-1][w]:
            continue
        else:
            allocation.append(demands[i-1])
            result -= demands[i-1]
            w -= demands[i-1]

    return allocation, sum(allocation)


def backtracking_allocation(total_bandwidth, demands):
    best_sum = 0
    best_alloc = []

    def backtrack(i, current, total):
        nonlocal best_sum, best_alloc
        if total > total_bandwidth:
            return
        if total > best_sum:
            best_sum = total
            best_alloc = current[:]
        if i == len(demands):
            return
        # include
        backtrack(i+1, current+[demands[i]], total+demands[i])
        # exclude
        backtrack(i+1, current, total)

    backtrack(0, [], 0)
    return best_alloc, best_sum


def auto_select(total_bandwidth, demands):
    results = {
        "Greedy": greedy_allocation(total_bandwidth, demands)[1],
        "Dynamic Programming": dynamic_allocation(total_bandwidth, demands)[1],
        "Backtracking": backtracking_allocation(total_bandwidth, demands)[1],
        "Random": random_allocation(total_bandwidth, demands)[1],
    }
    best_algo = max(results, key=results.get)
    return best_algo, results[best_algo], results


# =====================================================
#                      UI Design
# =====================================================

st.set_page_config(page_title="Bandwidth Optimizer", layout="wide", page_icon="📶")

# ---------- Custom CSS styling ----------
st.markdown("""
<style>
/* Background gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    background-attachment: fixed;
    color: white;
    font-family: 'Poppins', sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: rgba(0, 0, 0, 0.6);
}

/* Header styling */
h1 {
    color: #00BFFF;
    text-align: center;
    font-weight: bold;
    font-size: 2.5em !important;
}

/* Buttons */
div.stButton > button {
    background-color: #00BFFF;
    color: white;
    border-radius: 12px;
    font-weight: 600;
    font-size: 16px;
    border: none;
    transition: 0.3s;
}
div.stButton > button:hover {
    background-color: #009ACD;
    transform: scale(1.05);
}

/* Table styling */
thead tr th {
    background-color: #00BFFF;
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------- App Header ----------
st.markdown("<h1>📶 Bandwidth Allocation Optimizer</h1>", unsafe_allow_html=True)
st.write("### Efficiently allocate available bandwidth among user demands using multiple algorithms.")

# ---------- Inputs ----------
col1, col2 = st.columns(2)
with col1:
    total_bandwidth = st.slider("Total Bandwidth (MBps)", 10, 1000, 200, 10)
with col2:
    demand_text = st.text_input("Enter Demands (comma-separated)", "50,40,30,60,20")

algo_choice = st.selectbox(
    "Choose Algorithm",
    ["Auto", "Greedy", "Dynamic Programming", "Backtracking", "Random"]
)

# ---------- Run Button ----------
if st.button("🚀 Run Optimizer"):
    demands = [int(x.strip()) for x in demand_text.split(',') if x.strip().isdigit()]
    if not demands:
        st.error("Please enter valid demand values (e.g. 30,40,50)")
    else:
        with st.spinner("Optimizing bandwidth allocation..."):
            time.sleep(1)  # smooth spinner animation

            # Run selected algorithm
            if algo_choice == "Auto":
                best_algo, best_val, results = auto_select(total_bandwidth, demands)
                st.success(f"✅ Auto selected best algorithm: **{best_algo}** ({best_val}/{total_bandwidth} MBps)")
            elif algo_choice == "Greedy":
                alloc, val = greedy_allocation(total_bandwidth, demands)
                results = {"Greedy": val}
                best_algo, best_val = "Greedy", val
            elif algo_choice == "Dynamic Programming":
                alloc, val = dynamic_allocation(total_bandwidth, demands)
                results = {"Dynamic Programming": val}
                best_algo, best_val = "Dynamic Programming", val
            elif algo_choice == "Backtracking":
                alloc, val = backtracking_allocation(total_bandwidth, demands)
                results = {"Backtracking": val}
                best_algo, best_val = "Backtracking", val
            else:
                alloc, val = random_allocation(total_bandwidth, demands)
                results = {"Random": val}
                best_algo, best_val = "Random", val

        # ---------- Visualization ----------
        st.markdown(f"### 📈 Results for **{best_algo}**")
        st.write(f"**Total Bandwidth Used:** {best_val} / {total_bandwidth} MBps")

        df = pd.DataFrame({
            "Algorithm": list(results.keys()),
            "Bandwidth Used": list(results.values())
        })

        chart = px.bar(
            df, x="Algorithm", y="Bandwidth Used",
            color="Algorithm", text="Bandwidth Used",
            title="Algorithm Comparison",
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        chart.update_layout(
            template="plotly_dark",
            title_font=dict(size=24, color='cyan'),
            font=dict(size=14, color='white'),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=60, b=20),
        )

        chart.update_traces(
            textfont_size=16,
            textposition="outside",
            marker=dict(line=dict(width=1, color='white')),
            hovertemplate='Algorithm: %{x}<br>Used: %{y} MBps'
        )

        st.plotly_chart(chart, use_container_width=True)

        # ---------- Allocation Breakdown ----------
        if algo_choice != "Auto":
            st.subheader("📊 Allocation Breakdown")
            alloc_table = pd.DataFrame({
                "User": [f"User {i+1}" for i in range(len(alloc))],
                "Allocated Bandwidth": alloc
            })
            st.dataframe(alloc_table, use_container_width=True)

# ---------- Footer ----------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:lightgray;'>Made with 💙 by Shivam Shaunik</p>",
    unsafe_allow_html=True
)
