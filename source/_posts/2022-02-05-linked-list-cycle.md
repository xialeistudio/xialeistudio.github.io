---
title: LeetCode141——环形链表
date: 2022-02-05 20:09:35
tags:
- linklist
categories:
- algorithm
---

## 题目

给你一个链表的头节点 head ，判断链表中是否有环。

如果链表中有某个节点，可以通过连续跟踪 next 指针再次到达，则链表中存在环。 为了表示给定链表中的环，评测系统内部使用整数 pos 来表示链表尾连接到链表中的位置（索引从 0 开始）。注意：pos 不作为参数进行传递 。仅仅是为了标识链表的实际情况。

如果链表中存在环 ，则返回 true 。 否则，返回 false 。

**示例 1：**

![img](https://assets.leetcode-cn.com/aliyun-lc-upload/uploads/2018/12/07/circularlinkedlist.png)

```
输入：head = [3,2,0,-4], pos = 1
输出：true
解释：链表中有一个环，其尾部连接到第二个节点。
```

**示例 2：**

![img](https://assets.leetcode-cn.com/aliyun-lc-upload/uploads/2018/12/07/circularlinkedlist_test2.png)

```
输入：head = [1,2], pos = 0
输出：true
解释：链表中有一个环，其尾部连接到第一个节点。
```



来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/linked-list-cycle
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

### 哈希表法

利用哈希表存储访问过的节点，如果遍历时节点在哈希表，则有环。

> Go语言中map的value为struct可以不占用存储空间。

```go
func hasCycle(head *ListNode) bool {
    m := map[*ListNode]struct{}{}
    for head != nil {
        if _, ok := m[head]; ok {
            return true
        }
        m[head] = struct{}{}
        head = head.Next
    }
    return false
}
```

### 快慢指针法

1. 快指针每次走两步，慢指针走一步，如果相遇则存在环

```go
func hasCycle(head *ListNode) bool {
	if head == nil || head.Next == nil {
		return false
	}
	fast := head
	slow := head
	for fast != nil {
		slow = slow.Next
		fast = fast.Next // 快指针走1步
		if fast != nil {
			fast = fast.Next // 快指针再走1步
		}
		if fast == slow { // 相遇了
			return true
		}
	}
	return false
}
```

