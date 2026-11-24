# avl-tree

[![CI](https://github.com/ritesh7766/avl_tree/actions/workflows/ci.yml/badge.svg)](https://github.com/ritesh7766/avl_tree/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Typed: mypy](https://img.shields.io/badge/mypy-strict-blue.svg)](https://mypy-lang.org/)

A lightweight, strictly typed implementation of an AVL tree (a self-balancing binary search tree) in Python with zero runtime dependencies. All mutating operations preserve the AVL height invariant via single and double rotations, guaranteeing $O(\log n)$ worst-case time complexity for lookups, insertions, and deletions.

## Installation

```bash
git clone [https://github.com/](https://github.com/)<owner>/<repo>.git
cd <repo>
pip install -e .
```

## Usage

Operations follow a functional API: `insert` and `delete` return the updated root of the tree, so callers should always reassign the returned reference.

```python
from avl_tree import Node, delete, insert, pre_order

root: Node | None = None
for value in [10, 20, 30, 40, 50, 25]:
    root = insert(root, value)

root = delete(root, 10)
pre_order(root)
```

### API Reference

| Symbol | Signature | Description |
| :--- | :--- | :--- |
| `Node` | `Node(val, left=None, right=None, height=1)` | Dataclass representing a tree node and its subtree height. |
| `insert` | `insert(root: Node \| None, val: int) -> Node` | Inserts `val` (ignoring duplicates) and returns the rebalanced root. |
| `delete` | `delete(root: Node \| None, val: int) -> Node \| None` | Removes `val` if present and returns the rebalanced root (or `None` if empty). |
| `height` | `height(node: Node \| None) -> int` | Returns the height of `node` (`0` if `None`). |
| `balance_factor` | `balance_factor(node: Node \| None) -> int` | Returns `height(left) - height(right)`. |
| `pre_order` | `pre_order(root: Node \| None) -> None` | Prints node values in pre-order traversal (`node -> left -> right`). |

## Development

Install development dependencies and run the full quality suite:

```bash
pip install -e ".[dev]"

ruff check . && ruff format --check .   # lint and formatting
mypy                                    # strict type checking
pytest --cov                            # tests with coverage
```

## License

This project is licensed under the [MIT License](LICENSE).
