---
title: LeetCode92——反转链表 II
date: 2022-02-05 19:00:00
tags:
- linklist
categories:
- algorithm
---

## 题目

给你单链表的头指针 head 和两个整数 left 和 right ，其中 left <= right 。请你反转从位置 left 到位置 right 的链表节点，返回 反转后的链表 。


**示例 1：**
![示例1](https://assets.leetcode.com/uploads/2021/02/19/rev2ex2.jpg)

输入：head = [1,2,3,4,5], left = 2, right = 4
输出：[1,4,3,2,5]

**示例 2：**

输入：head = [5], left = 1, right = 1
输出：[5]

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/reverse-linked-list-ii
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

### 转数组
> 大部分的链表题只要未要求原节点上操作，都可以转数组处理，缺点是空间复杂度会额外增加达到O(n)。
1. 将原链表按顺序转为数组
2. 遍历数组，翻转left ~ right之间的数组，此处用双指针即可
   1. 定义left和right指针，交换left和right的值
   2. 两个指针同时向中间移动，left++,right--
3. 将数组构造为链表返回

```go
// 数组法
// 1. 链表转换为数组
// 2. 翻转left ~ right的数据
// 3. 重新构造链表
func reverseBetween(head *ListNode, left int, right int) *ListNode {
	array := convertListToArray(head)
	reverseArrayPart(array, left-1, right-1)
	return buildLinkList(array)
}

// 翻转数组指定区间
func reverseArrayPart(array []int, left, right int) {
	for left < right {
		array[left], array[right] = array[right], array[left]
		left++
		right--
	}
}

// 链表构造为数组
func convertListToArray(head *ListNode) []int {
	array := make([]int, 0)
	for head != nil {
		array = append(array, head.Val)
		head = head.Next
	}
	return array
}
```

### 链表操作

>链表相关的操作主要是要掌握定位任意节点的指针。

1. 定位以下节点
   1.  leftPrev: 翻转区间开始节点的上一个节点，最终要连接翻转后的头节点，所以需要保留
   2. rightNext: 翻转区间结束节点的后一个节点，最终要连接到最终链表，所以需要保留
   3. left和right节点，翻转开始和翻转结束节点
2. 定义子函数翻转left和right，返回right，翻转思路如下
   1. 定义prev和curr指针，prev初始指向null，curr指向head
   2. 开始迭代，迭代结束条件curr不等于rightNode
      1. 保存curr的下一个节点`next:=curr.Next`
      2. 此时我们有3个节点的指针，prev,curr,next
      3. 当前节点指向上一个,`curr.Next=prev`
      4. prev上一个节点指针后移,`prev=curr`
      5. curr后移,`curr=next`
   3. 迭代结束后将`curr`指向上一个节点`curr.Next=prev`
3. 按以下顺序连接所有节点：leftPrev -> right -> left -> rightNext，边界情况如下：
   1. left是头结点，此时leftPrevNode是空，最终结果链表right节点成为新头结点
   2. right是尾节点，此时rightNextNode是空，无需特殊处理
   3. left == right，无需翻转

```go
func reverseBetween(head *ListNode, left int, right int) *ListNode {
	if left == right {
		return head
	}
	leftPrevNode, leftNode, rightNode, rightNextNode := locateNodes(head, left-1, right-1)
	rightNode = reverse(leftNode, rightNode)
	// left是头节点，链表连接顺序，right,left,rightNext
	if leftPrevNode == nil {
		leftNode.Next = rightNextNode
		return rightNode
	}
	// 正常连接，连接顺序 leftPrevNode->right->left->rightNextNode
	leftPrevNode.Next = rightNode
	leftNode.Next = rightNextNode
	return head
}

// 翻转left ~ right之间的节点
// 迭代翻转即可
// p 指向当前节点
// prev 指向上一个节点
// next指向p的next节点
// 如果p == rightNode则结束翻转并返回right
func reverse(leftNode *ListNode, rightNode *ListNode) *ListNode {
	var (
		prev *ListNode
		p    = leftNode
	)
	for p != rightNode {
		next := p.Next
		p.Next = prev // p 指向 上一个节点
		prev = p      // 上一个节点后移
		p = next      // p后移
	}
	// p 此时向rightNode，需要连接p和上一个节点
	p.Next = prev
	return p
}

// 定位
func locateNodes(head *ListNode, left, right int) (*ListNode, *ListNode, *ListNode, *ListNode) {
	var (
		index         = 0
		prevNode      *ListNode
		leftPrevNode  *ListNode
		leftNode      *ListNode
		rightNode     *ListNode
		rightNextNode *ListNode
	)
	for head != nil {
		// 找到左节点
		if index == left {
			leftPrevNode = prevNode
			leftNode = head
		}
		// 找到右节点
		if index == right {
			rightNode = head
			rightNextNode = head.Next
		}
		// 指针移动
		index++
		prevNode = head
		head = head.Next
	}
	return leftPrevNode, leftNode, rightNode, rightNextNode
}
```

