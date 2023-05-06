---
title: 解析字符串中的数字
date: 2023-01-03 22:36:49
tags:
- leetcode
- string
categories:
- Algorithm
---

本文分享一种如何在字符串中解析数字的算法。

## 思路

解析字符串中的数字需要判断当前是否是数字字符，以及如何处理连续的数字字符。

本文使用while循环来解析数字，之所以不使用for循环，是笔者认为while循环操控力比for循环要好。

while循环解析方法如下：

1. 如果当前字符是数字，则开启内部while循环
2. 内部while循环退出条件为当前字符不是数字
3. 内部循环操作为读取当前数字，然后加上一个数字乘以10
4. 内部循环退出后，我们就得到一个连续的数字

## 示例

Leetcode [2042. 检查句子中的数字是否递增](https://leetcode.cn/problems/check-if-numbers-are-ascending-in-a-sentence/)

```java
class Solution {

        // 提取字符串中的数字，判断是否严格递增
        public boolean areNumbersAscending(String s) {
            // 定义上一个数字，初始化为最小的数字
            var lastNumber = Integer.MIN_VALUE;
            var i = 0;
            while (i < s.length()) {
                if (Character.isDigit(s.charAt(i))) { // 当前是数字，继续处理
                    var number = 0;
                    // 核心代码
                    while (i < s.length() && Character.isDigit(s.charAt(i))) { // 字符串没越界而且当前字符是数字字符
                        number = number * 10 + (s.charAt(i) - '0'); // (s.charAt(i) - '0') 就是利用ASCII码表直接得到数字值，不需要再做parseInt
                        i++; // 坐标后移
                    }
                    if (number <= lastNumber) { // 如果当前数字<=上一个数字，证明不是严格递增，return false
                        return false;
                    }
                    // number > lastNumber，更新lastNumber
                    lastNumber = number;
                }
                // i后移
                i++;
            }
            return true;
        }
    }
```

**复杂度分析**

时间复杂度：$O(n)$，每个字符访问一次。
空间复杂度:$O(1)$，仅需常数项额外变量。

**注意**

时间复杂度就是分析随着数据量增大，算法执行次数的变化。本题虽然有两重循环，有些同学可能无脑以为时间复杂度是$O(n^2)$，实际上是不对的。可以发现每个字符串最多访问一次，所以复杂度是$O(n)$。
