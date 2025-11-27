import csv
import os
from datetime import datetime
from typing import List, Dict, Type

DATA_FILE = "transactions.csv"

class Transaction:
    def __init__(self, date: str, amount: float, category: str, note: str = ""):
        self.date = date
        self.amount = amount
        self.category = category
        self.note = note

    def to_dict(self):
        return {
            "Date": self.date,
            "Type": self.__class__.__name__,
            "Amount": self.amount,
            "Category": self.category,
            "Note": self.note
        }

class Income(Transaction):
    pass

class Expense(Transaction):
    pass

class Investment(Transaction):
    pass

def save_transaction(transaction: Transaction):
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ["Date", "Type", "Amount", "Category", "Note"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(transaction.to_dict())

def load_transactions() -> List[Transaction]:
    transactions = []
    if not os.path.isfile(DATA_FILE):
        return transactions

    with open(DATA_FILE, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        # Strip whitespace from fieldnames if they exist
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            
        for row in reader:
            # Skip empty rows or rows with missing keys
            if not row or "Type" not in row:
                continue
                
            t_type = row.get("Type")
            date = row.get("Date")
            amount_str = row.get("Amount")
            category = row.get("Category")
            note = row.get("Note", "")
            
            if not t_type or not amount_str:
                continue
                
            try:
                amount = float(amount_str)
            except ValueError:
                continue
            
            if t_type == "Income":
                transactions.append(Income(date, amount, category, note))
            elif t_type == "Expense":
                transactions.append(Expense(date, amount, category, note))
            elif t_type == "Investment":
                transactions.append(Investment(date, amount, category, note))
    return transactions

def calculate_totals(transactions: List[Transaction]) -> Dict[str, float]:
    totals = {
        "Total Income": 0.0,
        "Total Expense": 0.0,
        "Total Investment": 0.0,
        "Net Balance": 0.0,
        "Savings Percentage": 0.0
    }
    
    for t in transactions:
        if isinstance(t, Income):
            totals["Total Income"] += t.amount
        elif isinstance(t, Expense):
            totals["Total Expense"] += t.amount
        elif isinstance(t, Investment):
            totals["Total Investment"] += t.amount
            
    totals["Net Balance"] = totals["Total Income"] - totals["Total Expense"] - totals["Total Investment"]
    
    if totals["Total Income"] > 0:
        # Assuming Savings = Income - Expense (Investment is a form of saving/asset, but usually treated separately or as saving. 
        # Let's define Savings for percentage as (Income - Expense) / Income * 100 or (Investment + Net Balance) / Income?
        # The prompt asks for "Savings percentage". Usually Savings = Income - Expenses. 
        # If Investment is considered an outflow from "cash" but an asset, it's tricky.
        # Let's treat Savings = Total Income - Total Expense. Investment is part of savings allocation.
        savings = totals["Total Income"] - totals["Total Expense"]
        totals["Savings Percentage"] = (savings / totals["Total Income"]) * 100
    else:
        totals["Savings Percentage"] = 0.0
        
    return totals

def get_insights(transactions: List[Transaction]):
    if not transactions:
        return None
        
    categories = [t.category for t in transactions]
    unique_categories = set(categories)
    
    # Category-wise totals
    category_totals = {}
    for t in transactions:
        if t.category in category_totals:
            category_totals[t.category] += t.amount
        else:
            category_totals[t.category] = t.amount
            
    # Highest spending category (considering only Expenses for "spending")
    expense_categories = {}
    for t in transactions:
        if isinstance(t, Expense):
            if t.category in expense_categories:
                expense_categories[t.category] += t.amount
            else:
                expense_categories[t.category] = t.amount
    
    highest_spending_category = max(expense_categories, key=expense_categories.get) if expense_categories else "N/A"
    
    # Most frequent category
    most_frequent_category = max(set(categories), key=categories.count) if categories else "N/A"
    
    return {
        "unique_categories": unique_categories,
        "category_totals": category_totals,
        "highest_spending_category": highest_spending_category,
        "most_frequent_category": most_frequent_category
    }

def string_analysis(categories: List[str]):
    if not categories:
        return "No categories available.", 0
        
    joined_string = ", ".join(categories)
    upper_string = joined_string.upper()
    count_a = upper_string.count("A")
    
    return upper_string, count_a
