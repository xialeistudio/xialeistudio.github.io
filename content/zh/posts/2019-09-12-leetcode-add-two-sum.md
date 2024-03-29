---
slug: leetcode-add-two-sum
title: leetcode(2) —— 两数相加
date: 2019-09-12 23:16:28
categories:
- Algorithm
tags:
- leetcode
---

本文是力扣算法的第二篇，讲解两数相加问题。

## Question

> 给出两个 **非空** 的链表用来表示两个非负的整数。其中，它们各自的位数是按照 **逆序** 的方式存储的，并且它们的每个节点只能存储 **一位** 数字。
>
> 如果，我们将这两个数相加起来，则会返回一个新的链表来表示它们的和。
>
> 您可以假设除了数字 0 之外，这两个数都不会以 0 开头。

**示例：**

```text
输入：(2 -> 4 -> 3) + (5 -> 6 -> 4)
输出：7 -> 0 -> 8
原因：342 + 465 = 807
```

## 分析

遍历两个链表把值加起来好之后插入链表，如果有进位的话需要把进位的值保存到后面的节点上，如果遍历完毕之后还剩下需要进位的值，那么需要插入末尾新节点。

### 边界情况

遇到链表相关的题目时一定要处理好边界情况，因为有些为空的链表或者只有1个节点的链表没有处理的必要，及时返回可以降低算法复杂度。

1. 链表1和链表2同时为空，直接返回undefined即可
2. 链表1为空，返回链表2
3. 链表2为空，返回链表1

## 解题方法

```javascript
// 链表节点定义
function ListNode(val) {
  this.val = val;
  this.next = null;
}

function addTwoNumbers(l1, l2) {
  if(!l1 && !l2) { // 链表1和链表2同时为空，无需任何处理
    return;
  }
  if(!l1) { // 链表1为空，直接返回链表2
    return l2;
  }
  if(!l2) { // 链表2为空，直接返回链表1
    return l1;
  }
  
  let carry = 0; // 进位值
  let head = new ListNode(0); // 链表头节点
  let p = head; // 链表移动指针
  
  while(l1 || l2 || carry > 0) { // l1和l2虽然不会同时为空，但是存在l1和l2长度不一致的情况， 这种也需要处理
    let sum = carry; // sum为本节点的值，需要加上前一个节点的进位值
    if(l1) {
     sum += l1.val; // 把链表1当前节点的值加上
     l1 = l1.next; // 移动链表1指针
    }
    if(l2) {
      sum += l2.val;
      l2 = l2.next;
    }
    
    if(sum >= 10) { // 两个个位数相加最大值为18，所以到下一个节点进位的最大值为1
      carry = 1;
      sum -= 10; // 去掉十位，保留个位为节点最终值
    } else {
      carry = 0; // 相加之后和小于10，不需要进位，清除进位数据，否则死循环
    }
    
    p.next = new ListNode(sum); // 插入新节点
    p = p.next; // 新链表指针后移
  }
  
  return head.next; // 头结点的值不是相加得到的，所以需要后移一个节点返回由两个链表加起来的结果
}
```

进位的处理搞清楚之后这道题就清楚了。

时间复杂度O(max(l1.length, l2.length))

> 　循环次数的根据链表1和链表2中长的那个链表来的，因为要保证两个链表的所有节点都被便利到

空间复杂度O(max(l1,l2))

> 最终链表的节点数也是根据链表1和链表2中长的那个链表来的，因为要保证两个链表的所有节点都被便利到，如果最后有进位的话，结果链表的长度会比链表1和链表2中长的链表大小+1。

## 结尾

这道题的难度是中等，但是摸清楚链表的基本操作之后，应该没什么问题就能解决。