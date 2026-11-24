"""Tests for the AVL tree implementation."""

from __future__ import annotations

import math
import random
from collections.abc import Iterable
from typing import TypeAlias

import pytest

import avl_tree
from avl_tree import (
    Node,
    balance_factor,
    balance_tree,
    delete,
    height,
    insert,
    left_rotate,
    pre_order,
    right_rotate,
)

# Nested-tuple snapshot of a tree: (value, left_shape, right_shape) or None.
Shape: TypeAlias = "tuple[int, Shape, Shape] | None"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _stored_height(node: Node | None) -> int:
    """Height lookup that is independent of the code under test."""
    return node.height if node else 0


def make(val: int, left: Node | None = None, right: Node | None = None) -> Node:
    """Build a node with a correct ``height`` for hand-made trees."""
    return Node(val, left, right, 1 + max(_stored_height(left), _stored_height(right)))


def leaf(val: int) -> Shape:
    """Shape of a node without children."""
    return (val, None, None)


def build(values: Iterable[int]) -> Node | None:
    """Insert ``values`` one by one into a fresh tree."""
    root: Node | None = None
    for value in values:
        root = insert(root, value)
    return root


def shape(node: Node | None) -> Shape:
    """Snapshot the structure of a tree as nested tuples."""
    if node is None:
        return None
    return (node.val, shape(node.left), shape(node.right))


def in_order(node: Node | None) -> list[int]:
    """Values of the tree in sorted (in-order) sequence."""
    if node is None:
        return []
    return [*in_order(node.left), node.val, *in_order(node.right)]


def assert_valid_avl(
    node: Node | None,
    low: float = -math.inf,
    high: float = math.inf,
) -> int:
    """Assert BST order, stored heights and AVL balance; return the height."""
    if node is None:
        return 0
    assert low < node.val < high, f"BST order violated at {node.val}"
    left_height = assert_valid_avl(node.left, low, node.val)
    right_height = assert_valid_avl(node.right, node.val, high)
    assert node.height == 1 + max(left_height, right_height), (
        f"stale height at {node.val}"
    )
    assert abs(left_height - right_height) <= 1, f"unbalanced at {node.val}"
    return node.height


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
class TestNode:
    def test_defaults(self) -> None:
        node = Node(5)
        assert node.val == 5
        assert node.left is None
        assert node.right is None
        assert node.height == 1


class TestHeight:
    def test_empty_tree_has_height_zero(self) -> None:
        assert height(None) == 0

    def test_leaf_has_height_one(self) -> None:
        assert height(Node(1)) == 1

    def test_returns_stored_height(self) -> None:
        assert height(Node(1, height=7)) == 7


class TestBalanceFactor:
    def test_empty_tree_is_zero(self) -> None:
        assert balance_factor(None) == 0

    def test_leaf_is_zero(self) -> None:
        assert balance_factor(Node(1)) == 0

    def test_left_heavy_is_positive(self) -> None:
        assert balance_factor(make(2, make(1))) == 1

    def test_right_heavy_is_negative(self) -> None:
        assert balance_factor(make(1, None, make(2))) == -1

    def test_unbalanced_chain(self) -> None:
        assert balance_factor(make(3, make(2, make(1)))) == 2
        assert balance_factor(make(1, None, make(2, None, make(3)))) == -2


