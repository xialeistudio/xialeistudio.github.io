---
title: c语言实现简单版的php z_val结构体
date: 2019-02-26 17:32:16
categories:
- backend
- php
tags:
- c
---

## 源码

学习过PHP的人都知道PHP是基于C语言开发的，但是C语言是强类型的，PHP如何实现弱类型呢？答案在于这个

```c
typedef union _zvalue_value {
	long lval;					/* long value */
	double dval;				/* double value */
	struct {
		char *val;
		int len;
	} str;
	HashTable *ht;				/* hash table value */
	zend_object_value obj;
	zend_ast *ast;
} zvalue_value;

struct _zval_struct {
	/* Variable information */
	zvalue_value value;		/* value */
	zend_uint refcount__gc;
	zend_uchar type;	/* active type */
	zend_uchar is_ref__gc;
};
```

**type**保存了实际的类型，而**value**这个共用体保存了具体的值，我们使用到变量的时候需要根据变量类型来取出**_zvalue_value**中保存的具体值。
采用union能够避免内存浪费，同一时刻，一个**_zval_struct**中的共用体**zvalue_value**只有一个成员会分配内存，避免了无谓的内存分配。

## 编码

阅读源码之前，可能觉得是一个很复杂的实现，阅读源码之后，其实也能自己实现，关键是type和value的组合。源码如下：

```c
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>

enum z_val_type
{
    DOUBLE,
    LONG,
    STRING
};

struct z_val
{
    union {
        double dval;
        long lval;
        struct
        {
            char *val;
            int len;
        } str;
    } value;
    enum z_val_type type;
};

void z_val_print(struct z_val *);

int main(void)
{
    // double
    struct z_val *doubleVal = malloc(sizeof(struct z_val));
    doubleVal->type = DOUBLE;
    doubleVal->value.dval = 1.0;
    // long
    struct z_val *longVal = malloc(sizeof(struct z_val));
    longVal->type = LONG;
    longVal->value.lval = 1;
    // string
    struct z_val *strVal = malloc(sizeof(struct z_val));
    strVal->type = STRING;
    strVal->value.str.val = "Hello World!";
    strVal->value.str.len = strlen(strVal->value.str.val);

    z_val_print(doubleVal);
    z_val_print(longVal);
    z_val_print(strVal);

    free(strVal);
    free(longVal);
    free(doubleVal);
    return 0;
}

void z_val_print(struct z_val *val)
{
    switch (val->type)
    {
    case LONG:
        printf("type: long, val: %ld\n", val->value.lval);
        break;
    case DOUBLE:
        printf("type: double, val: %f\n", val->value.dval);
        break;
    case STRING:
        printf("type: string, val: %s, len: %d\n", val->value.str.val, val->value.str.len);
        break;
    }
}
```

## 编译
采用gcc编译

```
gcc -o union union.c
```

## 执行

```
./union
```

输出

```
type: double, val: 1.000000
type: long, val: 1
type: string, val: Hello World!, len: 12
```

可以看到输出跟预期一样，我们也实现了一个“弱类型”的变量，是不是很有成就感呢？
实现上，多阅读源码可以多多参考别人的思维方式和编码习惯，所谓“站在巨人的肩膀上，才能看得更远”