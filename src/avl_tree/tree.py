"""AVL tree implementation.

An AVL tree is a self-balancing binary search tree in which the heights of
the two child subtrees of any node differ by at most one. Insertion and
deletion rebalance the tree through single or double rotations, which keeps
lookups, insertions and deletions at O(log n).

This module implements the tree functionally: every mutating operation
returns the (possibly new) root of the subtree it was applied to, so callers
must reassign the result, e.g. ``root = insert(root, 10)``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Node:
    """A node in an AVL tree.

    Attributes
    ----------
    val : int
        The value stored in the node.
    left : Node or None
        Left child, holding values smaller than ``val``.
    right : Node or None
        Right child, holding values larger than ``val``.
    height : int
        Height of the subtree rooted at this node. A leaf has height 1.
    """

    val: int
    left: Node | None = None
    right: Node | None = None
    height: int = 1


def height(node: Node | None) -> int:
    """Return the height of a subtree.

    Parameters
    ----------
    node : Node or None
        Root of the subtree.

    Returns
    -------
    int
        ``0`` for an empty subtree, otherwise the stored height of ``node``.
    """
    if node is None:
        return 0
    return node.height


def balance_factor(node: Node | None) -> int:
    """Compute the balance factor of a node.

    Parameters
    ----------
    node : Node or None
        Root of the subtree.

    Returns
    -------
    int
        ``height(left) - height(right)``, or ``0`` for an empty subtree.
        A value greater than 1 means the node is left-heavy; a value less
        than -1 means it is right-heavy.
    """
    if not node:
        return 0
    return height(node.left) - height(node.right)


def right_rotate(node: Node) -> Node:
    r"""Rotate a subtree to the right around ``node``.

    The left child of ``node`` becomes the new root of the subtree::

            node             left_child
            /  \             /      \
       left_child  C   ->   A        node
         /  \                        /  \
        A    B                      B    C

    Parameters
    ----------
    node : Node
        Root of the subtree to rotate. Must have a left child.

    Returns
    -------
    Node
        The new root of the rotated subtree (the former left child).

    Notes
    -----
    Heights of the two nodes whose children changed are recomputed.
    """
    left_child = node.left
    assert left_child is not None, "right_rotate requires a left child"
    ltr = left_child.right
    left_child.right = node
    node.left = ltr

    node.height = 1 + max(height(node.left), height(node.right))
    left_child.height = 1 + max(height(left_child.left), height(left_child.right))
    return left_child


def left_rotate(node: Node) -> Node:
    r"""Rotate a subtree to the left around ``node``.

    The right child of ``node`` becomes the new root of the subtree::

         node                   right_child
         /  \                   /        \
        A   right_child   ->  node         C
              /  \            /  \
             B    C          A    B

    Parameters
    ----------
    node : Node
        Root of the subtree to rotate. Must have a right child.

    Returns
    -------
    Node
        The new root of the rotated subtree (the former right child).

    Notes
    -----
    Heights of the two nodes whose children changed are recomputed.
    """
    right_child = node.right
    assert right_child is not None, "left_rotate requires a right child"
    rtl = right_child.left
    right_child.left = node
    node.right = rtl

    node.height = 1 + max(height(node.left), height(node.right))
    right_child.height = 1 + max(height(right_child.left), height(right_child.right))
    return right_child


def balance_tree(root: Node) -> Node:
    """Restore the AVL invariant at ``root`` if it is violated.

    Handles all four imbalance cases: Left-Left and Right-Right (single
    rotation) as well as Left-Right and Right-Left (double rotation).

    Parameters
    ----------
    root : Node
        Root of a subtree whose children are already balanced and whose
        ``height`` is up to date.

    Returns
    -------
    Node
        The root of the balanced subtree. This is ``root`` itself if no
        rotation was needed.
    """
    balance = balance_factor(root)
    if balance > 1:
        assert root.left is not None  # implied by balance > 1
        if balance_factor(root.left) < 0:  # Left-Right case
            root.left = left_rotate(root.left)
        root = right_rotate(root)
    elif balance < -1:
        assert root.right is not None  # implied by balance < -1
        if balance_factor(root.right) > 0:  # Right-Left case
            root.right = right_rotate(root.right)
        root = left_rotate(root)
    return root


def insert(root: Node | None, val: int) -> Node:
    """Insert a value into an AVL tree.

    Duplicate values are ignored.

    Parameters
    ----------
    root : Node or None
        Root of the tree (or subtree) to insert into. ``None`` creates a
        new tree.
    val : int
        Value to insert.

    Returns
    -------
    Node
        The root of the tree after insertion and rebalancing. This may
        differ from the ``root`` passed in, so callers must reassign it.

    Notes
    -----
    Time complexity is O(log n). The implementation is recursive, with
    recursion depth bounded by the tree height.
    """
    if not root:
        return Node(val)
    if root.val == val:
        return root
    elif root.val > val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    root.height = 1 + max(height(root.left), height(root.right))
    return balance_tree(root)


def delete(root: Node | None, val: int) -> Node | None:
    """Delete a value from an AVL tree.

    If ``val`` is not present, the tree's contents are left unchanged.

    Parameters
    ----------
    root : Node or None
        Root of the tree (or subtree) to delete from.
    val : int
        Value to delete.

    Returns
    -------
    Node or None
        The root of the tree after deletion and rebalancing, or ``None``
        if the tree becomes empty. This may differ from the ``root`` passed
        in, so callers must reassign it.

    Notes
    -----
    A node with two children is replaced by its in-order successor (the
    smallest value in its right subtree), which is then deleted from the
    right subtree. Time complexity is O(log n).
    """
    if not root:
        return root
    if root.val > val:
        root.left = delete(root.left, val)
    elif root.val < val:
        root.right = delete(root.right, val)
    else:
        if not root.left:
            return root.right
        elif not root.right:
            return root.left
        succ = root.right
        while succ.left:
            succ = succ.left
        root.val = succ.val
        root.right = delete(root.right, succ.val)
    root.height = 1 + max(height(root.left), height(root.right))
    return balance_tree(root)


def pre_order(root: Node | None) -> None:
    """Print the tree's values in pre-order (node, left, right).

    Parameters
    ----------
    root : Node or None
        Root of the tree (or subtree) to traverse.

    Returns
    -------
    None
        Values are printed to standard output, one per line.
    """
    if not root:
        return
    print(root.val)
    pre_order(root.left)
    pre_order(root.right)
