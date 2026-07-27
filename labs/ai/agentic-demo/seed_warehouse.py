"""Seeds a tiny local warehouse.duckdb standing in for Snowflake.

Creates a revenue_daily table with one deliberately injected anomaly
(a country/day with revenue collapsing to near-zero because of a currency
mapping bug) so the agents below have something real to catch.
"""
import duckdb

con = duckdb.connect("warehouse.duckdb")

con.execute("DROP TABLE IF EXISTS revenue_daily")
con.execute(
    """
    CREATE TABLE revenue_daily (
        report_date DATE,
        country VARCHAR,
        currency VARCHAR,
        revenue_usd DECIMAL(12, 2)
    )
    """
)

con.execute(
    """
    INSERT INTO revenue_daily VALUES
        ('2026-07-22', 'US', 'USD', 182340.50),
        ('2026-07-23', 'US', 'USD', 179880.12),
        ('2026-07-24', 'US', 'USD', 185120.77),
        ('2026-07-22', 'MX', 'MXN', 64210.00),
        ('2026-07-23', 'MX', 'MXN', 63875.40),
        ('2026-07-24', 'MX', 'MXN', 312.85),   -- anomaly: mxn_to_usd rate applied twice
        ('2026-07-22', 'BR', 'BRL', 41200.00),
        ('2026-07-23', 'BR', 'BRL', 40650.30),
        ('2026-07-24', 'BR', 'BRL', 42010.15)
    """
)

for row in con.execute("SELECT * FROM revenue_daily ORDER BY country, report_date").fetchall():
    print(row)
con.close()
print("\nSeeded warehouse.duckdb")
