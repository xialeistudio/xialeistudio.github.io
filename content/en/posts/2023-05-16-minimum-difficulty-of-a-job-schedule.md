---
slug: minimum-difficulty-of-a-job-schedule
title: Minimum difficulty of a job schedule
date: 2023-05-16 22:19:15
categories:
- Algorithm
tags:
- Dynamic programming
---

Today I'll share an article about `Dynamic Programing` .

> **Dynamic programming** is both a [mathematical optimization](https://en.wikipedia.org/wiki/Mathematical_optimization) method and a computer programming method. The method was developed by [Richard Bellman](https://en.wikipedia.org/wiki/Richard_Bellman) in the 1950s and has found applications in numerous fields, from [aerospace engineering](https://en.wikipedia.org/wiki/Aerospace_engineering) to [economics](https://en.wikipedia.org/wiki/Economics).
>
> ***wikipedia*** - [Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming)

<!--more-->

## Question

You want to schedule a list of jobs in `d` days. Jobs are dependent (i.e To work on the `ith` job, you have to finish all the jobs `j` where `0 <= j < i`).

You have to finish **at least** one task every day. The difficulty of a job schedule is the sum of difficulties of each day of the `d` days. The difficulty of a day is the maximum difficulty of a job done on that day.

You are given an integer array `jobDifficulty` and an integer `d`. The difficulty of the `ith` job is `jobDifficulty[i]`.

Return *the minimum difficulty of a job schedule*. If you cannot find a schedule for the jobs return `-1`.

**Example 1:**

![img](https://static.ddhigh.com/blog/2023/05/16/1684246842894993000.png)

```
Input: jobDifficulty = [6,5,4,3,2,1], d = 2
Output: 7
Explanation: First day you can finish the first 5 jobs, total difficulty = 6.
Second day you can finish the last job, total difficulty = 1.
The difficulty of the schedule = 6 + 1 = 7 
```

**Example 2:**

```
Input: jobDifficulty = [9,9,9], d = 4
Output: -1
Explanation: If you finish a job per day you will still have a free day. you cannot find a schedule for the given jobs.
```

**Example 3:**

```
Input: jobDifficulty = [1,1,1], d = 3
Output: 3
Explanation: The schedule is one job per day. total difficulty will be 3.
```

 

**Constraints:**

- `1 <= jobDifficulty.length <= 300`
- `0 <= jobDifficulty[i] <= 1000`
- `1 <= d <= 10`

## Solution

### Thinking

We need to split $jobDifficulty$ to $d$ parts, and make the sum of the maximum of each parts be lowest. 

If the $d$ equal `1`, the answer is simple: $ \max_{i=0}^n jobDifficulty_i $, so what if  $d$ is greater than $1$?

We can split at index $k$ , so we get  $2$ parts, the first part $jobDifficulty[0,k]$ and the second part $jobDifficulty[k+1, n]$,

so we can calculate the maximum of the first part and the second part, and then we succeeded in reducing the scale of the problem, we can keep splitting the first part, for different $k$, we'll get different parts and different maximum of each part.

Let's start Dynamic programming. In this article, I'll use **Recursion** to implement Dynamic programming.

**DP Definition**

We can declare a function as below, this function will return the **minimal** sum of $count$ parts from $nums[0, index]$.

```java
int dp(int[] nums, int index, int count)
```

**Base case**

+ If the $length$ of $nums[0, index]$ is less than $count$, it's impossible to split.
+ If the $count=1$ , just return  $\max_{i=0}^n nums_i$

**State transition equation**

If the $count>1$, we will declare a split point $i$ iterates from $0...index-1$,  so we get a answer and a sub problem, to solve the sub problem, we can call `dp` function again. So we can get a State transition equation.
$$
dp[index][count] = min(dp[index][count], current+subProblem)
$$

### Code

```java
class Solution {
        private int[][] memo;

        // Human translate
        // split the `jobDifficulty` array to `d` parts, make the sum of the maximum of each parts be lowest
        public int minDifficulty(int[] jobDifficulty, int d) {
            if (jobDifficulty.length < d) {
                return -1;
            }
            memo = new int[jobDifficulty.length][d+1];
            for(var i = 0; i < memo.length; i++) {
                Arrays.fill(memo[i], -2);
            }
            return dp(jobDifficulty, jobDifficulty.length - 1, d);
        }


        // split [0, index] to `count` parts
        private int dp(int[] nums, int index, int count) {
            // if [0, index] can't split to `count` parts, return -1(impossible)
            if (index + 1 < count) {
                return -1;
            }
            if (memo[index][count] != -2) { // if the memo store current value, return
                return memo[index][count];
            }
            // split to one part, return the maximun
            if (count == 1) {
                var max = Integer.MIN_VALUE;
                for (int i = 0; i <= index; i++) {
                    max = Math.max(max, nums[i]);
                }
                memo[index][count] = max;
                return max;
            }
            var answer = Integer.MAX_VALUE;
            for (int i = index - 1; i >= 0; i--) { // i represents the split point
                var current = max(nums, i + 1, index); // get the maximum of right part
                // we have a sub problem that split nums[0, i] to `count-1` part
                var subProblem = dp(nums, i, count - 1);
                if (subProblem != -1) { // if the sub problem has answer, update
                    answer = Math.min(answer, current + subProblem);
                }
            }
            answer = answer == Integer.MAX_VALUE ? -1 : answer;
            memo[index][count] = answer;
            return answer;
        }

        private int max(int[] nums, int i, int j) {
            var max = Integer.MIN_VALUE;
            for (int k = i; k <= j; k++) {
                max = Math.max(max, nums[k]);
            }
            return max;
        }
}
```

**Complexity**

Time Complexity: $O(n^2*d)$, $n$ is the length of $jobDiffculty$, we have a internal cycle to split the $nums$, whose time complexity is $d$, and the `max` function has a time complexity $n$, and when $d=1$, we have a cycle to calculate maximum.

Space complexity: $O(n*d)$, we use a memo to store the result to prevent repeat call.
