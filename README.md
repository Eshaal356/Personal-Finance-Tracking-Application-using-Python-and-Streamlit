# Personal Finance Tracking Application

A Python-based personal finance tracker built with **Streamlit**. This application allows users to record income, expenses, and investments, providing meaningful insights and visualizations to help manage personal finances.

## Features
- **Premium UI**: Clean, modern interface with custom styling, cards, and interactive charts.
- **Transaction Recording**: Add Income, Expense, and Investment records.
- **Data Persistence**: Transactions are saved to `transactions.csv` and reloaded on restart.
- **Financial Summary**: View Total Income, Expenses, Investments, Net Balance, and Savings Percentage.
- **Goal Evaluation**: Set a monthly savings goal and see if you are on track.
- **Analytics**: Identify highest spending categories and most frequent transaction types.
- **Visualization**: Advanced interactive charts including:
    - **Spending by Category** (Bar Chart)
    - **Income vs Expense Trend** (Line Chart)
    - **Expense Breakdown** (Donut Chart)
- **Smart Insights**:
    - **Savings Projection**: Estimates yearly savings based on current rate.
    - **Unique Categories**: Lists all categories used.
    - **Top Spend & Frequency**: Identifies spending habits.
- **String Analysis**: Fun analysis of category names (uppercase conversion, character counting).

## Installation & Running
1.  Ensure you have Python installed.
2.  Install the required packages:
    ```bash
    pip install streamlit pandas
    ```
3.  Run the application:
    ```bash
    streamlit run app.py
    ```

## Project Structure
- `app.py`: Main Streamlit application file.
- `finance_core.py`: Core logic and classes (OOP structure).
- `transactions.csv`: Data storage file (generated automatically).
- `test_core.py`: Unit tests for the core logic.

## Screenshot
