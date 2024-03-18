---
slug: leetcode-median-of-two-sorted-arrays
title: leetcode(4)——寻找两个有序数组的中位数
date: 2019-09-20 18:34:58
categories:
- Algorithm
tags:
- leetcode
---

本文是力扣算法的第四篇，讲解寻找两个有序数组的中位数。

## Question

> 给定两个大小为 m 和 n 的有序数组 `nums1` 和 `nums2`。
>
> 请你找出这两个有序数组的中位数，并且要求算法的时间复杂度为 O(log(m + n))。
>
> 你可以假设 `nums1` 和 `nums2` 不会同时为空。

**示例 1:**

```
nums1 = [1, 3]
nums2 = [2]

则中位数是 2.0
```

**示例 2:**

```
nums1 = [1, 2]
nums2 = [3, 4]

则中位数是 (2 + 3)/2 = 2.5
```

## 中位数

> 中位数是按顺序排列的一组数据中居于中间位置的数，即在这组数据中，有一半的数据比他大，有一半的数据比他小。

## 暴力法

> 1. 将两个有序数组合并成一个有序数组
>
> 2. 如果长度是奇数则返回中间的值，如果是否则则返回中间两个数的平均值。

```javascript
var findMedianSortedArrays = function (nums1, nums2) {
    const nums = [];
    let p1 = p2 = 0;
    while (p1 < nums1.length && p2 < nums2.length) {
        if (nums1[p1] < nums2[p2]) {
            nums.push(nums1[p1++]);
        } else if (nums1[p1] > nums2[p2]) {
            nums.push(nums2[p2++]);
        } else {
            nums.push(nums1[p1++]);
            nums.push(nums2[p2++]);
        }
    }
    if (p1 !== nums1.length) { // nums2比nums1长度要短，导致nums1没有走到末尾
        for (; p1 < nums1.length; p1++) {
            nums.push(nums1[p1]);
        }
    }
    if (p2 !== nums2.length) { // nums1比nums2长度要短，导致nums2没有走到末尾
        for (; p2 < nums2.length; p2++) {
            nums.push(nums2[p2]);
        }
    }
    if (nums.length % 2 === 0) { // 长度为偶数
        return (nums[nums.length / 2] + nums[nums.length / 2 - 1]) / 2
    }
    return nums[Math.floor(nums.length / 2)];
}
```

时间复杂度 $O(m+n)$

> 同时遍历了数组1和数组2

空间复杂度$O(m+n)$

> 声明了新数组，长度为数组1的长度加数组2的长度

提交完通过了，这道题定义为Hard是不是搞错了，明明是个Easy题。

如果你这么想那你可能漏了一个时间复杂度的要求：$O(log(m+n))$

## 思考 && 规律

> 一般来说看到$O(log)$ 级别的时间复杂度一般是跟二分有关的算法才会产生这个时间复杂度，所以我们不妨以二分的思想来重新考虑一下这个问题。
>
> 有序数组求中位数，一般化为就两个有序数组的第$k$个数，本问题中$k = (m+n)/2$时就是我们的答案。

怎么求第$k$个数？

>  我们可以现在数组1和数组2中求出$k/2$个数$a$和$b$，如果$a < b$，那说明$k$个数位于数组1的`后半段`或和数组2的`前半段`之间。我们把不符合规则的数组1`前半段`和数组2`后判断`给舍弃即可，这就只处理了一般的数据，达到的二分的目的。之后按照这个原则递归处理即可

```javascript
var findMedianSortedArrays = function (nums1, nums2) {
    const m = nums1.length;
    const n = nums2.length;

    // 如果第1个数组为空，直接返回第2个数组的数据即可
    if (m === 0) {
      	// 第2个数组长度为偶数，返回中间两个数字的平均值
        if (n % 2 === 0) {
            return (nums2[nums2.length / 2] + nums2[nums2.length / 2 - 1]) / 2;
        }
      	// 第2个数组长度为奇数，返回中间两个数字的平均值
        return nums2[Math.floor(nums2.length / 2)];
    }

    if (n === 0) {
        if (m % 2 === 0) {
            return (nums1[nums1.length / 2] + nums1[nums1.length / 2 - 1]) / 2;
        }
        return nums1[Math.floor(nums1.length / 2)];
    }

  	// 总长度
    const total = m + n;
    // 总数为奇数，找到第total/2+1个数（下标从1开始）
    if (total % 2 === 1) {
        return findKth(nums1, 0, nums2, 0, Math.floor(total / 2) + 1);
    }
    // 下标为偶数，找到中间的两个数
    return (
        findKth(nums1, 0, nums2, 0, Math.floor(total / 2)) +
        findKth(nums1, 0, nums2, 0, Math.floor(total / 2) + 1)
    ) / 2
}

// 找到两个有序数组的第k大的值
function findKth(nums1, aBegin, nums2, bBegin, k) {
  	// 如果数组1的下标或者数组2的下标超过各自的数组长度，k就是另一个数组的第k个数
    if (aBegin >= nums1.length) {
        return nums2[bBegin + k - 1];
    }
    if (bBegin >= nums2.length) {
        return nums1[aBegin + k - 1];
    }
    if (k === 1) {
        return Math.min(nums1[aBegin], nums2[bBegin]);
    }

    let midA = Number.MAX_VALUE;
    let midB = Number.MAX_VALUE;

  	// 如果数组1的第k/2个数没有越界
    if (aBegin + Math.floor(k / 2) - 1 < nums1.length) {
        midA = nums1[aBegin + Math.floor(k / 2) - 1];
    }
    if (bBegin + Math.floor(k / 2) - 1 < nums2.length) {
        midB = nums2[bBegin + Math.floor(k / 2) - 1];
    }
  	// 如果数组1的第k/2个数小于数组2的k/2个数，表示总的第k个数在数组1后判断和数组2的前半段
    // 所以数组1的下标需要往后走k/2个位置，响应的数组b的下标往前走k/2个位置
    if (midA < midB) {
        return findKth(nums1, aBegin + Math.floor(k / 2), nums2, bBegin, k - Math.floor(k / 2));
    }
    return findKth(nums1, aBegin, nums2, bBegin + Math.floor(k / 2), k - Math.floor(k / 2));
}
```

时间复杂度$O(log(m+n))$

> 每次递归都舍弃了一半数据，二分的复杂度是$log$

空间复杂度$O(1)$

> 只使用了固定的几个临时变量

## 结尾

本问题考察的是对二分法的基本功，面试中后期遇到的可能性比较大，可以多加熟悉。