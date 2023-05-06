---
title: LeetCode98——验证二叉搜索树
date: 2022-02-06 20:24:19
tags:
- tree
- leetcode
categories:
- Algorithm
---

## 题目

给你一个二叉树的根节点 root ，判断其是否是一个有效的二叉搜索树。

**有效** 二叉搜索树定义如下：

节点的左子树只包含 **小于** 当前节点的数。
节点的右子树只包含 **大于** 当前节点的数。
所有左子树和右子树自身必须也是二叉搜索树。

**示例 1：**

![img](https://assets.leetcode.com/uploads/2020/12/01/tree1.jpg)

```
输入：root = [2,1,3]
输出：true
```

**示例 2：**

![img](https://assets.leetcode.com/uploads/2020/12/01/tree2.jpg)

```
输入：root = [5,1,4,null,null,3,6]
输出：false
解释：根节点的值是 5 ，但是右子节点的值是 4 。
```



来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/validate-binary-search-tree
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

## 思路

直接用中序遍历即可。中序遍历可以保证后一个值一定比前一个值大。

中序遍历处理顺序：左->根->右

```go
// 中序遍历，值如果都是升序就满足要求
func isValidBST(root *TreeNode) bool {
  	var (
		lastValue = math.MinInt64 // 上一个值，初始化时保证是最小值即可，这样只要树节点有值就能大于该值
		helper    func(root *TreeNode) bool // 判断指定节点是否大于lastValue
	)
	helper = func(root *TreeNode) bool {
		if root == nil { // 节点为空，直接返回true
			return true
		}
		if !helper(root.Left) { // 如果左子树不满足要求则返回false
			return false
		}
		if root.Val <= lastValue { // 如果当前节点<=上一个节点，则不满足要求（中序遍历本节点一定大于上一个节点）
			return false
		}
		lastValue = root.Val // 更新上一个节点
		if !helper(root.Right) { // 检查右子树
			return false
		}
		return true
	}
	return helper(root)
}
```

