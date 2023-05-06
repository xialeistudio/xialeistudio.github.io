---
title: LeetCode142——环形链表2
date: 2022-02-05 20:14:56
tags:
- linklist
- leetcode
categories:
- Algorithm
---

## 题目

给定一个链表，返回链表开始入环的第一个节点。 如果链表无环，则返回 null。

如果链表中有某个节点，可以通过连续跟踪 next 指针再次到达，则链表中存在环。 为了表示给定链表中的环，评测系统内部使用整数 pos 来表示链表尾连接到链表中的位置（索引从 0 开始）。如果 pos 是 -1，则在该链表中没有环。注意：pos 不作为参数进行传递，仅仅是为了标识链表的实际情况。

不允许修改 链表。

 

**示例 1：**

![img](https://assets.leetcode-cn.com/aliyun-lc-upload/uploads/2018/12/07/circularlinkedlist.png)

```
输入：head = [3,2,0,-4], pos = 1
输出：返回索引为 1 的链表节点
解释：链表中有一个环，其尾部连接到第二个节点。
```

**示例 2：**

![img](https://assets.leetcode-cn.com/aliyun-lc-upload/uploads/2018/12/07/circularlinkedlist_test2.png)

```
输入：head = [1,2], pos = 0
输出：返回索引为 0 的链表节点
解释：链表中有一个环，其尾部连接到第一个节点。
```

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/linked-list-cycle-ii
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

### 哈希表

参考上一篇[环形链表](/2022/02/05/linked-list-cycle.md)，可以利用哈希表存储节点，当再次遇到该节点时，该节点就是成环点。

```go
// 1. 遍历节点存入map
// 2. 如果节点已存在，则该节点是成环节点
func detectCycle(head *ListNode) *ListNode {
	m := make(map[*ListNode]struct{})
	p := head
	for p != nil {
		if _, ok := m[p]; ok {
			return p
		}
		m[p] = struct{}{}
		p = p.Next
	}
	return nil
}
```

### 快慢指针

1. 快指针走2步，慢指针走1步
2. 快慢指针相遇时，慢指针走了`s`个节点，快指针走了`2s`，同时快指针比慢指针多走了`N`圈，设环形区间长度为`b`,因此`2s = s+nb`，因此`s=nb`，也就是快慢指针相遇时慢指针走过的距离刚好是环的倍数。
3. 新起指针指向头结点，和慢指针一起向后走，两点相遇时新指针走了a，慢指针走了a+nb，此时新指针和慢指针相遇，新指针指向成环点

```go
func detectCycle(head *ListNode) *ListNode {
	if head == nil || head.Next == nil {
		return nil
	}
	fast := head
	slow := head
	for fast != nil {
		slow = slow.Next
		fast = fast.Next
		if fast != nil {
			fast = fast.Next
		}
		if fast == slow {
			// 快慢相遇，新起指针指向节点，然后和慢指针一起走，两者相遇点就是成环点
			ptr := head
			for ptr != slow {
				ptr = ptr.Next
				slow = slow.Next
			}
			return ptr
		}
	}
	return nil
}
```

