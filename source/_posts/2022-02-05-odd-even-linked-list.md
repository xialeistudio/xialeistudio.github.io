---
title: LeetCode328——奇偶链表
date: 2022-02-05 20:24:19
tags:
- linklist
- leetcode
categories:
- algorithm
---

## 题目

给定单链表的头节点 head ，将所有索引为奇数的节点和索引为偶数的节点分别组合在一起，然后返回重新排序的列表。

第一个节点的索引被认为是 奇数 ， 第二个节点的索引为 偶数 ，以此类推。

请注意，偶数组和奇数组内部的相对顺序应该与输入时保持一致。

你必须在 O(1) 的额外空间复杂度和 O(n) 的时间复杂度下解决这个问题。

**示例 1:**

![img](https://assets.leetcode.com/uploads/2021/03/10/oddeven-linked-list.jpg)

```
输入: head = [1,2,3,4,5]
输出: [1,3,5,2,4]
```

**示例2:**

![img](https://assets.leetcode.com/uploads/2021/03/10/oddeven2-linked-list.jpg)

```
输入: head = [2,1,3,5,6,4,7]
输出: [2,3,6,7,1,5,4]
```



来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/odd-even-linked-list
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/odd-even-linked-list
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

1. 定义2个链表，`odd为奇数链表`，`even为偶数链表`
2. 遍历原链表，根据奇偶位置插入`odd`或者`even`
3. 连接`odd`和`even`

```go
// 1. 定义以下节点
//    1. 偶链表头节点，移动节点
//    2. 奇链表头结点，移动节点
// 2. 奇链表尾节点.Next = 偶链表头结点
func oddEvenList(head *ListNode) *ListNode {
	// 0,1,2个节点时直接返回
	if head == nil || head.Next == nil || head.Next.Next == nil {
		return head
	}
	var (
		oddHead  *ListNode
		oddMove  *ListNode
		evenHead *ListNode
		evenMove *ListNode
	)
	p := head
	for p != nil {
		// 连接奇数节点
		if oddHead == nil {
			oddHead = p
			oddMove = p
		} else {
			oddMove.Next = p
			oddMove = oddMove.Next
		}
		p = p.Next
		// 连接偶数节点
		if p != nil {
			if evenHead == nil {
				evenHead = p
				evenMove = p
			} else {
				evenMove.Next = p
				evenMove = evenMove.Next
			}
		}
		// 移动到下一个奇数节点
		if p != nil {
			p = p.Next
		}
	}
	// 断开原来的连接
	oddMove.Next = nil
	evenMove.Next = nil

	oddMove.Next = evenHead
	return oddHead
}
```

