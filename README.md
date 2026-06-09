# Olist Customer Intelligence Dashboard

Premium Streamlit dashboard for Project 1 MBKM Sains Data.

## Sections

1. Executive Overview — KPI, GMV/orders trend, category revenue map, top markets.
2. Customer Segmentation — RFM summary, revenue contribution, segment priority, and action cards.
3. Delivery Risk — late delivery review impact, model comparison, and risk interpretation.
4. Business Insight — executive recommendation cards.

## Required folder

Keep the following CSV files inside `olist_output/`:

- kpi.csv
- monthly_kpi.csv
- category_kpi.csv
- state_kpi.csv
- segment_priority.csv
- rfm_diagnostic.csv
- late_review_impact.csv
- model_comparison.csv
- model_result.csv
- risk_summary.csv
- insight_table.csv

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