class TestRotations:
    def test_right_rotate_restructures(self) -> None:
        #        5                3
        #       / \             /   \
        #      3   6    ->     2     5
        #     / \                   / \
        #    2   4                 4   6
        root = make(5, make(3, make(2), make(4)), make(6))
        new_root = right_rotate(root)
        assert shape(new_root) == (3, leaf(2), (5, leaf(4), leaf(6)))

    def test_left_rotate_restructures(self) -> None:
        #      2                    4
        #     / \                 /   \
        #    1   4       ->      2     5
        #       / \             / \
        #      3   5           1   3
        root = make(2, make(1), make(4, make(3), make(5)))
        new_root = left_rotate(root)
        assert shape(new_root) == (4, (2, leaf(1), leaf(3)), leaf(5))

    def test_right_rotate_updates_heights(self) -> None:
        root = make(5, make(3, make(2), make(4)), make(6))
        new_root = right_rotate(root)
        assert new_root.height == 3
        assert new_root.right is not None
        assert new_root.right.height == 2
        assert_valid_avl(new_root)

    def test_left_rotate_updates_heights(self) -> None:
        root = make(2, make(1), make(4, make(3), make(5)))
        new_root = left_rotate(root)
        assert new_root.height == 3
        assert new_root.left is not None
        assert new_root.left.height == 2
        assert_valid_avl(new_root)

    def test_rotations_preserve_in_order(self) -> None:
        root = make(5, make(3, make(2), make(4)), make(6))
        assert in_order(right_rotate(root)) == [2, 3, 4, 5, 6]
        root = make(2, make(1), make(4, make(3), make(5)))
        assert in_order(left_rotate(root)) == [1, 2, 3, 4, 5]

    def test_left_then_right_rotate_round_trips(self) -> None:
        root = make(5, make(3, make(2), make(4)), make(6))
        original = shape(root)
        assert shape(left_rotate(right_rotate(root))) == original


class TestBalanceTree:
    def test_balanced_node_is_returned_unchanged(self) -> None:
        root = make(2, make(1), make(3))
        assert balance_tree(root) is root

    def test_left_left_case(self) -> None:
        root = make(3, make(2, make(1)))
        result = balance_tree(root)
        assert shape(result) == (2, leaf(1), leaf(3))
        assert_valid_avl(result)

    def test_right_right_case(self) -> None:
        root = make(1, None, make(2, None, make(3)))
        result = balance_tree(root)
        assert shape(result) == (2, leaf(1), leaf(3))
        assert_valid_avl(result)

    def test_left_right_case(self) -> None:
        root = make(3, make(1, None, make(2)))
        result = balance_tree(root)
        assert shape(result) == (2, leaf(1), leaf(3))
        assert_valid_avl(result)

    def test_right_left_case(self) -> None:
        root = make(1, None, make(3, make(2)))
        result = balance_tree(root)
        assert shape(result) == (2, leaf(1), leaf(3))
        assert_valid_avl(result)


class TestInsert:
    def test_insert_into_empty_tree_creates_root(self) -> None:
        root = insert(None, 5)
        assert shape(root) == leaf(5)
        assert root.height == 1

    def test_smaller_values_go_left_and_larger_go_right(self) -> None:
        root = build([2, 1, 3])
        assert shape(root) == (2, leaf(1), leaf(3))

    def test_duplicate_is_ignored(self) -> None:
        root = build([1, 2, 3])
        before = shape(root)
        root = insert(root, 2)
        assert shape(root) == before
        assert_valid_avl(root)

    @pytest.mark.parametrize(
        ("values", "expected"),
        [
            pytest.param([3, 2, 1], (2, leaf(1), leaf(3)), id="left-left"),
            pytest.param([1, 2, 3], (2, leaf(1), leaf(3)), id="right-right"),
            pytest.param([3, 1, 2], (2, leaf(1), leaf(3)), id="left-right"),
            pytest.param([1, 3, 2], (2, leaf(1), leaf(3)), id="right-left"),
        ],
    )
    def test_each_rotation_case(self, values: list[int], expected: Shape) -> None:
        root = build(values)
        assert shape(root) == expected
        assert_valid_avl(root)

    def test_perfect_tree_from_ascending_values(self) -> None:
        root = build(range(1, 128))
        assert root is not None
        assert root.height == 7
        assert_valid_avl(root)

    @pytest.mark.parametrize("n", [1, 2, 3, 10, 100, 1000])
    def test_ascending_inserts_stay_balanced(self, n: int) -> None:
        root = build(range(n))
        assert root is not None
        assert_valid_avl(root)
        assert in_order(root) == list(range(n))
        assert root.height <= 1.45 * math.log2(n + 2)

    @pytest.mark.parametrize("n", [1, 2, 3, 10, 100, 1000])
    def test_descending_inserts_stay_balanced(self, n: int) -> None:
        root = build(range(n, 0, -1))
        assert root is not None
        assert_valid_avl(root)
        assert in_order(root) == list(range(1, n + 1))
        assert root.height <= 1.45 * math.log2(n + 2)

    def test_random_inserts_keep_invariants(self) -> None:
        rng = random.Random(42)
        values = rng.sample(range(10_000), 500)
        root: Node | None = None
        for value in values:
            root = insert(root, value)
            assert_valid_avl(root)
        assert in_order(root) == sorted(values)


