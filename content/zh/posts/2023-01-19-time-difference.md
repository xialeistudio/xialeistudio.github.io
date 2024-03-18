---
slug: time-difference
title: 时间差计算算法
date: 2023-01-19 23:27:14
tags:
- leetcode
categories:
- Algorithm
---

本文分享如何解决计算时间差类的问题。

## 算法

1. 首先需要将时间转化为数字，比如23:59，可以转化为23*60+59
2. 然后根据数字从小到大排序，此时从`[0, n]`处的数据有序，可以遍历该区间计算差值
3. 需要注意的是，由于时间的特殊性，比如`23:59`下一分会归0，因此还需要比如`0`处和`n`处的时间差

## 示例

Leetcode [539. 最小时间差](https://leetcode.cn/problems/minimum-time-difference/)

**代码**

```java
class Solution {

        // 模拟
        // 时间字符串转化为数字
        // 排序，线性遍历，然后再比较第一个和最后一个的差值
        public int findMinDifference(List<String> timePoints) {
            // 24小时总共1440个可能，超过1440，直接返回0（存在重复时间点）
            if (timePoints.size() > 1440) {
                return 0;
            }
            var array = new int[timePoints.size()];
            for (int i = 0; i < timePoints.size(); i++) {
                var str = timePoints.get(i);
                array[i] = Integer.parseInt(str.substring(0, 2)) * 60 + Integer.parseInt(str.substring(3));
            }
            Arrays.sort(array);
            var answer = Integer.MAX_VALUE;
            for (int i = 1; i < array.length; i++) {
                answer = Math.min(answer, array[i] - array[i - 1]);
            }
            // 和首尾差值比较
            return Math.min(answer, array[0] + 1440 - array[array.length - 1]);
        }
}
```

**复杂度分析**

时间复杂度：$O(nlogn)$,$n$是序列长度，主要是排序的时间。

空间复杂度：$O(n)$,$n$是序列长度。
