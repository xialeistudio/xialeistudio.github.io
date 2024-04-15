---
title: leetcode热题100(11) - 盛最多水的容器
slug: container-with-most-water
date: 2024-04-15T13:15:26+08:00
categories:
- Algorithm
tags:
- leetcode

featured: true
---

### Question

[https://leetcode.cn/problems/container-with-most-water/?favorite=2cktkvj](https://leetcode.cn/problems/container-with-most-water/?favorite=2cktkvj)



给定一个长度为 `n` 的整数数组 `height` 。有 `n` 条垂线，第 `i` 条线的两个端点是 `(i, 0)` 和 `(i, height[i])` 。

找出其中的两条线，使得它们与 `x` 轴共同构成的容器可以容纳最多的水。

返回容器可以储存的最大水量。

**说明：**你不能倾斜容器。

&#x20;

**示例 1：**

![](https://aliyun-lc-upload.oss-cn-hangzhou.aliyuncs.com/aliyun-lc-upload/uploads/2018/07/25/question\_11.jpg)

<pre><code>输入：[1,8,6,2,5,4,8,3,7]
<strong>输出：
</strong>49 
<strong>解释：
</strong>图中垂直线代表输入数组 [1,8,6,2,5,4,8,3,7]。在此情况下，容器能够容纳水（表示为蓝色部分）的最大值为 49。
</code></pre>

**示例 2：**

<pre><code>输入：height = [1,1]
<strong>输出：
</strong>1
</code></pre>

&#x20;

**提示：**

* `n == height.length`
* `2 <= n <= 105`
* `0 <= height[i] <= 104`

### Solution

#### 双指针

本题要求容纳最大的水量，实际上就是求两根线之间的最大面积。

在本题中，宽就是两条线的距离，高就是两条线中`矮` 的那条，因此我们可以考虑使用双指针法，左指针`l`指向0，右指针`r`指向`nums.length-1` ，此时的面积为: \min(nums[l],nums[r])*(r-l) ，我们可以将`l` 右移或者`r` 左移。

那么什么时候右移`l` ，什么情况下左移`r` 呢？不管是`l` 还是`r`在移动过程中，`宽(r-l)` 是减小的，而要保证宽度减少的情况下，面积还能增大，我们只能移动`矮` 的那条线，这样如果矮的那条线移动之后能变大，面积才有可能变大。因此每次循环我们都需判断`l` 和`r` 的大小，移动`矮` 的那条线，当`l` 和`r` 重合时，循环结束。

```java
static class Solution1 {

        public int maxArea(int[] height) {
            if (height.length == 0) {
                return 0;
            }
            int answer = 0;
            int l = 0;
            int r = height.length - 1;
            while (l < r) {
                int area = Math.min(height[l], height[r]) * (r - l); // 计算面积
                answer = Math.max(answer, area);

                // 矮的边移动
                if (height[l] < height[r]) {
                    l++;
                } else {
                    r--;
                }
            }
            return answer;
        }
    }
```

**时间复杂度**

O(n), n数组长度，我们需要依次访问每一个元素。

**空间复杂度**

O(1),需使用固定的几个变量。