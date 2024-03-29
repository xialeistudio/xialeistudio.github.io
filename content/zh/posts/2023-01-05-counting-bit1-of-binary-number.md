---
slug: counting-bit1-of-binary-number
title: 计算数字二进制位中1的个数
date: 2023-01-05 12:35:00
tags:
- leetcode
categories:
- Algorithm
---

本文分享一种计算给定数字二进制表示中有多少个1的算法。

位运算对于非硬件相关的开发者来说可能用的比较少，朴素做法是将数字转换为二进制字符串，然后遍历该字符串得到1的个数。

## 算法

1. 通过右移我们可以访问到数字的指定比特
2. 将该比特与1进行按位与`&`，结果为1则证明当前比特位是1，计数器+1

根据给定数字的数据类型可以确定需要位移的次数，对于`int`来说，4个字节，因此需要右移32次，而对于`long`来说，8个字节，需要右移64次。

## 代码

```java
class Solution {
  public int getBit1Count(int num) {
              var count = 0;
              for (int i = 0; i < 32; i++) {
                  if (((num >> i) & 1) == 1) {
                      count++;
                  }
              }
              return count;
  }
}
```

**复杂度分析**

时间复杂度：$O(1)$，不管多大的数字，只需要右移32次。

空间复杂度：$O(1)$，无需额外空间。
