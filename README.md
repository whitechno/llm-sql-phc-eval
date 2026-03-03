# EDA: LLM-SQL-PHC Benchmark Datasets

Exploratory data analysis of the 7 processed datasets from the paper  
*Optimizing LLM Queries in Relational Data Analytics Workloads*
(arXiv:2403.05821v2).

Datasets analyzed here are the sampled/filtered JSONL files (not the raw
downloads). See [datasets-README](datasets-README.md) for details on the
datasets. See the [nbs](nbs) folder for the Jupyter notebooks with EDA.

## Tech Notes

To set the Python environment, run:
```text
uv sync
```

`llm-sql-phc-eval` public GitHub repo has been created and pushed with `gh` CLI
tool:
```text
gh repo create llm-sql-phc-eval --public --source=. --remote=origin --push 2>&1
```

