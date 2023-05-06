---
title: LeetCode103——二叉树的锯齿形层序遍历
date: 2022-02-06 20:24:19
tags:
- tree
- leetcode
categories:
- Algorithm
---

## 题目

给你二叉树的根节点 `root` ，返回其节点值的 **锯齿形层序遍历** 。（即先从左往右，再从右往左进行下一层遍历，以此类推，层与层之间交替进行）。

**示例 1：**

![img](https://assets.leetcode.com/uploads/2021/02/19/tree1.jpg)

```
输入：root = [3,9,20,null,null,15,7]
输出：[[3],[20,9],[15,7]]
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
链接：https://leetcode-cn.com/problems/binary-tree-zigzag-level-order-traversal
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

用层序遍历的思路即可，不过偶数行需要将该行的值翻转。

```go
// BFS处理，记录遍历层数，当层数是奇数，翻转下本层元素
func zigzagLevelOrder(root *TreeNode) [][]int {
	if root == nil {
		return [][]int{}
	}
	answers := [][]int{}
	queue := []*TreeNode{root}
	for level := 1; len(queue) > 0; level++ {
		size := len(queue)
		tmp := queue
		queue = []*TreeNode{} // 清空，存储下一层的节点
		vals := []int{}
		for i := 0; i < size; i++ {
			node := tmp[0]
			tmp = tmp[1:]
			vals = append(vals, node.Val)
			if node.Left != nil {
				queue = append(queue, node.Left)
			}
			if node.Right != nil {
				queue = append(queue, node.Right)
			}
		}
		if level%2 == 0 { // 偶数行，翻转vals
			length := len(vals)
			for i := 0; i < length/2; i++ {
				vals[i], vals[length-1-i] = vals[length-1-i], vals[i] // length-1是结束下标，-i就是同步往左逼近
			}
		}
		answers = append(answers, vals)
	}
	return answers
}
```

