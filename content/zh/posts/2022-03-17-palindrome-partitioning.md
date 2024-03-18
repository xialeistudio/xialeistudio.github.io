---
slug: palindrome-partitioning
title: 算法篇-leetcode 131 分割回文串
date: 2022-03-17 12:00:14
tags:
- binarysearch
- leetcode
categories:
- Algorithm
---

## 题目

给你一个字符串 `s`，请你将 `s` 分割成一些子串，使每个子串都是 **回文串** 。返回 `s` 所有可能的分割方案。

**回文串** 是正着读和反着读都一样的字符串。

**示例1**

```
输入：s = "aab"
输出：[["a","a","b"],["aa","b"]]
```

## 解答

**题目要求**

1. 将字符串字符打散后，将其中的回文串添加到一个单独的List
2. 第1步的所有List构成最后的答案

可以看出，这是一个典型的回溯问题，考察有多少种方法可以组装最后的答案。

#### 方法一：直接回溯

**思路及算法**

回溯需要回答以下3个问题：
1. 回溯终止条件是什么？
2. 回溯有哪些选择?
3. 如何进入下一个选择？

对于本题来说，我们需要将字符串打散，从中选择回文串添加到最终答案，因此，需要定义以下变量:  
1. $index$, 记录当前选择的字符索引
2. $path$, 记录本次回文串选择情况
3. $answer$, 记录最终答案

回答上面提出来的两个问题：
1. 回溯终止条件: $index==s.length()$，此时将$path$拷贝到$answer$，不可以直接添加，因为回溯存在撤回操作，必须断开$answer$和$path$的引用。
2. 回溯有哪些选择：定义变量$right$, 遍历 $s[index,s.length())$，当$s[index,right]$是回文串时，将其加入$path$。
3. 如何进入下一个选择：第2个问题满足条件的情况下，增加$index$然后再次递归即可。

```java
class Solution {

    /**
     * DFS回溯
     * 1. 回溯出口      index == s.length()
     * 2. 回溯递进      遍历[i,n)  如果s[i,j] 是回文串，则加入path，然后递归 s[i,j+1]
     *
     * @param s
     * @return
     */
    public List<List<String>> partition(String s) {
        List<List<String>> answer = new ArrayList<>();
        List<String> path = new ArrayList<>();
        dfs(answer, path, 0, s.length(), s);
        return answer;
    }

    private void dfs(List<List<String>> answer, List<String> path, int index, int length, String s) {
        if (index == length) {
            answer.add(new ArrayList<>(path));
            return;
        }
        // 本次有什么选择?
        // j => [index,len)，检测s[index,j]是否回文，如果是，则加入path，最后撤销选择
        for (int i = index; i < length; i++) {
            if (!isPalindrome(s, index, i)) {
                continue;
            }
            path.add(s.substring(index, i + 1));
            dfs(answer, path, i + 1, length, s);
            path.remove(path.size() - 1);
        }
    }

    private boolean isPalindrome(String s, int left, int right) {
        while (left < right) {
            if (s.charAt(left) != s.charAt(right)) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }
}
```

**复杂度分析**
+ 时间复杂度：$O(N*2^n)$，每个位置的字符可以拆分也可以不拆分，因此时间复杂度是$O(2^n)$，判断每个子字符串是否为回文串需要$O(N)$的时间。
+ 空间复杂度：$O(N*2^n)$，考虑$answer$，每个位置的字符可以拆分也可以不拆分，两种情况都需要占用空间，此部分空间是$O(2^n)$，而对于所有的答案都需要保存，此部分空间是$O(N)$.

#### 方法二：记忆法回溯

**思路及算法**

在方法一的基础上添加$memo$保存$s[i,j]$是否为回文串，减少重复判断。

```java
class Solution {
 /**
     * DFS回溯
     * 1. 回溯出口      index == s.length()
     * 2. 回溯递进      遍历[i,n)  如果s[i,j] 是回文串，则加入path，然后递归 s[i,j+1]
     *
     * @param s
     * @return
     */
    public List<List<String>> partition(String s) {
        List<List<String>> answer = new ArrayList<>();
        List<String> path = new ArrayList<>();
        Boolean[][] memo = new Boolean[s.length()][s.length()];
        dfs(memo, answer, path, 0, s.length(), s);
        return answer;
    }

    private void dfs(Boolean[][] memo, List<List<String>> answer, List<String> path, int index, int length, String s) {
        if (index == length) {
            answer.add(new ArrayList<>(path));
            return;
        }
        // 本次有什么选择?
        // j => [index,len)，检测s[index,j]是否回文，如果是，则加入path，最后撤销选择
        for (int i = index; i < length; i++) {
            if (!isPalindrome(memo, s, index, i)) {
                continue;
            }
            path.add(s.substring(index, i + 1));
            dfs(memo, answer, path, i + 1, length, s);
            path.remove(path.size() - 1);
        }
    }

    private boolean isPalindrome(Boolean[][] memo, String s, int left, int right) {
        if (memo[left][right] != null) {
            return memo[left][right];
        }
        while (left < right) {
            if (s.charAt(left) != s.charAt(right)) {
                return memo[left][right] = false;
            }
            left++;
            right--;
        }
        return memo[left][right] = true;
    }
}
```

