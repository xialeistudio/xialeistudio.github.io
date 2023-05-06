---
title: 查找第N大的数
date: 2023-01-03 12:22:08
tags:
- leetcode
categories:
- Algorithm
---

在给定的序列中查找第N大的数，朴素做法是对序列排序，然后根据索引直接查询，时间复杂度为$O(nlogn)$。

本文介绍一种在$O(n)$的时间复杂度查询第N大的数的算法。

## 算法

算法思路就是定义标志变量，然后遍历数组，根据标志变量和当前数组变量的大小更新标志变量，最后根据情况返回标志变量。

## 示例：查找第2大的数

定义$first$和$second$分别存储最大和次大，然后遍历数组时更新即可。

```java

/**
 * 查找第二大的数字
 */
public class SecondMaximumNumber {

    public int secondMaximumNumber(int[] nums) {
        // 最大数
        var first = Integer.MIN_VALUE;
        // 次大数
        var second = Integer.MIN_VALUE;
        for (var num : nums) {
            // 当前数字比最大数还大，最大数更新为当前数字，原来的最大数更新为第2大
            if (num >= first) {
                second = first;
                first = num;
            } else if (num >= second) { // 当前数字小于最大，但是大于第2大，更新第2大
                second = num;
            }
        }
        return second;
    }

    public static void main(String[] args) {
        var nums = new int[]{1, 3, 2, 8, 5};
        var s = new SecondMaximumNumber();
        System.out.println(s.secondMaximumNumber(nums));
    }
}

```

## 示例：查找第3大的数

Leetcode: [第三大的数](https://leetcode.cn/problems/third-maximum-number/)

原理和查第2大的数想通，定义$first$,$second$,$third$三个变量，然后遍历$nums$

1. 若$num > first$，则$second$赋值给$third$，$first$赋值给$second$,$num$赋值给$first$
2. 若$num < first$且 $num > second$，则$second$赋值给$third$，$num$赋值给$second$
1. 若$num < second$且$num > third$，则$num$赋值给$third$

最后根据题意返回$third$或者$first$即可。

```java
class Solution3 {

        // 三个变量
        public int thirdMax(int[] nums) {
            var first = Long.MIN_VALUE;
            var second = first;
            var third = second;
            for (var num : nums) {
                if (num > first) { // 如果num>最大值，原来的最大变次大，原来的次大变三大, 当前边最大
                    third = second;
                    second = first;
                    first = num;
                } else if (num < first && num > second) { // 小于最大，但是大于第二, 第二变第三，当前边第二
                    third = second;
                    second = num;
                } else if (num < second && num > third) { // 小于第二，但是大于第三
                    third = num;
                }
            }
            return (int) (third == Long.MIN_VALUE ? first : third);
        }
    }
```

时间复杂度:$O(n)$，$n$是数组长度，仅需遍历一次。

空间复杂度: $O(1)$，仅需使用3个变量。
