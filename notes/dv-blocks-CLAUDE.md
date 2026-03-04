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

## Blocks and distinct values as a graph

Create new notebook `nbs/eda-04-dv-blocks-conn.ipynb` where we will explore the
relationship between blocks by expressing them as a graph and computing
connectivity.

Combine all blocks and remaining distinct values with a non-zero hit
count ($R_v \geq 2$). We can say that any remaining distinct value is a
**block** with a single column (a "trivial" block).

Each block $b$ is represented by:
- a set of columns $[V1, V2, ..., Vn]$ ($n$ is 1 for a trivial block);
- a sorted array of row indices $R_b = R_{v1} = R_{v2} = ...$ (a "signature" for
  the block);
- a hit count for the block: $HC_b = \sum_i HC_{vi}$.

By construction of blocks, each block has a unique signature, i.e., there are no
two blocks that span the same set of rows. However, blocks may have overlapping
rows.

According to the intersection of their rows $R_a$ and $R_b$, there are 3
possible relationship types between two blocks $a$ and $b$:
- **No overlap**, $R_a \cap R_b = \emptyset$.
- **Strict overlap**, when one is strictly within the other, say $b$
  within $a$: $R_b \subset R_a$ and $R_a \setminus R_b \neq \emptyset$. (Can be
  expressed as $R_b \subsetneq R_a$.)
- **Normal overlap**, $R_a \neq R_b$ and $R_a \cap R_b \neq \emptyset$.

(Obviously, we cannot have two blocks that span the same set of
rows, $R_a = R_b$.)

If we exclude blocks that are strictly within other blocks, then we are left
with blocks that have only 2 types of relationships: normal overlap and no
overlap. We can express this as a graph with blocks as (hit-count weighted)
vertices and edges between blocks that have a normal overlap.

Express each dataset as such a graph, present some interesting properties of the
graph, and compute its connectivity.

## EDA-04 results: graph connectivity findings

Notebook: `nbs/eda-04-dv-blocks-conn.ipynb`.

### Summary table

| Dataset  | n_rows  | Total blocks | Trivial (1-col) | Inner removed | Vertices kept | Edges   | Components |
|----------|---------|--------------|-----------------|---------------|---------------|---------|------------|
| Movies   | 15,000  | 1,581        | 331             | 1,287         | 294           | 2,322   | 1          |
| Products | 14,890  | 3,120        | 1,059           | 2,646         | 474           | 2,817   | 1          |
| Beer     | 28,479  | 11,193       | 6,603           | 5,674         | 5,519         | 151,853 | 1          |
| PDMX     | 10,000  | 10,105       | 9,266           | 10,104        | 1             | 0       | 1          |
| FEVER    | 145,449 | 5,898        | 5,897           | 5,220         | 678           | 1,352   | 1          |
| SQuAD    | 87,599  | 26,599       | 26,539          | 1,792         | 24,807        | 25,430  | 5,714      |
| BIRD     | 15,000  | 3,509        | 38              | 0             | 3,509         | 62      | 3,448      |

### Key findings

**Most datasets form a single connected component** (Movies, Products, Beer,
PDMX, FEVER). After removing inner blocks, all remaining blocks connect into one
graph via normal overlap. This suggests the datasets have a rich, interlocking
repetition structure — repeated values in one column co-occur with repeated
values in others.

**SQuAD fragments into 5,714 components** despite having the most blocks (
26,599). Almost all blocks (26,539 / 99.8%) are trivial (single-column), and
5,362 of those are isolated singletons. One giant component contains 18,209
blocks — driven by the `context` column where long passages repeat across many
questions. The fragmentation reflects SQuAD's structure: each context passage is
an island of related Q&A pairs that rarely overlaps with other passages.

**BIRD is nearly fully disconnected** (3,448 components from 3,509 vertices,
only 62 edges). BIRD has no inner blocks at all — no block's row set is
contained in another's. The small number of edges comes from the Posts/Comments
JOIN structure where a few post bodies share partial overlapping comment sets.
Most blocks are isolated.

**PDMX collapses to a single vertex**. After inner-block removal, 10,104 of
10,105 blocks are eliminated — nearly every block is contained inside the one
surviving 6-column block covering all 10,000 rows (`hasannotations='True'`,
`isdraft='False'`, and 4 other columns all spanning the full dataset). PDMX has
almost no variation in its categorical columns.

**Beer has by far the most edges** (151,853) despite fewer vertices than SQuAD.
Its high edge density (average degree ≈ 55) comes from the `beer/style` column:
many style values are subsets of each other's row sets before inner-block
removal, and after removal the remaining trivial style blocks heavily overlap
with the multi-column blocks.

### Inner block compression rates

The fraction of blocks eliminated as "inner" varies widely:

- PDMX: 10,104 / 10,105 = **99.99%** — extreme compression
- Movies: 1,287 / 1,581 = **81%**
- Products: 2,646 / 3,120 = **85%**
- FEVER: 5,220 / 5,898 = **88%**
- Beer: 5,674 / 11,193 = **51%**
- SQuAD: 1,792 / 26,599 = **7%** — almost no containment
- BIRD: 0 / 3,509 = **0%** — no containment at all

High compression (PDMX, Movies, Products, FEVER) indicates deeply nested block
hierarchies — a small number of large "parent" blocks contain many smaller ones.
Low compression (SQuAD, BIRD) indicates flat structure with few containment
relationships.

### Implementation notes

- **Signature type**: `frozenset` (not `tuple`) is used in eda-04 because
  `frozenset.issubset()` is needed for inner-block detection.
- **Inner-block detection efficiency**: Rather than O(n²) pairwise checks, a
  `row → block indices` mapping is built so each block j only checks candidate
  parents that share its first row. This makes Beer (5,519 vertices) fast
  (0.6s).
- **Edge finding**: Same row-mapping approach — iterate rows, emit pairs of
  blocks sharing that row into an `edge_set`. After inner-block filtering, any
  shared row implies normal overlap (strict containment is impossible by
  construction).