**复杂度分析**
+ 时间复杂度：$O(N*2^n)$，每个位置的字符可以拆分也可以不拆分，因此时间复杂度是$O(2^n)$，判断每个子字符串是否为回文串需要$O(N)$的时间，但是添加了记忆化搜索，每个子串至多搜索一次。
+ 空间复杂度：$O(N*2^n)$，考虑$answer$，每个位置的字符可以拆分也可以不拆分，两种情况都需要占用空间，此部分空间是$O(2^n)$，而对于所有的答案都需要保存，此部分空间是$O(N)$.

#### 方法三：DP+回溯

我们可以利用DP通过提前计算好字符串的回文信息。

**思路和算法**

需要提前截取子字符串然后进行DP。那么问题来了，如何截取所有在子字符串？
我们可以定义如下双重循环：
```java
for(int right = 0;right < s.length(); right++) {
    for(int left = 0;left<= right; right++) {
        // s[left,right] 就是所有的子字符串
    }
}
```

**思考状态转移方程**
1. 定义$dp[i][j]$代表$s[i, j]$是否为回文串
2. 当$s[left] == s[right]$可知字符串两端是相等的，需要考虑$left和right$的距离，通过穷举(笨办法)可知：
    1. $right - left = 0$时，$left$和$right$就是同一个字符，显然可以直接得到答案$true$
    2. $right - left = 1$时，$left$和$right$是挨着的，比如$aa$，显然可以直接得到答案$true$
    3. $right - right = 2$时，$left$和$right$中间夹了一个字符，比如$aba$，显然可以直接得到答案$true$
    4. $right - right > 2$ 时，不能直接看不出来了，需要进行状态转移，比如$aabaa$，当$s[0] == s[4]$时，我们需要看看$s[1,3]$是不是回文串，在本例中，由于$s[1,3]$是回文串，因此$s[0,4]$也是。

综上，DP方程如下：

$$
dp(i,j) = \begin{cases} 
false, & \text{if } s[i] \ne s[j] \\
true, & \text{if } s[i] = s[j] \& j-i \le 2 \\  
dp[i+1][j-1], & \text{if } j-i \gt 2
\end{cases}
$$

```java

    /**
     * DP+DFS回溯
     * 1. DP处理 dp[i][j]是否为回文
     * 1.1 dp[i][i] = true
     * 1.2 dp[i][j] = s[i] == s[j] && (dp[i+1][j-1] || j-i<=2)
     * 2. 回溯
     * 2.1 回溯出口: index == s.length()
     * 2.2 回溯递进：j => [i,s.length())  if(dp[i][j])  添加子串，然后 dfs(index+1)
     *
     * @param s
     * @return
     */
    public List<List<String>> partition(String s) {
        int n = s.length();
        boolean[][] dp = new boolean[n][n];
        for (int right = 0; right < n; right++) {
            for (int left = 0; left <= right; left++) {
                if (s.charAt(left) == s.charAt(right)) {
                    if (right - left <= 2) {
                        dp[left][right] = true;
                    } else {
                        dp[left][right] = dp[left + 1][right - 1]; // 上一轮遍历过
                    }
                }
            }
        }

        List<List<String>> answer = new ArrayList<>();
        List<String> path = new ArrayList<>();
        dfs(answer, path, dp, 0, n, s);
        return answer;
    }

    private void dfs(List<List<String>> answer, List<String> path, boolean[][] dp, int index, int n, String s) {
        if (index == n) {
            answer.add(new ArrayList<>(path));
            return;
        }
        for (int right = index; right < n; right++) {
            if (dp[index][right]) {
                path.add(s.substring(index, right + 1));
                dfs(answer, path, dp, right + 1, n, s);
                path.remove(path.size() - 1);
            }
        }
    }
}
```
**复杂度分析**
+时间复杂度：$O(2^n)$，计算$dp$需要$O(n^2)$,回溯需要$O(2^n)$。
+ 空间复杂度：$O(N*2^n)$，考虑$answer$，每个位置的字符可以拆分也可以不拆分，两种情况都需要占用空间，此部分空间是$O(2^n)$，而对于所有的答案都需要保存，此部分空间是$O(N)$;考虑$dp$，需要$O(n^2)$的空间
