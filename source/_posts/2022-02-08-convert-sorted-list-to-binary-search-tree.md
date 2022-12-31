---
title: LeetCode109——有序链表转换二叉搜索树
date: 2022-02-08 20:24:19
tags:
- tree
- leetcode
categories:
- algorithm
---

## 题目

给定一个单链表，其中的元素按升序排序，将其转换为高度平衡的二叉搜索树。

本题中，一个高度平衡二叉树是指一个二叉树每个节点 的左右两个子树的高度差的绝对值不超过 1。

**示例:**

```
给定的有序链表： [-10, -3, 0, 5, 9],

一个可能的答案是：[0, -3, 9, -10, null, 5], 它可以表示下面这个高度平衡二叉搜索树：

      0
     / \
   -3   9
   /   /
 -10  5
```

## 思路

### 转换为数组

> 转换为数组后解法跟前面一道题一样。

```go

// 链表转换为数组，复用108解法
func sortedListToBST(head *ListNode) *TreeNode {
	if head == nil {
		return nil
	}
	list := listToArray(head)
	return helper(list, 0, len(list)-1)
}

func listToArray(head *ListNode) []int {
	result := []int{}
	for head != nil {
		result = append(result, head.Val)
		head = head.Next
	}
	return result
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

### 链表操作

> 我们遍历到中间节点后，将链表拆分为[左部分，中间点，右部分]即可复用逻辑，而且无额外空间占用

单链表是无法直到中间点在哪里的，因此我们需要先遍历一次，获取链表长度，除以2就是中间的index。

```go
// 1. 遍历一遍链表得到链表长度，算出中间节点index
// 2. 再次遍历链表，拆分为三段
// 1. 起点到中间节点的上一个节点：左子链表
// 2. 中间节点
// 3. 中间节点的下一个节点到链表末尾：右子链表
// 3. 将中间节点作为树根，利用左右子链表，递归构建左右子树，然后挂到根节点
func sortedListToBST(head *ListNode) *TreeNode {
	if head == nil {
		return nil
	}
	return helper(head)
}


func helper(head *ListNode) *TreeNode {
	if head == nil {
		return nil
	}
	if head.Next == nil {
		return &TreeNode{Val: head.Val}
	}
	// 获取链表总长度
	length := 0
	p := head
	for p != nil {
		length++
		p = p.Next
	}
	middle := length / 2 // 取得中间点位置
	// 再次遍历到中间点
	var (
		prev = head      // 指向中间点的上一个节点
		curr = head.Next // 指向中间点
	)
	var (
		left  *ListNode // 左子链表头结点
		right *ListNode // 右子链表头结点
	)
	index := 0
	for curr != nil {
		// index是prev的下标，因此定位到middle的前一个
		if index == middle-1 {
			// 找到中点，将中点和右子链表连接打断
			right = curr.Next
			curr.Next = nil
			// 将左子链表和中点连接打断
			prev.Next = nil
			left = head
			break
		}
		prev = curr
		curr = curr.Next
		index++
	}
	// 此时我们拥有left,curr,right 三个链表，开始递归组合
	root := &TreeNode{Val: curr.Val}
	root.Left = helper(left) // 给你一条链表，给我构建一个树出来
	root.Right = helper(right)
	return root
}
```

