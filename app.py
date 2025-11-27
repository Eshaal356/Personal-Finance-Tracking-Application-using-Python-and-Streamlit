import streamlit as st
import pandas as pd
import altair as alt
from finance_core import (
    Income, Expense, Investment, 
    save_transaction, load_transactions, 
    calculate_totals, get_insights, string_analysis
)
from datetime import date

# --- Page Configuration ---
st.set_page_config(
    page_title="FinTrack | Personal Finance",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Feel ---
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Custom Card Styling for Metrics */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #2c3e50;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #2c3e50;
        color: white;
    }
    
    /* Button styling */
    div.stButton > button {
        background-color: #2ecc71;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #27ae60;
        border-color: #27ae60;
    }
    
    /* Alert/Success messages */
    .stAlert {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Header Section ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2382/2382461.png", width=80) # Placeholder icon
with col2:
    st.title("FinTrack")
    st.markdown("### *Your Personal Financial Command Center*")

st.markdown("---")

# --- Sidebar: Transaction Input ---
st.sidebar.title("📝 New Transaction")
st.sidebar.markdown("Record your financial moves below.")

with st.sidebar.form("transaction_form", clear_on_submit=True):
    t_type = st.selectbox("Type", ["Income", "Expense", "Investment"])
    t_date = st.date_input("Date", date.today())
    t_amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f", step=10.0)
    t_category = st.text_input("Category", placeholder="e.g., Groceries, Salary, Crypto")
    t_note = st.text_area("Note", placeholder="Optional details...")
    
    submitted = st.form_submit_button("Add Transaction")
    
    if submitted:
        if t_amount > 0 and t_category:
            if t_type == "Income":
                transaction = Income(str(t_date), t_amount, t_category, t_note)
            elif t_type == "Expense":
                transaction = Expense(str(t_date), t_amount, t_category, t_note)
            elif t_type == "Investment":
                transaction = Investment(str(t_date), t_amount, t_category, t_note)
            
            save_transaction(transaction)
            st.sidebar.success("✅ Transaction Added Successfully!")
        else:
            st.sidebar.error("⚠️ Please enter a valid amount and category.")

# --- Load Data ---
transactions = load_transactions()

if not transactions:
    st.container().markdown("""
        <div style="text-align: center; padding: 50px;">
            <h2>👋 Welcome to FinTrack!</h2>
            <p>It looks like you don't have any transactions yet.</p>
            <p>Use the sidebar to add your first income, expense, or investment.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # 1. Financial Overview (Cards)
    totals = calculate_totals(transactions)
    
    st.subheader("📊 Financial Overview")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Income", f"${totals['Total Income']:,.2f}", delta="Income")
    m2.metric("Total Expenses", f"${totals['Total Expense']:,.2f}", delta="-Expense", delta_color="inverse")
    m3.metric("Investments", f"${totals['Total Investment']:,.2f}", delta="Asset")
    m4.metric("Net Balance", f"${totals['Net Balance']:,.2f}", delta_color="normal")
    
    st.markdown("---")

    # 2. Analytics & Visualization Split
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📉 Financial Analytics")
        
        # Prepare data for charts
        insights = get_insights(transactions)
        expense_data = {k: v for k, v in insights['category_totals'].items() if k in [t.category for t in transactions if isinstance(t, Expense)]}
        df_trend = pd.DataFrame([t.to_dict() for t in transactions])
        
        tab1, tab2, tab3 = st.tabs(["Spending by Category", "Income vs Expense Trend", "Expense Breakdown"])
        
        with tab1:
            # Bar Chart: Spending by Category
            if expense_data:
                chart_data = pd.DataFrame(list(expense_data.items()), columns=["Category", "Amount"])
                c_bar = alt.Chart(chart_data).mark_bar(cornerRadius=5).encode(
                    x=alt.X('Category', sort='-y', axis=alt.Axis(labelAngle=-45)),
                    y='Amount',
                    color=alt.Color('Category', legend=None, scale=alt.Scale(scheme='viridis')),
                    tooltip=['Category', 'Amount']
                ).properties(height=350)
                st.altair_chart(c_bar, use_container_width=True)
            else:
                st.info("No expenses to show.")
                
        with tab2:
            # Line Chart: Income vs Expense Over Time
            if not df_trend.empty:
                try:
                    df_trend['Date'] = pd.to_datetime(df_trend['Date'])
                    trend_chart = alt.Chart(df_trend).mark_line(point=True).encode(
                        x='Date',
                        y='Amount',
                        color='Type',
                        tooltip=['Date', 'Type', 'Amount', 'Category']
                    ).properties(height=350).interactive()
                    st.altair_chart(trend_chart, use_container_width=True)
                except Exception as e:
                    st.error(f"Error plotting trend: {e}")
            else:
                st.info("No data for trends.")

        with tab3:
            # Donut Chart: Expense Breakdown
            if expense_data:
                chart_data = pd.DataFrame(list(expense_data.items()), columns=["Category", "Amount"])
                base = alt.Chart(chart_data).encode(
                    theta=alt.Theta("Amount", stack=True)
                )
                pie = base.mark_arc(outerRadius=120, innerRadius=80).encode(
                    color=alt.Color("Category", scale=alt.Scale(scheme='spectral')),
                    order=alt.Order("Amount", sort="descending"),
                    tooltip=["Category", "Amount"]
                )
                text = base.mark_text(radius=140).encode(
                    text="Category",
                    order=alt.Order("Amount", sort="descending"),
                    color=alt.value("black")  
                )
                st.altair_chart(pie + text, use_container_width=True)
            else:
                st.info("No expenses to show.")

    with c2:
        st.subheader("🎯 Goals & Insights")
        
        # Goal Section
        goal_percentage = st.slider("Monthly Savings Goal (%)", 0, 100, 20)
        actual_savings = totals['Savings Percentage']
        
        st.write(f"**Current Savings Rate:** {actual_savings:.1f}%")
        st.progress(min(actual_savings / 100, 1.0))
        
        if actual_savings >= goal_percentage:
            st.success(f"🎉 Goal Met! ({goal_percentage}%)")
        else:
            if actual_savings > 0:
                st.warning(f"⚠️ {goal_percentage - actual_savings:.1f}% to go!")
            else:
                st.error("🚨 Negative or Zero Savings")

        # Savings Projection Algorithm
        if actual_savings > 0:
            monthly_income = totals['Total Income']
            projected_savings_year = (monthly_income * (actual_savings / 100)) * 12
            st.markdown(f"""
                <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    <strong>🔮 Savings Projection:</strong><br>
                    At this rate, you could save <strong>${projected_savings_year:,.2f}</strong> in a year!
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🧠 Smart Insights")
        st.info(f"**Top Spend:** {insights['highest_spending_category']}")
        st.info(f"**Most Frequent:** {insights['most_frequent_category']}")
        
        # Unique Categories (Requirement)
        with st.expander("📂 Unique Categories"):
            st.write(", ".join(insights['unique_categories']))

    st.markdown("---")

    # 3. Recent Transactions & String Analysis
    r1, r2 = st.columns([3, 2])
    
    with r1:
        st.subheader("📝 Recent Transactions")
        df = pd.DataFrame([t.to_dict() for t in transactions])
        # Reorder columns
        df = df[["Date", "Type", "Category", "Amount", "Note"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    with r2:
        st.subheader("🔤 String Analysis")
        categories_list = [t.category for t in transactions]
        upper_str, count_a = string_analysis(categories_list)
        
        with st.expander("View Analysis Details", expanded=True):
            st.write("**Joined Categories:**")
            st.caption(upper_str)
            st.metric("Count of 'A'", count_a)

# --- Footer ---
st.markdown("""
    <div style="text-align: center; margin-top: 50px; color: #888;">
        <small>Built with ❤️ using Streamlit | FinTrack v1.0</small>
    </div>
""", unsafe_allow_html=True)


