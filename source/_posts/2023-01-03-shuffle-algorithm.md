---
title: 洗牌算法
date: 2023-01-03 12:05:44
tags:
- leetcode
categories:
- algorithm
---

洗牌算法用来将给定的序列打乱，可以认为是排序的反操作。

## 正确性判断

对于包含$n$个元素的序列，其全排列有$n!$种。如果**序列打乱的结果为$n!$种且每种序列出现的概率相同**，则是正确的洗牌算法。

## Fisher–Yates 洗牌算法

> 以下算法说明摘自: https://gaohaoyang.github.io/2016/10/16/shuffle-algorithm/
>
> Fisher–Yates shuffle 的原始版本，最初描述在 1938 年的 Ronald Fisher和 Frank Yates 写的书中，书名为《Statistical tables for biological, agricultural and medical research》。他们使用纸和笔去描述了这个算法，并使用了一个随机数表来提供随机数。它给出了 1 到 N 的数字的的随机排列，具体步骤如下：
>
> 1. 写下从 1 到 N 的数字
> 2. 取一个从 1 到剩下的数字（包括这个数字）的随机数 k
> 3. 从低位开始，得到第 k 个数字（这个数字还没有被取出），把它写在独立的一个列表的最后一位
> 4. 重复第 2 步，直到所有的数字都被取出
> 5. 第 3 步写出的这个序列，现在就是原始数字的随机排列
>
> 已经证明如果第 2 步取出的数字是真随机的，那么最后得到的排序一定也是。

## 正确性证明

正确的洗牌算法要保证每个数字出现在每个位置的概率一样。我们来看看Fisher–Yates洗牌算法是否正确。

假设现在有1,2,3,4,5五个数字。

1. 首先在`1-5`随机一个数，假设是`4`，随机概率为`1/5`
2. 再次从`1,2,3,5`中随机一个数，假设是`5`，随机概率为`1/4`，但是`5`在第一步没被选上的概率是`4/5`，因此总体概率是`1/4*4/5`还是`1/5`

## 代码

```java
public void shuffle(int[] nums) {
	var n = nums.length;
  for (int i = 0; i < n; i++) {
  	int newIndex = i + random.nextInt(n - i); // 在i之后的下标随机，可以保证不会随机到i前面的
    int temp = nums[i];
    nums[i] = nums[newIndex];
    nums[newIndex] = temp;
  }
}
```

时间复杂度: $O(n)$，$n$是数组长度，只需要遍历一次。

空间复杂度：$O(1)$，仅需常数项空间。