class TestDelete:
    def test_delete_from_empty_tree_returns_none(self) -> None:
        assert delete(None, 1) is None

    def test_delete_only_node_empties_the_tree(self) -> None:
        assert delete(Node(1), 1) is None

    def test_delete_missing_value_leaves_tree_unchanged(self) -> None:
        root = build([2, 1, 3])
        root = delete(root, 99)
        assert shape(root) == (2, leaf(1), leaf(3))
        assert_valid_avl(root)

    def test_delete_leaf(self) -> None:
        root = delete(build([2, 1, 3]), 1)
        assert shape(root) == (2, None, leaf(3))
        assert_valid_avl(root)

    def test_delete_node_with_only_left_child(self) -> None:
        root = delete(build([3, 2, 4, 1]), 2)
        assert shape(root) == (3, leaf(1), leaf(4))
        assert_valid_avl(root)

    def test_delete_node_with_only_right_child(self) -> None:
        root = delete(build([2, 1, 4, 5]), 4)
        assert shape(root) == (2, leaf(1), leaf(5))
        assert_valid_avl(root)

    def test_delete_node_with_two_children_uses_in_order_successor(self) -> None:
        root = delete(build([4, 2, 6, 1, 3, 5, 7]), 4)
        assert shape(root) == (5, (2, leaf(1), leaf(3)), (6, None, leaf(7)))
        assert_valid_avl(root)

    def test_delete_triggers_right_rotation(self) -> None:
        root = delete(build([2, 1, 3, 0]), 3)
        assert shape(root) == (1, leaf(0), leaf(2))
        assert_valid_avl(root)

    def test_delete_triggers_left_rotation(self) -> None:
        root = delete(build([2, 1, 3, 4]), 1)
        assert shape(root) == (3, leaf(2), leaf(4))
        assert_valid_avl(root)

    def test_delete_triggers_left_right_rotation(self) -> None:
        root = delete(build([3, 1, 4, 2]), 4)
        assert shape(root) == (2, leaf(1), leaf(3))
        assert_valid_avl(root)

    def test_delete_triggers_right_left_rotation(self) -> None:
        root = delete(build([2, 1, 4, 3]), 1)
        assert shape(root) == (3, leaf(2), leaf(4))
        assert_valid_avl(root)

    def test_deleting_every_value_empties_the_tree(self) -> None:
        rng = random.Random(7)
        values = rng.sample(range(1_000), 200)
        root = build(values)
        rng.shuffle(values)
        remaining = set(values)
        for value in values:
            root = delete(root, value)
            remaining.discard(value)
            assert_valid_avl(root)
            assert in_order(root) == sorted(remaining)
        assert root is None

    def test_random_interleaved_inserts_and_deletes_match_a_set(self) -> None:
        rng = random.Random(123)
        model: set[int] = set()
        root: Node | None = None
        for _ in range(1_500):
            value = rng.randrange(200)
            if rng.random() < 0.55:
                root = insert(root, value)
                model.add(value)
            else:
                root = delete(root, value)
                model.discard(value)
            assert_valid_avl(root)
            assert in_order(root) == sorted(model)


class TestPreOrder:
    def test_empty_tree_prints_nothing(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        pre_order(None)
        assert capsys.readouterr().out == ""

    def test_single_node(self, capsys: pytest.CaptureFixture[str]) -> None:
        pre_order(Node(1))
        assert capsys.readouterr().out == "1\n"

    def test_visits_node_then_left_then_right(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        pre_order(build([4, 2, 6, 1, 3, 5, 7]))
        assert capsys.readouterr().out == "4\n2\n1\n3\n6\n5\n7\n"


class TestPublicApi:
    def test_all_exports_are_importable(self) -> None:
        for name in avl_tree.__all__:
            assert hasattr(avl_tree, name)

    def test_exports_match_expected_names(self) -> None:
        assert set(avl_tree.__all__) == {
            "Node",
            "balance_factor",
            "balance_tree",
            "delete",
            "height",
            "insert",
            "left_rotate",
            "pre_order",
            "right_rotate",
        }
