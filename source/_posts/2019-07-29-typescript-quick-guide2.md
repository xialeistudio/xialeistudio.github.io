---
title: TS简明教程(2)
date: 2019-07-29 10:11:30
categories:
- frontend
tags:
- typescript
- ts
---
为了后续内容(如`nestjs`等框架)的开展，本文更新TS相关的基础知识。

关注获取更多`TS精品文章`
![二维码](https://more-happy.ddhigh.com/FuFpZh9QTZVatcBtupR4MtOGPGTJ?imageView2/1/w/200)

## 类

传统JS使用`函数`和`原型链`进行集成，在`ES6`出现了`class`关键，JS也能使用传统OOP的方式进行继承，但是还是存在一定的局限性，在TS中，OOP已经和传统语言差不多。

```typescript
class Parent {
    name: string;
    age: number;

    constructor(name: string, age: number) {
        this.name = name;
        this.age = age;
    }

    say() {
        return `name: ${this.name}, age: ${this.age}`;
    }
}

const parent = new Parent();
parent.say();
```

可以看到TS的OOP写法和Java还是有点类似的。但是他两的构造方法名不同，TS构造方法名为`constructor`，Java是`类名`。

## 继承

继承用来扩展现有的类，TS中这一点和传统语言一样使用`extends`语法。

```typescript
class Parent {
    name: string;
    constructor(name: string) {
        this.name = name;
    }
    say() {
        console.log(`Parent say: ${this.name}`);
    }
}

class Child extends Parent {
    age: number;
    constructor(name: string, age: number) { // 覆盖父类构造方法
        super(name); // 调用父类构造方法
        this.age = age;
    }
    say() {
        console.log(`Child say: ${this.name} ${this.age}`);
    }
}

const child: Parent = new Child("haha" ,1);
child.say(); // 输出 Child say haha 1
```

1. 子类存在构造方法时，必须`显示调用`父类构造方法`先有父亲，后有儿子`
2. TS方法调用是基于`值`而不是基于`类型声明`，比如`child`声明为`Parent`类型，但是值是子类型，所以调用方法时会调用`子类`的`say`


## 访问限定符

### public

TS中方法和属性默认的访问限定符为`public`，所有外部或内部成员都可访问。

```typescript
class Parent {
    public name: string; // public可以不加
    say() {
        console.log(`say ${this.name}`);
    }
}
const p = new Parent();
p.name = 'hello';
p.say(); // 输出 say hello
```

### private

私有访问，只能在`本类`访问,`子类和其他类都不行`。

```typescript
class Parent {
    private name: string;

    private say() {
        console.log(`say ${this.name}`);
    }
}
const p = new Parent();
p.name = 'hello'; // 错误，private限定的属性不能被外部访问
p.say(); // 错误，private限定的访问不能被外部访问
```

### protected

保护性访问，只能`被本类或本类的子类(子类的子类也可以访问)`。

```typescript
class Parent {
    protected name: string;

    constructor(name: string) {
        this.name = name;
    }

    protected say() {
        console.log(`say ${this.name}`);
    }
}

class Child extends Parent {
    public say() { // 提升访问性
        console.log(`say ${this.name}`); // 访问父类属性
    }
}
const c = new Child('hello');
c.say(); // 输出 say hello
```

访问限定符只能提升，不能降低，如下例子是`无法通过编译的`：

```typescript
class Parent {
    protected name: string;
}

class Child extends Parent {
    private name: string; // 错误，子类访问性必须>=父类的访问性
}
```

## 只读限定

TS使用`readonly`声明只读`属性(方法不能使用)`，必须在`声明时`或者`构造时`进行赋值,`其他地方不能赋值`

```typescript
class Parent {
    private readonly name = 'hello';
    private readonly age: number;
    constructor(age: number) {
        this.age = age;
    }
}
```

## 参数属性

在上例中我们在构造方法中使用`this.age = age`对已存在的`私有只读属性age`进行了赋值。由于该操作时常用操作，所以TS有了更加便捷的写法：

```typescript
class Parent {
    constructor(readonly name: string, private readonly age: number) {

    }
    say() {
        console.log(`say ${this.name} ${this.age}`);
    }
}
```

上例中声明了`公有只读的name属性，私有只读的age属性`

## getter && setter

在传统语言中，几乎不会直接声明公有属性，然后对其进行操作，都会先定义私有属性，然后提供`getter`和`setter`方法对其操作(`Java中很多类都是这种情况`)

```typescript
class Parent {
    private _name: string;

    get name(): string {
        return this._name;
    }

    set name(name: string) {
        console.log(`name设置前: ${this._name} 设置后: ${name}`);
        this._name = name;
    }
}

const parent = new Parent();
parent.name = 'ok'; // 可以直接使用赋值语句，但是会自动调用set name(name: string)方法
```

getter和setter方法提高了开发者对属性的控制，一起对属性的访问都是可控的，为以后的扩展性打下了基础（比如如果需要加缓存，我们可以在set时设置缓存,get时读取缓存，如果是直接操作属性的话，该功能实现起来很麻烦

## 静态属性 && 静态方法

以上讨论的都是`实例属性和梳理方法`，需要有实例才能调用，如果有些属性或方法并不是存在于实例上时可以使用静态方法或静态属性

```typescript
class Parent {
    static name: string;

    static say() {
        console.log(`name ${this.name}`); // 方法是静态，属性是静态时可以使用this
    }
}
Parent.say();// 使用类名调用静态方法
```

需要注意的是`实例可以直接调用静态，静态不能直接调用实例`，因为`实例需要实例化后调用`

## 抽象类

传统语言中接口只包含实现，不包含细节。而抽象类可以包含细节。一般来说，有些公有方法可以放到抽象类做，不同的子类完成不同功能的代码可以放到抽象类做。

```typescript
abstract class Animal {
    abstract say(): void; // 声明抽象方法，子类必须实现

    eat() {
        console.log(`animal eat`);
    }
}

class Human extends Animal { // 使用extends关键字
    say() {
        console.log('human say words');
    }
}

class Dog extends Animal {
    say() {
        console.log('dog say wangwang');
    }
}
```

## 接口

接口用来限定子类的行为，不关心具体实现。与传统语言不同的是,TS接口还可以限定变量或常量的属性

限定子类行文：

```typescript
interface Animal {
    say(): void;
    eat(): void;
}

class Human implements Animal {
    say() {
        console.log('human say');
    }
    eat() {
        console.log('human eat');
    }
}
```

限定变量属性：
```typescript
interface A {
    name?: string;
    age: number;
}
const obj: A = {
    age: 10,
    // name是可选的
};
```

### 可索引类型

使用`可索引类型`来`描述`可以通过`索引访问得到`的类型。如`person["name"]`,`list[0]`

```typescript
interface HashMap {
    [key: string]: any; // 冒号左边为属性名类型，右边为值类型
}

const map: HashMap = {};
map["name"] = "1";
map.a = "2";
```

### 接口继承

与类继承类似，接口也可以通过继承来扩展现有的功能：

```typescript
interface Animal {
    eat(): void; // 动物会吃，但是怎么吃的不管
}
interface Human extends Animal {
    say(): void; // 人会说话，但是怎么说，说什么不管
}
```

### 混合类型

JS中，函数可以直接调用也可以通过对象方式调用，TS中可以通过接口声明被修饰的函数支持的调用方式：

```typescript
interface Counter {
    (start: number): string;
    step: number;
    reset(): void;
}

function getCounter(): Counter {
    const counter = <Counter> function(start: number) {};
    counter.step = 1;
    counter.reset = function() {};
}
const c = getCounter();
c(1);
c.reset();
c.step = 2;
```

## 结语

面向对象中的类和接口内容实在是太多了，本文只选择了开发中常用到的用法进行说明，不足之处，敬请包涵。
对TS有兴趣的小伙伴可以扫码加我进行交流
![微信](https://more-happy.ddhigh.com/Fg5UE615NzZ0dXo6_gUe6qpCJILG?imageView2/1/w/200)