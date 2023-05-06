---
title: leetcode(1) —— 两数之和
date: 2019-09-12 19:32:13
categories:
- Algorithm
tags:
- leetcode
---
本文是力扣算法的第一篇，讲解两数之和问题。

## 问题

>  给定一个整数数组 *`nums`* 和一个目标值 *`target`*，请你在该数组中找出和为目标值的那 两个 整数，并返回他们的数组下标。
>
> 你可以假设每种输入只会对应一个答案。但是，你不能重复利用这个数组中同样的元素。

**示例:**

```text
给定 nums = [2, 7, 11, 15], target = 9

因为 nums[0] + nums[1] = 2 + 7 = 9

所以返回 [0, 1]
```

## 嵌套循环解题法

> 通过第1遍循环可以拿到当前值和剩余值，然后嵌套循环一次，检查剩余值是不是在数组中。

```javascript
function twoSum(nums, target) {
  for(let i = 0;i<nums.length;i++) {
    const current = nums[i]; // 拿到当前值
    const remain = target - current; // 拿到剩余值
    
    for(let j = 1;j<nums.length;j++) {
      if(nums[j] === remain) {
        return [i, j];
      }
    }
  }
}
```

时间复杂度是O(n^2)

> nums的长度为n,嵌套循环的总执行次数是 n*(n-1)，当n趋向于无穷大时n-1和n没什么区别，忽略

空间复杂度为O(1)

> 增加的临时变量有 current, remain, i, j，不会随着nums的长度而增加，所以是常量O(1)

嵌套循环的效率是最低的, 面试的时候就算回答出来被送走的几率也是很大的。

## 两遍HashTable解题法

> 核心思想是使用一个HashTable保存每个值和每个值的位置。
>
> 第1次循环时构造出HashTable，键为nums数组的元素，值为元素对应的下标
>
> 第2次循环时获取当前循环的值以及剩余值，如果剩余值的索引不等于当前值的索引，且剩余值也在HashTable中，直接从HashTable读取出当前值和剩余值的index返回。

```javascript
function twoSum(nums, target) {
  const hashTable = {};
  // 第1次循环
  for(let i = 0;i<nums.length;i++) {
    hashTable[nums[i]] = i;
  }
  // 第2次循环
  for(let i = 0;i<nums.length;i++) {
    const current = nums[i];
    const remain = target - current;
    if(map[remain] !== undefined && map[remain] !== i) {
      return [i, map[remain]];
    }
  }
}
```

时间复杂度为O(2n) = O(n)

> 进行了两次循环，理论上是2*n的时间复杂度，但是当n趋向于无穷大时，n和2n的差距可以忽略，所以结果是O(n)

空间复杂度为O(n)

> 增加了HashTable，大小是nums的长度n，所以空间复杂度是O(n)

该算法利用了HashTable的O(1)的时间复杂度巧妙地减少了嵌套循环，算法效率提升很大！

一般回答到这里基本就没啥问题了，但是还有一种基于HashTable一次循环就能解决问题的方案。

## 一遍HashTable解题法

> 循环nums数组，得到当前值和剩余值，判断剩余值在不在HashTable，如果在的话，直接返回剩余值的位置和当前值的位置。如果不在则把剩余值插入HashTable，继续循环。

> Q: 为什么先返回的是剩余值的位置而不是当前值的位置？
>
> A: 因为当前值的位置是确定的，所以当前值的位置不在HashTable中，但是剩余值可能在前面的循环中插入了HashTable，是老值，所以先返回。

```javascript
function twoSum(nums, target) {
  const hashTable = {};
  
  for(let i = 0;i<nums.length;i++) {
    const current = nums[i];
    const remain = target - remain;
    if(hashTable[remain] !== undefined) { // 为什么不需要判断位置?因为当前值的位置根本没插入HashTable中，索引不可能重复
      return [hashTable[remain], i];
    }
    hashTable[current] = i; // 插入当前值到HashTable，下一次循环时这里就成了"老值"
  }
}
```

时间复杂度O(n)

> 正宗的O(n),一次循环解决问题

空间复杂度O(n)

> 增加了HashTable，大小随着nums的增大而增大

## 结尾

合理使用HashTable能够将算法的时间复杂度降低很多，一般会有一个指数级的提升！