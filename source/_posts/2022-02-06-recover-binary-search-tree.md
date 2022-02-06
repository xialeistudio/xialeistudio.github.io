---
title: LeetCode99——恢复二叉搜索树
date: 2022-02-06 20:24:19
tags:
- tree
categories:
- algorithm
---

## 题目

给你二叉搜索树的根节点 root ，该树中的 恰好 两个节点的值被错误地交换。请在不改变其结构的情况下，恢复这棵树 。

 

**示例 1：**

![img](https://assets.leetcode.com/uploads/2020/10/28/recover1.jpg)

```
输入：root = [1,3,null,null,2]
输出：[3,1,null,null,2]
解释：3 不能是 1 的左孩子，因为 3 > 1 。交换 1 和 3 使二叉搜索树有效。
```

**示例 2：**

![img](https://assets.leetcode.com/uploads/2020/10/28/recover2.jpg)

```
输入：root = [3,1,4,null,null,2]
输出：[2,1,4,null,null,3]
解释：2 不能在 3 的右子树中，因为 2 < 3 。交换 2 和 3 使二叉搜索树有效。
```



来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/recover-binary-search-tree
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

1. 中序遍历构造一个数组，根据二叉搜索树的性质，中序遍历是严格递增的
2. 遍历该数组，找出`后一个值`小于`前一个值`的下标，根据这两个下标访问数组，可以得到两个错误值
3. 遍历二叉树，根据第2步的两个值定位两个二叉树节点
4. 交换两个节点的值

```go
// 1. 中序遍历构造一个数组
// 2. 检查数组顺序，定位有问题的下标
// 3. 中序遍历原来的树，定位指定下标的节点， 交换两个节点值
func recoverTree(root *TreeNode) {
	// 构造数组
	var values []int
	var valueGetter func(root *TreeNode)
	valueGetter = func(root *TreeNode) {
		if root == nil {
			return
		}
		valueGetter(root.Left)
		values = append(values, root.Val)
		valueGetter(root.Right)
	}
	valueGetter(root)
	// 检查数组值顺序，如果比前面的小或者比后面的大
	var (
		wrongIndex1 = -1
		wrongIndex2 = -1
	)
	for i := 0; i < len(values)-1; i++ {
		// 如果比前面的小或者比后面的大
		if values[i+1] < values[i] {
			wrongIndex2 = i + 1
			if wrongIndex1 == -1 {
				wrongIndex1 = i
			} else {
				break
			}
		}
	}
	// 中序遍历，定位到wrongIndex1和wrongIndex2的节点，交换两者的值
	var (
		locator    func(root *TreeNode)
		wrongNode1 *TreeNode
		wrongNode2 *TreeNode
	)
	locator = func(root *TreeNode) {
		if root == nil {
			return
		}
		locator(root.Left)
		if root.Val == values[wrongIndex1] { // 根据值定位节点
			wrongNode1 = root
		} else if root.Val == values[wrongIndex2] {
			wrongNode2 = root
		}
		locator(root.Right)
	}
	locator(root)
	wrongNode1.Val, wrongNode2.Val = wrongNode2.Val, wrongNode1.Val
}
```

