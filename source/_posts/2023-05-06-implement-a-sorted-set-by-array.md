---
title: Implementing a sorted set by ordered array
date: 2023-05-06 15:41:52
categories:
- Engineering
tags:
- Algorithm
---

> A [`Set`](https://docs.oracle.com/javase/8/docs/api/java/util/Set.html) that further provides a *total ordering* on its elements. The elements are ordered using their [natural ordering](https://docs.oracle.com/javase/8/docs/api/java/lang/Comparable.html), or by a [`Comparator`](https://docs.oracle.com/javase/8/docs/api/java/util/Comparator.html) typically provided at sorted set creation time. The set's iterator will traverse the set in ascending element order. Several additional operations are provided to take advantage of the ordering. (This interface is the set analogue of [`SortedMap`](https://docs.oracle.com/javase/8/docs/api/java/util/SortedMap.html).)
>
> ***Oracle*** - [SortedSet](https://docs.oracle.com/javase/8/docs/api/java/util/SortedSet.html)

Java provides a built-in `SortedSet` implementation, known as `TreeSet`. In this article, I'll show how to implement a `SortedSet` by `Ordered Array`.

<!--more-->

## Prerequisite

To implement a `SortSet`, you need to know about the following concepts and algorithms.

### Binary Search Algorithm

> In [computer science](https://en.wikipedia.org/wiki/Computer_science), **binary search**, also known as **half-interval search**,[[1\]](https://en.wikipedia.org/wiki/Binary_search_algorithm#cite_note-Williams1976-1) **logarithmic search**,[[2\]](https://en.wikipedia.org/wiki/Binary_search_algorithm#cite_note-FOOTNOTEKnuth1998§6.2.1_("Searching_an_ordered_table"),_subsection_"Binary_search"-2) or **binary chop**,[[3\]](https://en.wikipedia.org/wiki/Binary_search_algorithm#cite_note-FOOTNOTEButterfieldNgondi201646-3) is a [search algorithm](https://en.wikipedia.org/wiki/Search_algorithm) that finds the position of a target value within a [sorted array](https://en.wikipedia.org/wiki/Sorted_array).[[4\]](https://en.wikipedia.org/wiki/Binary_search_algorithm#cite_note-FOOTNOTECormenLeisersonRivestStein200939-4)[[5\]](https://en.wikipedia.org/wiki/Binary_search_algorithm#cite_note-5) Binary search compares the target value to the middle element of the array. If they are not equal, the half in which the target cannot lie is eliminated and the search continues on the remaining half, again taking the middle element to compare to the target value, and repeating this until the target value is found. If the search ends with the remaining half being empty, the target is not in the array.
>
> ***Wikipedia*** - [Binary search algorithm](https://en.wikipedia.org/wiki/Binary_search_algorithm)

Binary Search can also search for ceil and floor key to a specific key.

In my implementation, I use Binary Search to find a specific key or the first key greater than the specific key.

### Automatic expansion algorithm

In Java,`Array ` can't be automatically expanded, so we need to expand manually, a simple way is to double the array size and copy the element to the new array.

Here is an example.

```java
// Automatic expansion
private void ensureCapacity(int newCapacity) {
  // keys is enough for newCapacity
  if (newCapacity < keys.length) {
  	return;
  }
  // increase by double
  var newKeys = (K[]) Array.newInstance(Comparable.class, keys.length * 2);
  var newValues = (V[]) Array.newInstance(Comparable.class, values.length * 2);
  for (int i = 0; i < keys.length; i++) {
  	if (keys[i] != null) {
    	newKeys[i] = keys[i];
    	newValues[i] = values[i];
    }
  }
  keys = newKeys;
  values = newValues;
}
```

## Implementation

### How to find ceil/floor key?

Well, for examle, there is a sorted array.

```java
[1,2,3,4,7,8]
```

If we want to find $ceil(5)$, what's the step? Here is the binary search procedure.

**Step 1**
$$
left = 0, right = 5, middle = (0+5)/2=2, nums[middle] = 3, \because 3 < 5, \therefore left = middle + 1 = 4
$$
**Step 2**
$$
left = 4, right = 5, middle = (4+5)/2=4, nums[middle] = 7, \because 7 > 5, \therefore right = middle-1=3
$$
**Step3**
$$
left=4,right=3, exit loop
$$
so finally $ceil(5) = 7$.

### Code

First, we need to declare a interface, so if we have some new implementations, we can easily expand our algorithm.

```java
import java.lang.reflect.Array;

// A simple SortSet implementation by Array
public interface SortSet<K extends Comparable<K>, V> {
    // Retrieve for the value of specific key
    V get(K key);

    // Put a new value
    void put(K key, V value);

    // Remove a specific key
    void remove(K key);

    // Retrieve the first key greater than the specific key
    K ceil(K key);

    // Get the rank of the specific key
    int rank(K key);

    // Retrieve the last key less than the specific key
    K floor(K key);

    // Check whether the key is exists
    boolean containsKey(K key);

    class ArraySortedSet<K extends Comparable<K>, V> implements SortSet<K, V> {
        private K[] keys;
        private V[] values;

        private int size;

        public ArraySortedSet(int capacity) {
            keys = (K[]) Array.newInstance(Comparable.class, capacity);
            values = (V[]) Array.newInstance(Object.class, capacity);
        }

        public ArraySortedSet() {
            this(8);
        }

        @Override
        public V get(K key) {
            var rank = rank(key);
            if (rank < size && keys[rank].compareTo(key) == 0) {
                return values[rank];
            }
            return null;
        }

        @Override
        public void put(K key, V value) {
            var rank = rank(key);
            if (rank < size && keys[rank].compareTo(key) == 0) {
                values[rank] = value;
                return;
            }
            ensureCapacity(size + 1);
            for (int j = size; j > rank; j--) {
                // move the prev element forward to make an empty to save new element
                keys[j] = keys[j - 1];
                values[j] = values[j - 1];
            }
            keys[rank] = key;
            values[rank] = value;
            size++;
        }

        // Automatic expansion
        private void ensureCapacity(int newCapacity) {
            // keys is enough for newCapacity
            if (newCapacity < keys.length) {
                return;
            }
            // increase by double
            var newKeys = (K[]) Array.newInstance(Comparable.class, keys.length * 2);
            var newValues = (V[]) Array.newInstance(Comparable.class, values.length * 2);
            for (int i = 0; i < keys.length; i++) {
                if (keys[i] != null) {
                    newKeys[i] = keys[i];
                    newValues[i] = values[i];
                }
            }
            keys = newKeys;
            values = newValues;
        }

        @Override
        public void remove(K key) {
            var rank = rank(key);
            if (rank < size && keys[rank].equals(key)) {
                // move the next element forward
                for (int i = rank + 1; i < size; i++) {
                    keys[i - 1] = keys[i];
                    values[i - 1] = values[i];
                }
                size--;
            }
        }

        @Override
        public K ceil(K key) {
            var rank = rank(key);
            if (rank < size && keys[rank].compareTo(key) == 0) {
                return keys[rank];
            }
            return rank >= size ? null : keys[rank];
        }

        @Override
        public int rank(K key) {
            var start = 0;
            var end = size;
            while (start <= end) {
                var middle = start + (end - start) / 2;
                if (keys[middle] == null) {
                    end = middle - 1;
                    continue;
                }
                var compare = key.compareTo(keys[middle]);
                if (compare == 0) {
                    return middle;
                }
                if (compare > 0) {
                    start = middle + 1;
                } else {
                    end = middle - 1;
                }
            }
            return start;
        }

        @Override
        public K floor(K key) {
            var left = 0;
            var right = size - 1;
            while (left <= right) {
                var middle = left + (right - left) / 2;
                var compare = keys[middle].compareTo(key);
                if (compare == 0) {
                    return keys[middle];
                } else if (compare > 0) {
                    right = middle - 1;
                } else {
                    left = middle + 1;
                }
            }
            // target is left than minimal value of keys
            if (right < 0) {
                return null;
            }
            if (left >= size) { // left is greater than the max keys
                return keys[size - 1];
            }
            return keys[right];
        }

        @Override
        public boolean containsKey(K key) {
            return get(key) != null;
        }

        @Override
        public String toString() {
            var sb = new StringBuilder();
            for (var i = 0; i < size; i++) {
                if (keys[i] != null) {
                    sb.append(keys[i]).append('=').append(values[i]);
                    if (i < size - 1) {
                        sb.append(',');
                    }
                }
            }
            return sb.toString();
        }
    }

    static void main(String[] args) {
        var set = new ArraySortedSet<Integer, Integer>();
        set.put(2, 2);
        set.put(1, 1);
        set.put(3, 3);
        set.put(4, 4);
        set.put(5, 5);
        set.put(6, 6);
        set.put(7, 7);
        set.put(8, 8);
        set.put(9, 9);
        System.out.println(set);
        System.out.println(set.get(3));
        System.out.println(set.get(-1));
        System.out.println(set.get(2));
        System.out.println(set.ceil(2));
        System.out.println(set.ceil(-1));
        set.put(0, 0);
        System.out.println(set.ceil(-1));
        System.out.println(set);
    }
}
```

## Reference

+ ***Oracle*** - [SortedSet](https://docs.oracle.com/javase/8/docs/api/java/util/SortedSet.html)
+ ***Wikipedia*** - [Binary search algorithm](https://en.wikipedia.org/wiki/Binary_search_algorithm)
