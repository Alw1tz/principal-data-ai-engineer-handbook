"""A small, real QA/reconciliation agent — the pattern behind your SODA
data quality framework at Rappi, rebuilt in miniature.

No framework, no multi-agent graph. Five steps, top to bottom:

    1. connect to Snowflake
    2. seed two small tables with a realistic ETL discrepancy
    3. run reconciliation rules (plain SQL — this is exactly what SODA does)
    4. ask a local LLM to turn the raw findings into a QA report
    5. upload the report to S3

Run: uv run qa_agent.py
"""
import os

import boto3
import snowflake.connector
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

S3_BUCKET = "carlos-agentic-qa-practice"
llm = ChatOllama(model="qwen3:30b-64k", temperature=0)


def connect():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    )


def seed_tables(con) -> None:
    """SOURCE_ORDERS = the upstream extract. TARGET_ORDERS = what actually
    landed after the ETL run. Three deliberate discrepancies, the same
    three kinds a real reconciliation job checks for."""
    cur = con.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS AGENTIC_QA_PRACTICE")
    cur.execute("CREATE SCHEMA IF NOT EXISTS AGENTIC_QA_PRACTICE.QA_DEMO")
    cur.execute("USE SCHEMA AGENTIC_QA_PRACTICE.QA_DEMO")

    cur.execute("CREATE OR REPLACE TABLE SOURCE_ORDERS (order_id INT, amount_usd DECIMAL(10,2))")
    cur.execute("CREATE OR REPLACE TABLE TARGET_ORDERS (order_id INT, amount_usd DECIMAL(10,2))")

    cur.execute("""
        INSERT INTO SOURCE_ORDERS VALUES
            (1001, 250.00), (1002, 89.50), (1003, 412.10),
            (1004, 15.00), (1005, 630.75)
    """)
    cur.execute("""
        INSERT INTO TARGET_ORDERS VALUES
            (1001, 250.00),
            (1002, 89.50),
            (1003, 41.21),   -- decimal-shift bug: 412.10 landed as 41.21
            (1005, 630.75),  -- 1004 never landed at all
            (1005, 630.75)   -- and 1005 landed twice
    """)
    con.commit()


def run_checks(con) -> list[dict]:
    """Plain SQL reconciliation rules — this is the actual QA work.
    The LLM step later doesn't replace this, it explains it."""
    cur = con.cursor()
    findings = []

    cur.execute("SELECT COUNT(*) FROM SOURCE_ORDERS")
    source_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM TARGET_ORDERS")
    target_count = cur.fetchone()[0]
    findings.append({
        "rule": "row_count_match",
        "detail": f"source={source_count} rows, target={target_count} rows",
        "passed": source_count == target_count,
    })

    cur.execute("""
        SELECT s.order_id FROM SOURCE_ORDERS s
        LEFT JOIN TARGET_ORDERS t ON s.order_id = t.order_id
        WHERE t.order_id IS NULL
    """)
    missing = [r[0] for r in cur.fetchall()]
    findings.append({
        "rule": "no_missing_orders",
        "detail": f"order_ids in source but never landed in target: {missing}",
        "passed": len(missing) == 0,
    })

    cur.execute("""
        SELECT order_id, COUNT(*) c FROM TARGET_ORDERS
        GROUP BY order_id HAVING COUNT(*) > 1
    """)
    dupes = cur.fetchall()
    findings.append({
        "rule": "no_duplicate_order_ids",
        "detail": f"order_ids appearing more than once in target: {dupes}",
        "passed": len(dupes) == 0,
    })

    cur.execute("""
        SELECT s.order_id, s.amount_usd, t.amount_usd
        FROM SOURCE_ORDERS s JOIN TARGET_ORDERS t ON s.order_id = t.order_id
        WHERE s.amount_usd != t.amount_usd
    """)
    mismatches = cur.fetchall()
    findings.append({
        "rule": "amounts_match",
        "detail": f"(order_id, source_amount, target_amount) mismatches: {mismatches}",
        "passed": len(mismatches) == 0,
    })

    return findings


def summarize_with_llm(findings: list[dict]) -> str:
    prompt = (
        "You are a data QA agent. Below are the raw results of 4 "
        "reconciliation checks comparing SOURCE_ORDERS to TARGET_ORDERS "
        "after an ETL run. Write a short report (5-8 sentences) a data "
        "engineer could act on immediately: state which checks failed, "
        "the likely root cause for each, and which one is most urgent to "
        "fix first and why. No preamble.\n\n"
        f"{findings}"
    )
    return llm.invoke(prompt).content


def upload_report(report: str) -> str:
    key = "qa-reports/source-vs-target-orders.md"
    boto3.client("s3").put_object(
        Bucket=S3_BUCKET, Key=key, Body=report.encode("utf-8"),
        ContentType="text/markdown",
    )
    return f"s3://{S3_BUCKET}/{key}"


if __name__ == "__main__":
    con = connect()
    try:
        seed_tables(con)
        findings = run_checks(con)
        print("=== Raw check results ===")
        for f in findings:
            status = "PASS" if f["passed"] else "FAIL"
            print(f"[{status}] {f['rule']}: {f['detail']}")

        report = summarize_with_llm(findings)
        print("\n=== LLM-written QA report ===")
        print(report)

        s3_uri = upload_report(report)
        print(f"\nUploaded to {s3_uri}")
    finally:
        con.close()
