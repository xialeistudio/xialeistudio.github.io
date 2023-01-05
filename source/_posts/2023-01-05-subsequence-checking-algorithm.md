---
title: 字符串子序列检测算法
date: 2023-01-05 12:36:10
tags:
- leetcode
- string
categories:
- algorithm
---

本文分享一种检测一个字符串是否为另一个字符串子序列的算法。

子序列的定义：

若字符串$s1$可以由字符串$s2$删除某些字符得到，则$s1$是$s2$的子序列。换句话说，若$s1$的所有字符都在$s2$中且顺序一致，则$s1$是$s2$的子序列。

例如：

a是aaa的子序列，adf是abcdef的子序列，但是cba不是abc的子序列（因为字符顺序变了）。

## 算法

1. 声明$s1$的下标变量$strIndex$，若$s2$有$s1$的该字符，则$strIndex+1$
2. 若遍历过程中$strIndex$和$s1$的长度相等，则证明$s1$所有字符都在$s2$中，返回$s1$是$s2$在子序列
3. 遍历结束仍未返回，证明$s1$不是$s2$的子序列

## 代码

```java
class Solution {
  public boolean isSubsequent(String str, String str1) {
            var strIndex = 0;
            // 逐字符遍历
            // 如果字符想通，则strIndex++
            // 如果strIndex到达末尾，则证明str是子序列
            for (var i = 0; i < str1.length(); i++) {
                if (str.charAt(strIndex) == str1.charAt(i)) {
                    strIndex++;
                }
                if (strIndex == str.length()) {
                    return true;
                }
            }
            return false;
        }
}
```

**复杂度分析**

时间复杂度：$O(n)$,$n$是$str1$的长度。

空间复杂度：$O(1)$。
