# exploring distinct values and relationships between them

## Value blocks
For the notebook `nbs/eda-03-dv-blocks.ipynb`.

Each distinct value in a table `T` can be expressed as a set of the following
properties:
- the value `v` itself;
- the column `V` that contains the value `v`;
- a set of row indices $R_v$ that value `v` spans: $R_v = \{r | T[r][V] = v\}$;
- a hit count for the value `v`: $HC_v = \text{len}(v)^2 \times (|R_v| - 1)$.

$|R_v|$ is the number of rows with value `v`, and $\text{len}(v)$ is the string
length of `v`.

We are interested only in distinct values that span at least two
rows: $|R_v|>1$.

If two distinct values `u` and `v` (from two different columns `U` and `V`)
are in the same set of rows, $R_u = R_v$, then we want to combine them into a
single block with the following properties:
- a set of columns $[U, V]$;
- a set of row indices $R_{uv} = R_u = R_v$;
- a hit count for the block: $HC_{uv} = HC_u + HC_v$.

If there is a third distinct value `w` that is in the same set of rows as `u`
and `v`, then we want to combine it into a block in the same way:
- a set of columns $[U, V, W]$;
- a set of row indices $R_{uvw} = R_u = R_v = R_w$;
- a hit count for the block: $HC_{uvw} = HC_u + HC_v + HC_w$.

We want to find all such blocks in the table `T`.

What is the most efficient way to do this?

Implement it in Python and apply it to all tables in the dataset.

### Algorithm

For each column `V` in table `T`, call `df.groupby(V).indices` to obtain a dict
mapping each distinct value `v` to the array of row indices where it appears.
For every value whose row count is ≥ 2, compute a **signature** — a sorted tuple
of those row indices (`tuple(sorted(row_indices))`) — and record `(V, v, HC_v)`
under that signature key in a shared dict.

After processing all columns, every signature key that has entries from ≥ 2
different columns corresponds to a block. Collect those entries, compute the
block's total hit count, and sort blocks by hit count descending.

```python
from collections import defaultdict


def find_dv_blocks(df):
    df = df.reset_index(drop=True)  # ensure 0-based integer index
    sig_groups = defaultdict(list)

    for col in df.columns:
        for val, idx_arr in df.groupby(col, sort=False).indices.items():
            n = len(idx_arr)
            if n < 2:
                continue
            sig = tuple(sorted(idx_arr.tolist()))
            hc = len(str(val)) ** 2 * (n - 1)
            sig_groups[sig].append((col, val, hc))

    blocks = []
    for sig, entries in sig_groups.items():
        cols_in_block = sorted({col for col, val, hc in entries})
        if len(cols_in_block) < 2:
            continue
        blocks.append({
            "row_count": len(sig),
            "n_cols": len(cols_in_block),
            "cols": cols_in_block,
            "hc": sum(hc for col, val, hc in entries),
            "entries": sorted(entries, key=lambda x: x[0]),
        })

    return sorted(blocks, key=lambda b: b["hc"], reverse=True)
```

**Complexity**: O(N · C) for data access (N rows, C columns), plus O(k log k)
per non-singleton value to sort its k row indices. The signature tuple is used
as a Python dict key, so grouping across columns costs O(k) per lookup (tuple
hashing). Total memory is bounded by the sum of row counts of all non-singleton
values.
