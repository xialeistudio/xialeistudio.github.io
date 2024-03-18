---
slug: convert-sorted-array-to-binary-search-tree
title: LeetCode108——将有序数组转换为二叉搜索树
date: 2022-02-08 20:24:19
tags:
- tree
- leetcode
categories:
- Algorithm
---

## 题目

给你一个整数数组 nums ，其中元素已经按 升序 排列，请你将其转换为一棵 高度平衡 二叉搜索树。

高度平衡 二叉树是一棵满足「每个节点的左右两个子树的高度差的绝对值不超过 1 」的二叉树。

**示例 1：**

![img](https://assets.leetcode.com/uploads/2021/02/18/btree1.jpg)

```
输入：nums = [-10,-3,0,5,9]
输出：[0,-3,9,-10,null,5]
```

**示例 2：**

![img](https://assets.leetcode.com/uploads/2021/02/18/btree.jpg)

```
输入：nums = [1,3]
输出：[3,1]
解释：[1,3] 和 [3,1] 都是高度平衡二叉搜索树。
```

## 思路

> 二叉树的中序遍历是升序，节点顺序为[左，根，右]

1. 对于给定的数组，根据升序的性质，可知，中间节点为根节点，左半部分为左子树，右半部分为右子树
2. 左半部分也是一颗完整的树，复用1的逻辑，因此用递归即可

```go

// 升序数组是树的中序遍历结果，中间Index就是根，可以递归的还原为一个树
func sortedArrayToBST(nums []int) *TreeNode {
	if len(nums) == 0 {
		return nil
	}
	if len(nums) == 1 {
		return &TreeNode{Val: nums[0]}
	}
	return helper(nums, 0, len(nums)-1)
}

func helper(nums []int, start, end int) *TreeNode {
	if start > end {
		return nil
	}
	// 取得根
	rootIndex := (start + end) / 2
	rootValue := nums[rootIndex]
	root := &TreeNode{Val: rootValue}
	root.Left = helper(nums, start, rootIndex-1)
	root.Right = helper(nums, rootIndex+1, end)
	return root
}

```

