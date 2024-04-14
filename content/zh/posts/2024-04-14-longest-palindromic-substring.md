---
title: 最长回文子串
slug: longest-palindromic-substring
date: 2024-04-14T15:15:26+08:00
categories:
- Algorithm
tags:
- leetcode
featured: true
---

### Question

[https://leetcode.cn/problems/longest-palindromic-substring/description/](https://leetcode.cn/problems/longest-palindromic-substring/description/)

给你一个字符串 `s`，找到 `s` 中最长的回文子串。

&#x20;

**示例 1：**

<pre><code>输入：s = "babad"
<strong>输出：
</strong>"bab"
<strong>解释：
</strong>"aba" 同样是符合题意的答案。
</code></pre>

**示例 2：**

<pre><code>输入：s = "cbbd"
<strong>输出：
</strong>"bb"
</code></pre>

&#x20;

**提示：**

* `1 <= s.length <= 1000`
* `s` 仅由数字和英文字母组成

### Solution

#### 暴力法

> 此解法提交Leetcode会超时

暴力法主要有两个步骤：穷举所有子串和判断子串是否问回文串。

1. 子串的长度从`1...N` ,所有需要一重循环
2. 针对每个长度的子串，我们需要遍历子串起点

```java
lass Solution1 {
        public String longestPalindrome(String s) {
            if (s.length() <= 1) {
                return s;
            }
            int maxLength = 0;
            String maxString = "";
            // 子串长度
            for (int length = 2; length <= s.length(); length++) {
                // 子串起点
                for (int start = 0; start <= s.length() - length; start++) {
                    var end = start + length;
                    var substring = s.substring(start, end);
                    // 如果是回文串且长度大于当前最大的子串长度则更新
                    if (isPalindrome(substring) && substring.length() > maxLength) {
                        maxLength = substring.length();
                        maxString = substring;
                    }
                }
            }
            return maxString;
        }
        
        boolean isPalindrome(String s) {
            var length = s.length();
            for (int i = 0; i < length / 2; i++) {
                if (s.charAt(i) != s.charAt(length - 1 - i)) {
                    return false;
                }
            }
            return true;
        }
    }
```

**时间复杂度**

O(n^3), n是字符串长度，我们有两重循环穷举子串，有一重循环检测是否为回文串。

**空间复杂度**

O(1),需要使用几个固定数量的变量。

#### 动态规划(Dynamic Programing)

对于此类题目，动态规划一般可以用来降维。

根据回文字符串的定义，可以知道字符串的子串是对称的，根据该条件我们可以优化`isPalindrome` 函数的调用。

假设我们使用二维数组dp[start][end]来存储子串s[start,end]是否为回文串，那么需要讨论以下几种情况：

当s[start] = s[end] 时，考虑如下情况：

1. 如果start = end, 则s[start] 和 s[end] 是同一个字符，满足回文串条件；
2. 如果 |start-end|=1 ，则s[start] 和s[end] 相邻，满足回文串条件；
3. 如果|start-end|=2 ，则s[start] 和s[end] 中间隔了一个字符，满足回文串条件；
4. 如果|start-end|>2 ，则需要根据上一个子串s[start-1][end+1] 是否为回文串来确定。

因此状态转移方程如下:


DP(start,end)=\begin{cases} s[start]=s[end], &\text{if } (end-start) \leqslant 2 \\ DP(start-1, end+1) \land s[start]=s[end], &\text{if } (end-start) \gt 2 \end{cases}




```java
class Solution2 {

        public String longestPalindrome(String s) {
            if (s.length() <= 1) {
                return s;
            }
            var maxLength = 1;
            var maxBegin = 0;
            var dp = new boolean[s.length()][s.length()];
            // 初始化DP
            for (int i = 0; i < s.length(); i++) {
                dp[i][i] = true;
            }
            // 遍历子串长度
            for (int length = 2; length <= s.length(); length++) {
                // 遍历起点
                for (int start = 0; start <= s.length() - length; start++) {
                    // 计算结束下标
                    var end = start + length - 1;
                    if (s.charAt(start) != s.charAt(end)) {
                        dp[start][end] = false;
                    } else {
                        // 可以直接得出结论
                        if (end - start <= 2) {
                            dp[start][end] = true;
                        } else { // 需要状态转移
                            dp[start][end] = dp[start + 1][end - 1];
                        }
                    }
                    // 当前子串是回文串而且长度比当前最大长度大，则更新最大长度
                    if (dp[start][end] && (end - start + 1) > maxLength) {
                        maxLength = end - start + 1;
                        maxBegin = start;
                    }
                }
            }
            return s.substring(maxBegin, maxBegin + maxLength);
        }
    }
```

**时间复杂度**

O(n^2)​, n​是字符串长度。

**空间复杂度**

O(n^2), n是字符串长度，需要二维数组存储动态规划状态。

#### 中心扩展法

本题还可以使用中心扩展法解答。

对于字符串`s` 的每个字符`s[i]` 我们考察`s[i-1]` 和`s[i+1]` 是否相等，如果相等，则继续考察前1个和后一个是否匹配，这就是中心扩展法的核心思想。需要注意的是，回文中心有单个字符和两个相同的相邻字符，如`a` 和`aa` 都是有效的回文中心，因此在编码时需要考虑这两种情况并取长度更长的作为当前位置`i` 的最优解。

```java
class Solution3 {

        public String longestPalindrome(String s) {
            if (s.length() <= 1) {
                return s;
            }
            int start = 0;
            int end = 0;
            for (int i = 0; i < s.length(); i++) {
                int len1 = extendCenter(s, i, i); // 中点是同一个字符
                int len2 = extendCenter(s, i, i + 1); // 中点是两个字符
                int len = Math.max(len1, len2);
                if (len > end - start) {
                    start = i - (len - 1) / 2; // 闭区间，所以len-1
                    end = i + len / 2; // 开区间
                }
            }
            return s.substring(start, end + 1);
        }

        private int extendCenter(String s, int start, int end) {
            while (start >= 0 && end < s.length() && s.charAt(start) == s.charAt(end)) {
                start--;
                end++;
            }
            // 此时的start和end满足回文条件，因此需要回退一位才是回文串
            // 起点(start+1), 终点(end-1)
            // 距离公式 (end-1)-(start+1)+1
            // 化简得 end-start-1
            return end - start - 1;
        }
    }
```

需要注意的是在方法`extendCenter` 中，`while` 循环结束后`start` 和`end` 构成的子串一定不是回文串（如果是的话循环还会继续），因此在计算当前`start~end` 的最大回文串长度时需要将`start` 和`end` 进行回退(回退过程见代码注释)。

**时间复杂度**

O(n^2),n字符串长度，外侧需要遍历字符串，内侧有两个while循环调用，总的时间复杂度为O(n*2n)=O(2n^2) ，化简得O(n^2) .

**空间复杂度**

O(1), 需要使用常数项的变量。