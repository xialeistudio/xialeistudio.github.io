---
title: 电话号码的字母组合
slug: letter-combinations-of-a-phone-number
date: 2024-04-18T15:15:26+08:00
categories:
- Algorithm
tags:
- leetcode
featured: true
---

### Question

[https://leetcode.cn/problems/letter-combinations-of-a-phone-number/description/?favorite=2cktkvj](https://leetcode.cn/problems/letter-combinations-of-a-phone-number/description/?favorite=2cktkvj)

给定一个仅包含数字 `2-9` 的字符串，返回所有它能表示的字母组合。答案可以按 任意顺序 返回。

给出数字到字母的映射如下（与电话按键相同）。注意 1 不对应任何字母。

![img](https://assets.leetcode-cn.com/aliyun-lc-upload/uploads/2021/11/09/200px-telephone-keypad2svg.png)

示例 1：

<pre><code>输入：digits = "23"
<strong>输出：
</strong>["ad","ae","af","bd","be","bf","cd","ce","cf"]
</code></pre>
示例 2：

<pre><code>输入：digits = ""
<strong>输出：
</strong>[]
</code></pre>

示例 3：

<pre><code>输入：digits = "2"
<strong>输出：
</strong>["a","b","c"]
</code></pre>



提示：

* `0 <= digits.length <= 4`
* `digits[i]` 是范围 `['2', '9']` 的一个数字。



### Solution

回溯法

遇到求组合的题目都可使用回溯法解答。

回溯法是什么？

简单来说就是可撤销的递归，解决回溯法的思路如下：

1. 找到回溯出口，什么情况下我们找到了题目要求的一个解，此时不再继续递归
2. 查找本趟调用中，有哪些可选项
3. 遍历可选项，将每个项选择，然后递归调用处理下一个位置，然后撤销选择

对于本题，我们回答以上三个问题：

> 需要声明一个StringBuilder，来存储我们的选择字符

1. 回溯出口，我们选择的字符串长度等于题目`digits` 的长度，此时查找到了一个解，将其插入最终的答案
2. 每趟调用我们处理一位`digit` ，而每个`digit` 可选的字母是固定的，比如`2` 对应`abc` (图片已给出）
3. 遍历`abc` ，在每趟遍历中选择当前的字母(`StringBuilder.append`)，然后递归调用下一个`digit` ，然后再撤销选择(`StringBuilder.deleteCharAt`)

```java
class Solution1 {

        public List<String> letterCombinations(String digits) {
            if (digits.length() == 0) {
                return Collections.emptyList();
            }

            var answer = new ArrayList<String>();
            var sb = new StringBuilder();
            var charMap = new HashMap<Character, String>();
            charMap.put('2', "abc");
            charMap.put('3', "def");
            charMap.put('4', "ghi");
            charMap.put('5', "jkl");
            charMap.put('6', "mno");
            charMap.put('7', "pqrs");
            charMap.put('8', "tuv");
            charMap.put('9', "wxyz");
            helper(answer, sb, 0, digits, charMap);
            return answer;
        }

        private void helper(ArrayList<String> answer, StringBuilder sb, int index, String digits, HashMap<Character, String> charMap) {
            if (sb.length() == digits.length()) { // sb的长度已达到要求，因此写入最终答案
                answer.add(sb.toString());
                return;
            }
            var digit = digits.charAt(index); // 本轮的数字
            var chars = charMap.get(digit); // 该数字可以选择的字母列表
            for (int i = 0; i < chars.length(); i++) { // 遍历可选择的字母
                sb.append(chars.charAt(i)); // 选择该字母
                helper(answer, sb, index + 1, digits, charMap); // 递归处理下一个数字
                sb.deleteCharAt(index); // 当前不选该字母，这样可以撤回当前选择去尝试其他选择
            }
        }
    }
```

**时间复杂度**

O(3^m*4^n), m是长度为3字母的数字数量，n是长度为4字母的数字数量。对于每个字符，我们都有3种或4种选择。

**空间复杂度**

O(m+n) ,m长度为3个字母的数字数量，n长度为4个字母的数字数量，需要一个`StringBuilder` 来存储选择的数据，`answers` 所占空间不计入空间复杂度，`charMap` 大小是固定的。
