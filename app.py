from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Configure Google Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(messages):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(messages)
    return response.text

def clean_sql_query(sql):
    sql = sql.strip()
    if sql.startswith("```"):
        sql = sql[3:].strip()
    if sql.endswith("```"):
        sql = sql[:-3].strip()
    if sql.lower().startswith("sql"):
        sql = sql[3:].strip()
    return sql

def run_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    except Exception as e:
        return f"SQL Error: {e}"

# ✅ UPDATED: Accurate table and column names from northwind.db
sql_generation_prompt = """
You are an expert in translating natural language into SQL queries.

The database is called northwind.db and contains these tables and relevant columns:

- Categories(CategoryID, CategoryName, Description)
- Customers(CustomerID, CompanyName, ContactName, Country)
- Employees(EmployeeID, FirstName, LastName, Title, ReportsTo)
- Suppliers(SupplierID, CompanyName, Country)
- Products(ProductID, ProductName, SupplierID, CategoryID, UnitPrice, Discontinued)
- Orders(OrderID, CustomerID, EmployeeID, OrderDate, ShipCountry)
- OrderDetails(OrderID, ProductID, UnitPrice, Quantity, Discount)
- Shippers(ShipperID, CompanyName)
- Region(RegionID, RegionDescription)
- Territories(TerritoryID, TerritoryDescription, RegionID)
- EmployeeTerritories(EmployeeID, TerritoryID)

Examples:
- List all products
  → SELECT * FROM Products;

- Show customers from Germany
  → SELECT * FROM Customers WHERE Country='Germany';

- Count employees who report to someone
  → SELECT COUNT(*) FROM Employees WHERE ReportsTo IS NOT NULL;

Output only the SQL query — no explanations or markdown.
"""

def agentic_ai_response(user_question, db="northwind.db"):
    raw_sql = get_gemini_response([sql_generation_prompt, user_question])
    sql_query = clean_sql_query(raw_sql)

    results = run_sql_query(sql_query, db)

    if isinstance(results, str) and results.startswith("SQL Error"):
        return sql_query, [], results

    summary_prompt = f"""
Given the SQL query result below (as a list of tuples):
{results}

Please answer the question in natural language:
{user_question}
"""
    final_answer = get_gemini_response([summary_prompt])
    return sql_query, results, final_answer

# Streamlit UI
st.set_page_config(page_title="Northwind Agentic AI SQL Assistant")
st.title("Agentic AI: Natural Language to SQL on Northwind DB")

user_question = st.text_input("Ask a question about the Northwind database:")

if st.button("Ask"):
    if user_question.strip() == "":
        st.error("Please enter a valid question.")
    else:
        with st.spinner("Generating SQL and fetching answer..."):
            sql_query, results, answer = agentic_ai_response(user_question)

            st.markdown("### 🧾 Generated SQL Query")
            st.code(sql_query, language="sql")

            st.markdown("### 📊 Raw SQL Results")
            if not results:
                st.warning("No results found or table/column name may be incorrect.")
            elif isinstance(results, str) and results.startswith("SQL Error"):
                st.error(results)
            else:
                for row in results:
                    st.write(row)

            st.markdown("### 💡 Agentic AI's Natural Language Answer")
            st.write(answer)
