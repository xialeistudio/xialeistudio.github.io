---
title: LeetCode99——恢复二叉搜索树
date: 2022-02-06 20:24:19
tags:
- tree
categories:
- algorithm
---

## 题目

给定两个整数数组 preorder 和 inorder ，其中 preorder 是二叉树的先序遍历， inorder 是同一棵树的中序遍历，请构造二叉树并返回其根节点。

**示例 1:**

![img](https://assets.leetcode.com/uploads/2021/02/19/tree.jpg)

```
输入: preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
输出: [3,9,20,null,null,15,7]
```

**示例 2:**

```
输入: preorder = [-1], inorder = [-1]
输出: [-1]
```

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

利用前序遍历和中序遍历性质

1. 前序遍历节点顺序如下[根，左，右]
2. 中序遍历节点顺序如下[左，根，右]
3. 前序遍历的左/右子树长度和中序遍历的左/右子树长度是相同的
4. 由于这是同一颗树遍历来的，因此前序遍历的第0个元素和中序遍历的根节点是相同的。因此只要能定位中序遍历的根节点，将中序遍历数组拆分为左右两半后就可以了
   1. 查找中序遍历的数组中值为前序遍历第0个元素节点的下标，记为`middle`
   2. 此时中序遍历左子树节点列表为`[:middle]`，右子树节点列表为`[middle+1:]`，左子树长度为`len([:middle])`，记为`leftTreeSize`
   3. 根据第3点可知，前序遍历的左子树节点列表为`[1:leftTreeSize+1]`,右子树节点为`[leftTreeSize+1:]`

```go
// 递归法
// 中序，左根右；前序根左右
// 1. 根据中序遍历找到根节点(值为preorder[0]的节点)
// 2. 中序遍历根节点左边的节点数和前序遍历的节点数是相同的，根据该性质可以将前序遍历拆分为两半
func buildTree(preorder []int, inorder []int) *TreeNode {
	n := len(preorder)
	if n == 0 {
		return nil
	}
	root := &TreeNode{Val: preorder[0]}
	// 查找根节点在中序遍历的位置
	middle := 0
	for ; middle < n; middle++ {
		if inorder[middle] == preorder[0] {
			break
		}
	}
	leftTreeSize := len(inorder[:middle])                                 // 中序遍历的左半边就是左子树
	root.Left = buildTree(preorder[1:leftTreeSize+1], inorder[:middle])   // 将前序遍历的左半边和中序的左半边递归构造左子树
	root.Right = buildTree(preorder[leftTreeSize+1:], inorder[middle+1:]) // 将前序遍历的右半边和中序遍历的右半边构建右子树
	return root
}
```

