---
slug: binary-tree-level-order-traversal-ii
title: LeetCode107——二叉树的层序遍历 II
date: 2022-02-06 20:24:19
tags:
- tree
- leetcode
categories:
- Algorithm
---

## 题目

给你二叉树的根节点 `root` ，返回其节点值 **自底向上的层序遍历** 。 （即按从叶子节点所在层到根节点所在的层，逐层从左向右遍历）

**示例 1：**

![img](https://assets.leetcode.com/uploads/2021/02/19/tree1.jpg)

```
输入：root = [3,9,20,null,null,15,7]
输出：[[15,7],[9,20],[3]]
```

**示例 2：**

```
输入：root = [1]
输出：[[1]]
```

**示例 3：**

```
输入：root = []
输出：[]
```



来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/binary-tree-level-order-traversal-ii
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

直接用层序遍历即可，结果数组翻转之后就是答案

```go
// BFS正向遍历，最后翻转一下最终结果
func levelOrderBottom(root *TreeNode) [][]int {
	if root == nil {
		return [][]int{}
	}
	answers := [][]int{}
	queue := []*TreeNode{root}
	for len(queue) > 0 {
		size := len(queue)
		tmp := queue
		queue = []*TreeNode{} // 清空，存储下一层的节点
		level := []int{}
		for i := 0; i < size; i++ {
			node := tmp[0]
			tmp = tmp[1:]
			level = append(level, node.Val)
			if node.Left != nil {
				queue = append(queue, node.Left)
			}
			if node.Right != nil {
				queue = append(queue, node.Right)
			}
		}
		answers = append(answers, level)
	}
    // 翻转数组
	length := len(answers)
	for i := 0; i < length/2; i++ {
		answers[i], answers[length-1-i] = answers[length-1-i], answers[i]
	}
	return answers
}
```

