# Roadmap

Phased plan for filling in `topics/`. Order roughly follows dependency (later phases assume familiarity with earlier ones) — not a strict requirement, just a sane default path.

This is a planning document (what order, not what's done) — for actual completion status, see [PROGRESS.md](PROGRESS.md), which is computed automatically from chapter metadata and can't drift out of sync the way a hand-checked box here would.

## Phase 1 — Foundations

Python, SQL, Data Modeling, Distributed Systems

## Phase 2 — Data Engineering Core

Spark, Airflow, Kafka, dbt, Snowflake, Lakehouse, Data Governance

## Phase 3 — Cloud & Platform

AWS, Kubernetes, Terraform, Security, Observability

## Phase 4 — AI Engineering

AI Engineering, LLMs, RAG, Vector Databases, Knowledge Graphs, MCP, LangGraph

## Phase 5 — Systems & Leadership

System Design, Leadership, Production Projects

## Phase 6 — Interview & Career

Research Papers (reading queue, see PAPERS.md), Mock Interviews, Salesforce Interview Preparation

## What "done" means

A chapter is worth marking `complete` (`python3 scripts/mark_complete.py <path>`) once it covers, at minimum: Concepts, Production Architecture, Failure Modes, and Interview Questions — the four sections that matter most for actually being useful in an interview or on-call. The rest of the template can fill in over time; use `in-progress` until then.
