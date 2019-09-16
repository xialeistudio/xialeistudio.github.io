---
title: leetcode(3)——无重复字符的最长子串
date: 2019-09-16 18:34:58
categories:
- leetcode
---

欢迎跟着夏老师一起学习算法。

关注公众号可以进行交流和加入微信群，群内定期有系列文章分享噢！

![img](https://static.ddhigh.com/blog/2019-08-26-060638.jpg)

[TOC]

## Question

> 给定一个字符串，请你找出其中不含有重复字符的 **最长子串** 的长度。

**示例1：**

```text
输入: "abcabcbb"
输出: 3 
解释: 因为无重复字符的最长子串是 "abc"，所以其长度为 3。
```

**示例2：**

```text
输入: "bbbbb"
输出: 1
解释: 因为无重复字符的最长子串是 "b"，所以其长度为 1。
```

**示例3：**

```text
输入: "pwwkew"
输出: 3
解释: 因为无重复字符的最长子串是 "wke"，所以其长度为 3。
     请注意，你的答案必须是 子串 的长度，"pwke" 是一个子序列，不是子串。
```

## 遍历法

> 最容易想到的一种算法，也是效率最低的一种算法
>
> 1. 通过两次遍历得到所有可能的 **子字符串** 列表
> 2. 将每个字符串传入一个函数检测是否包含重复字符，如果不包含则更新最长子串的长度

```javascript
// 判断给定的子串是否包含重复字符
function isUnique(str, start, end) {
  const chars = [];
  for(let i = start; i < end; i++) {
    const char = str[i];
    if(chars.indexOf(char) !== -1) { // 字符已存在，本字符串不符合条件
      return false;
    }
    chars.push(char); // 添加字符
  }
  return true;
}

// 获取字符串最长子串长度
function lengthOfLongestSubstring(s) {
  let max = 0;
  for(let i = 0; i < s.length; i++) {
    for(let j = i+1; j <= s.length; j++) {
      if(isUnique(s, i, j)) { // 判断子串是否唯一
        max = Math.max(max, j - i); // j - i 为当前子串长度
      }
    }
  }
  return max;
}
```

时间复杂度$O(n^3)$

> i循环，j循环，isUnquie中的循环，3次循还嵌套

空间复杂度$O(min(n,m))$

> isUnique函数中定义了一个数组来存储不重复的子串字符，长度为$k$,$k$的长度取决于字符串$s$的大小$n$以及 字符串$s$包含的不重复字符数大小$m$

## 滑动窗口法

> 暴力法中我们会重复检查一个子串是否包含重复的字符，如果从$i$ ~ $j-1$ 之间的子串已经被检查过没有重复字符了，那么只需要检查$s[j]$是否在这个子串就行了。
>
> 子串使用js自带的数据结构Set存储
>
> 如果不在该子串，那么子串长度+1，$j+1$，继续往后走
>
> 如果在这个子串，证明出现了重复，我们需要将$s[i]$移出来之后$i+1$，继续往后走

```javascript
function lengthOfLongestSubstring(s) {
  const set = new Set();
  const max = 0;
  let i = 0;
  let j = 0;
  
  while(i < s.length && j < s.length) {
    if(!set.has(s[j])) { // j 不在set中，set中添加s[j],j后移，同时更新最大子串长度
      set.add(s[j]);
     	j++;
      max = Math.max(max, j - i);
    } else {
      set.delete(s[i]); // 移除set左边的数据，i后移一位
      i++;
    }
  }
  return max;
}
```

时间复杂度 $O(2n) \approx O(n)$

> 最好的情况是j一次走完没有出现重复，最坏的情况是i和j都走到了末尾

空间复杂度 $O(min(n,m))$

> 与暴力法相似，也需要一个Set存储不重复字符，$n$ 是字符串$s$长度，$m$是字符串$s$中不重复的字母个数

## 优化的滑动窗口

> 在滑动窗口解法中，$i$的后移可以优化一下，如果 s$[j]$ 在 s[$i$] ~ s[$j$] 内与字符 $c$ (随便取的名字)重复，$i$ 不需要一步一步$i$++，直接把 $i$ 定位到 $c$ + 1的位置即可。这样可以将算法时间复杂度稳定在 $O(n)$

```javascript
function lengthOfLongestSubstring(s) {
	const map = {}; // 保存 字符和下标的映射关系，如果字符重复，从map拿到位置，i直接跳到这个位置
  let max = 0;
  
  for(let i = 0, j = 0;j < s.length;j++) {
    const char = s[j];
    if(map[char] !== undefined) { // 当前字符存在重复，需要将i更新
      i = Math.max(i, map[char]); // 如果i的当前位置大于map[char]，不能更新为map[char]
    }
    max = Math.max(max, j - i + 1); // 由于j最大是s.length-1，所以最大子串长度需要+1
    map[char] = j + 1; // 保存映射关系
  }
  return max;
}
```

时间复杂度 $O(n)$

> 只遍历了j

空间复杂度 $O(min(n,m))$

> 与之前的方法相同

Q: 为什么第8行的 `i = Math.max(i, map[char])` 不能直接是 `i = map[char]`?

A: $i$ 的位置比`map[char]`大的情况下如果直接赋值会导致 $i$ 往前面走，会导致返回的子串长度大于实际的子串长度

错误例子 `abba`

| i                                               | j    | s[j] | s[i] ~ s[j] | Max  |
| ----------------------------------------------- | ---- | ---- | ----------- | ---- |
| 0                                               | 0    | a    | a           | 1    |
| 0                                               | 1    | b    | ab          | 2    |
| 2(map中没有s[j]，所以这里的位置直接是当前j的值) | 2    | b    | b           | 2    |
| 1(map中有s[j]，第1个字符就是a，直接拿来用)      | 3    | a    | bba         | 3    |

可以看到第4次循环中 i 的位置已经出现了问题，把位置1的a拿过来进行计算了，窗口的起始左边也从2变成了1，往回走了。