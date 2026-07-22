# Retail Data Pipeline

An end-to-end ETL pipeline that transforms raw retail transaction data into an analytical PostgreSQL data warehouse using Python and SQL.

## Project Overview

This project processes raw retail data through a complete ETL workflow:
- Cleaning and validating raw CSV data using Python and Pandas
- Loading transformed data into PostgreSQL
- Organizing data using a star schema design
- Performing SQL analysis using joins, CTEs, and window functions

## Project Structure
# Data Pipeline

**1. Cleaning & Transformation**
- Standardized dates, handled missing values, removed duplicates, and validated order totals.
- Transformed shopping cart data into product-level records.

**2. Database Loading**
- Created a PostgreSQL star schema with four dimension tables:
  - Customer
  - Product
  - Warehouse
  - Date
- Loaded two fact tables:
  - Orders
  - Order Items

**3. Analysis**
Created SQL queries to analyze:
- Customer revenue ranking
- Product performance by warehouse
- Monthly revenue trends
- Running revenue totals

## Technologies

Python | Pandas | PostgreSQL | SQL | Git
