# avl-tree

A small, fully typed implementation of an AVL tree (a self-balancing binary
search tree) in Python. Insertion and deletion are O(log n).

## Usage

```python
from avl_tree import insert, delete, pre_order

root = None
for value in [10, 20, 30, 40, 50, 25]:
    root = insert(root, value)

root = delete(root, 10)
pre_order(root)
```

Operations are functional: `insert` and `delete` return the new root of the
tree, so always reassign the result.

## Development

```bash
pip install -e ".[dev]"

ruff check . && ruff format --check .   # lint and formatting
mypy                                    # strict type checking
pytest --cov                            # tests with coverage
```
