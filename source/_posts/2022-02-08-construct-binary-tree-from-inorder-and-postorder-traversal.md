---
title: LeetCode106——从中序与后序遍历序列构造二叉树
date: 2022-02-08 20:24:19
tags:
- tree
- leetcode
categories:
- Algorithm
---

## 题目

给定两个整数数组 inorder 和 postorder ，其中 inorder 是二叉树的中序遍历， postorder 是同一棵树的后序遍历，请你构造并返回这颗 二叉树 。

 **示例 1:**

```
输入：inorder = [9,3,15,20,7], postorder = [9,15,7,20,3]
输出：[3,9,20,null,null,15,7]
```

**示例 2:**

```
输入：inorder = [-1], postorder = [-1]
输出：[-1]
```



来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

> 核心是中序遍历的顺序是[左，根，右]，后序遍历是[左，右，根]。而同一颗树不管前/中/后序遍历，节点数是不变的。

```go
// 后序遍历顺序: 左右根
// 1. postorder最后一个元素为根
// 2. 遍历inorder查找根的index
// 3. inorder[:index]为左子树，inorder[index+1:]为右子树，左子树大小记为leftTreeSize
// 4. postorder[:leftTreeSize]为左子树，postorder[leftTreeSize:len(postorder)-1]是右子树
func buildTree(inorder []int, postorder []int) *TreeNode {
	n := len(inorder)
	if n == 0 {
		return nil
	}
	if n == 1 {
		return &TreeNode{Val: inorder[0]}
	}
	// 查找中序遍历根的index
	index := -1
	rootValue := postorder[len(postorder)-1]
	for i := 0; i < len(inorder); i++ {
		if inorder[i] == rootValue {
			index = i
			break
		}
	}
	// 分割数组
	leftTreeSize := len(inorder[:index])
	root := &TreeNode{Val: rootValue}
	root.Left = buildTree(inorder[:index], postorder[:leftTreeSize])
	root.Right = buildTree(inorder[index+1:], postorder[leftTreeSize:len(postorder)-1])
	return root
}
```

