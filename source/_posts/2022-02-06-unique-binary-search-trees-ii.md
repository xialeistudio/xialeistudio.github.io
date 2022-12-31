---
title: LeetCode95——不同的二叉搜索树 II
date: 2022-02-06 20:24:19
tags:
- tree
- leetcode
categories:
- algorithm
---

## 题目

给你一个整数 `n` ，请你生成并返回所有由 `n` 个节点组成且节点值从 `1` 到 `n` 互不相同的不同 **二叉搜索树** 。可以按 **任意顺序** 返回答案。

**示例 1：**

![img](https://assets.leetcode.com/uploads/2021/01/18/uniquebstn3.jpg)

```
输入：n = 3
输出：[[1,null,2,null,3],[1,null,3,2],[2,1,3],[3,1,null,null,2],[3,2,null,1]]
```

**示例 2：**

输入：n = 1
输出：[[1]]

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/unique-binary-search-trees-ii
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

1. 由于每个节点都可以成为根节点，因此遍历1~n，i为遍历参数名称，此时可以构造如下树
   1. 1~i-1为左子树
   2. i为根节点
   3. i+1~n为右子树
2. 递归的调用步骤1可以得到所有的组合

```go
func generateTrees(n int) []*TreeNode {
	if n == 0 {
		return nil
	}
	return generate(1, n)
}

// 生成start ~ end的数列表
func generate(start, end int) []*TreeNode {
    // 非法条件拦截
	if start > end {
		return []*TreeNode{nil}
	}
	allNodes := []*TreeNode{}
	// 遍历n
	for i := start; i <= end; i++ {
        // start ~ i-1可以构造左子树节点
		leftTrees := generate(start, i-1)
        // i+1 ~ end可以构造右子树节点
		rightTrees := generate(i+1, end)
		for _, left := range leftTrees {
			for _, right := range rightTrees {
                // 组装左根右节点
				root := &TreeNode{Val: i}
				root.Left = left
				root.Right = right
				allNodes = append(allNodes, root)
			}
		}
	}
	return allNodes
}
```

