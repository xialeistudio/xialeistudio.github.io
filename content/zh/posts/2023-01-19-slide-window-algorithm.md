---
slug: slide-window-algorithm
title: 滑动窗口算法
date: 2023-01-19 23:16:29
tags:
- leetcode
categories:
- Algorithm
---

滑动窗口算法是查找连续区间常用的算法之一。

本文分享滑动窗口算法的通用框架。

## 算法

1. 定义$left$和$right$双指针，代表窗口的左边界和右边界
2. 当$right$小于给定区间大小时，我们可以进行操作。
3. 在扩大窗口时，需要加当前新加入的数据进行处理
4. 当当前窗口内数据不满足条件时，右移$left$指针缩小窗口
5. 计算$[left,right]$之间的数据，和最佳答案比较并更新最佳答案
6. 右移$right$

下面是滑动窗口通用框架的java语言实现。

```java
int left = 0;
int right = 0;
while(right < 上界) {
  将right处数据加入窗口
  while(窗口数据不符合要求) {
    移除left数据
    left++
  }
  根据当前right和left计算最佳答案并更新
  right++
}
```

## 示例

Leetcode [3. 无重复字符的最长子串](https://leetcode.cn/problems/longest-substring-without-repeating-characters/description/)

**思路**

基于算法框架的思路如下：

1. 定义$left$和$right$双指针，代表窗口的左边界和右边界，再定义`HashMap<Character, Integer>`存储窗口内的字符和数量(可以使用长度为`128`的字符数组代替，省去操作hashmap的开销。
2. 当$right$小于$s.length()$时，我们可以进行操作。
3. 在扩大窗口时，将$s.charAt(right)$加入`HashMap`
4. 当`HashMap.get(s.charAt(right)>1)`，此时$right$处字符重复，需要收缩左边界，$left$处的字符数量-1，右移$left$
5. 计算$[left,right]$之间的数据，和最佳答案比较并更新最佳答案

**代码**

```java
class Solution {
    // 滑动窗口
        // 定义left,right, hashmap<char,int>
        // 循环条件 right<s.length()
        // right字符入map
        // while刚才入的字符重复，map移除left的字符，left++
        // 计算长度
        // right++
        public int lengthOfLongestSubstring(String s) {
            var left = 0;
            var right = 0;
            var answer = 0;
            var map = new int[128];
            while (right < s.length()) {
                var rightChar = s.charAt(right);
                map[rightChar]++;
                // 窗口有重复字符，收缩左边界
                while (map[rightChar] > 1) {
                    var leftChar = s.charAt(left);
                    map[leftChar]--;
                    left++;
                }
                answer = Math.max(answer, right - left + 1);
                right++;
            }
            return answer;
        }
}
```

**复杂度分析**

时间复杂度：$O(n)$, $n$是字符串长度，每个字符至多访问2次。

空间复杂度: $O(1)$，只需常数项空间。
