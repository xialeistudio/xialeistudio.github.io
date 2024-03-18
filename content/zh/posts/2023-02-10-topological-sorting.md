---
slug: topological-sorting
title: 拓补排序
date: 2023-02-10 12:00:00
tags:
- leetcode
categories:
- Algorithm
---

>  在计算机科学领域，有向图的拓扑排序或拓扑测序是对其顶点的一种线性排序，使得对于从顶点$u$到顶点$v$的每个有向边$uv$, $u$在排序中都在$v$之前。
>
> 例如，图形的顶点可以表示要执行的任务，并且边可以表示一个任务必须在另一个任务之前执行的约束；在这个应用中，拓扑排序只是一个有效的任务顺序。
>
> 当且仅当图中没有定向环时（即有向无环图），才有可能进行拓扑排序。
>
> 任何有向无环图至少有一个拓扑排序。

## 算法

1. 遍历有向边，构造u->v边中v的入度表，可使用哈希存储入度
2. 将入度为0的节点入队
3. 队列节点不断出队，出队时减小被更新节点的入度，如果被更新节点入度为0，则该节点入队
4. 重复以上过程，最终可以得到一个从入度为0到最终节点的序列，这就是拓补排序算法。

## 示例

Leetcode [210. 课程表2](https://leetcode.cn/problems/course-schedule-ii/description/)

```java
class Solution {

    // 生成邻接表 <当前节点，后置节点>
    // 进行BFS拓补排序，由最低依赖的开始写入答案
    public int[] findOrder(int numCourses, int[][] prerequisites) {
        Set<Integer>[] graph = new HashSet[numCourses];
        for (int i = 0; i < numCourses; i++) {
            graph[i] = new HashSet<>();
        }
        // 入度
        int[] inDegree = new int[numCourses];
        for (int[] p : prerequisites) {
            int current = p[0];
            int pre = p[1];
            graph[pre].add(current);
            inDegree[current]++;
        }
        Queue<Integer> queue = new LinkedList<>();
        for (int i = 0; i < numCourses; i++) {
            if (inDegree[i] == 0) {
                queue.offer(i);
            }
        }
        int[] answer = new int[numCourses];
        int index = 0;
        while (!queue.isEmpty()) {
            // 弹出课程
            int course = queue.remove();
            answer[index++] = course;
            // 遍历邻接表，减掉入度，入度归0时入队
            for (int target : graph[course]) {
                inDegree[target]--;
                if (inDegree[target] == 0) {
                    queue.offer(target);
                }
            }
        }
        return index >= numCourses ? answer : new int[0];
    }
}
```

**复杂度分析**

时间复杂度：$O(n)$ ,$n$是课程数量

空间复杂度：$O(n)$，$n$是课程数量