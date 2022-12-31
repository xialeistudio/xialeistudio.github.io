---
title: LeetCode102--二叉树的层序遍历
tags:
- tree
- leetcode
categories:
- algorithm
---

## 题目

给你二叉树的根节点 `root` ，返回其节点值的 **层序遍历** 。 （即逐层地，从左到右访问所有节点）。	

**示例 1：**

![img](https://assets.leetcode.com/uploads/2021/02/19/tree1.jpg)

```
输入：root = [3,9,20,null,null,15,7]
输出：[[3],[9,20],[15,7]]
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
链接：https://leetcode-cn.com/problems/binary-tree-level-order-traversal
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

层序遍历直接用广度有限遍历即可。

1. 用两个队列存储本层节点`tmp`和下一层节点`queue`（可以简化处理清理，避免一个队列操作时即弹出又插入的问题）
2. 获取队列长度，将`queue`复制到`tmp`,清空本层节点变量(`queue`)
3. tmp不断出队即可，出队时把后代节点插入`queue`

```go
// BFS遍历即可
// 用队列处理，需要注意的是，每次处理一层，每层的大小就是队列的大小，可以准备两个队列，一个用来存储本层，一个用来存储下一层
func levelOrder(root *TreeNode) [][]int {
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
	return answers
}
```

