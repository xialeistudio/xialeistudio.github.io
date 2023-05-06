---
title: 博耶-摩尔多数投票算法
date: 2022-12-31 14:13:06
tags:
- leetcode
categories:
- Algorithm
---

来自[维基百科](https://zh.m.wikipedia.org/zh-hans/%E5%A4%9A%E6%95%B0%E6%8A%95%E7%A5%A8%E7%AE%97%E6%B3%95)的解释：

> **博耶-摩尔多数投票算法**（英语：Boyer–Moore majority vote algorithm）,中文常作**多数投票算法**、**摩尔投票算法**等，是一种用来寻找一组元素中占多数元素的常数空间级[时间复杂度](https://zh.m.wikipedia.org/wiki/时间复杂度)算法。这一算法由[罗伯特·S·博耶](https://zh.m.wikipedia.org/w/index.php?title=罗伯特·S·博耶&action=edit&redlink=1)（英语：[Robert S. Boyer](https://en.wikipedia.org/wiki/Robert_S._Boyer)）和[J·斯特罗瑟·摩尔](https://zh.m.wikipedia.org/w/index.php?title=J_Strother_Moore&action=edit&redlink=1)（英语：[J Strother Moore](https://en.wikipedia.org/wiki/J_Strother_Moore)）在1981年发表[[1\]](https://zh.m.wikipedia.org/zh-hans/多数投票算法#cite_note-bm-1)，也是[处理数据流](https://zh.m.wikipedia.org/w/index.php?title=Streaming_algorithm&action=edit&redlink=1)（英语：[streaming algorithm](https://en.wikipedia.org/wiki/streaming_algorithm)）的一种典型算法。

简单来说，博耶-摩尔多数投票算法用来寻找数组中的多数元素，相比于用哈希表存储元素和次数使用$O(n)$的时间复杂度来说，该投票算法使用$O(1)$的空间复杂度。

## 算法

摩尔投票算法分为投票-校验两个阶段。投票阶段会统计候选人的票数，遍历数组，如果当前数字和当前候选人不相等，则该候选人票数-1，当候选人票数归0时，需要更换候选人为当前数字；在校验阶段，需要重新遍历数字，并将值等于候选人的数字计数，遍历结束后，比如计数满足要求，则候选人满足要求。

## 举例

比如[A,A, A, B,C]这组元素，我们需要筛选数量超过一半的数字。

首先我们定A为候选人，然后遍历数组，遇到B时A有3个，由于A!=B，因此A结果为2，再和C比较，犹豫A!=C，因此A结尾为1，遍历结束，A是投票阶段的候选人；再遍历数组，统计A的数量为3，超过一半(5/2)，因此A是票数最高的元素。

## 算法题

Leetcode [229. 多数元素 II](https://leetcode.cn/problems/majority-element-ii/)

给定一个大小为 *n* 的整数数组，找出其中所有出现超过 `⌊ n/3 ⌋` 次的元素。

**示例 1：**

```
输入：nums = [3,2,3]
输出：[3]
```

**示例 2：**

```
输入：nums = [1]
输出：[1]
```

**示例 3：**

```
输入：nums = [1,2]
输出：[1,2]
```

 ### 思路

题目要求找出所有出现次数超过`n/3`次的元素，由于摩尔投票算法空间复杂度是常数，因此需要预先定义候选人个数。

设出现次数超过`n/3`次的元素有$x$个，以下是求解$x$的过程：
$$
\begin{equation}\label{eqn:1}
\begin{aligned}
& 假设刚好是n/3个 \\
& \because x * n/3 = n \\
& \therefore x=3 \\
& 而实际上题目要求次数 > n/3 \\
& \therefore x < 3 \\
& \therefore x = 2
\end{aligned}
\end{equation}
$$
所以本题最多能选择2个候选人。

1. 不妨设两个候选人$candidate1$和$candidate2$，$count1$和$count2$都是0
2. 遍历数组，如果当前$nums[i]==candidate1$，则$count1++$，否则$count1--$，对$candidate2$同样处理
3. 如果遍历过程中$count1$或$count2$为0，则更新对应的候选人为$nums[i]$
4. 投票阶段结束，进入重新计数校验阶段，我们留下了$candidate1$和$candidate2$，再次遍历数组，如果值和这两个候选人相同，则对应的$count$增加
5. 如果$count>nums.length/3$，则将当前候选人加入答案

### 代码

```java
class Solution2 {

        // 摩尔投票法
        // 1. 因为题目要求超过 n/3 的数字，因此最多有2个数字
        // 2. 投票阶段，初始化2个数字，以及count
        // 3. 遍历nums，如果和num1相等，则count1++，如果和num2相等，则count2++，否则票数--
        // 4. 如果num1的count1为0，则num1为当前num
        // 5. 校验阶段
        // 6. 统计num1和num2的次数，看看是否>n/3
        public List<Integer> majorityElement(int[] nums) {
            var answer = new ArrayList<Integer>();
            if (nums.length == 0) {
                return Collections.emptyList();
            }
            int candidate1 = nums[0], count1 = 0;
            int candidate2 = nums[0], count2 = 0;
            for (int num : nums) {
                // 增加1的票数
                if (num == candidate1) {
                    count1++;
                    continue;
                }
                // 增加2的票数
                if (num == candidate2) {
                    count2++;
                    continue;
                }
                // 1票数不足，更新候选人1
                if (count1 == 0) {
                    candidate1 = num;
                    count1++;
                    continue;
                }
                // 2票数不足，更新候选人2
                if (count2 == 0) {
                    candidate2 = num;
                    count2++;
                    continue;
                }
                // 票数相减
                count1--;
                count2--;
            }
            count1 = 0;
            count2 = 0;
            for (var num : nums) {
                if (num == candidate1) {
                    count1++;
                } else if (num == candidate2) {
                    count2++;
                }
            }
            if (count1 > nums.length / 3) {
                answer.add(candidate1);
            }
            if (count2 > nums.length / 3) {
                answer.add(candidate2);
            }
            return answer;
        }
    }
```

时间复杂度：$O(n)$, $n$是数组长度，需要遍历两次。

空间复杂度: $O(1)$，只需要常数项额外空间。
