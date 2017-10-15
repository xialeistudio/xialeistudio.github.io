---
layout: post
title: C++ RTTI 示例
date: 2016-06-21 01:51:07.000000000 +08:00
type: post
published: true
status: publish
categories:
- cpp
tags:
- rtti
- cpp
- dynamic_cast
meta:
  _edit_last: '1'
  views: '430'
  _wp_old_slug: c-rtti-%e7%a4%ba%e4%be%8b
---
```cpp
#include <iostream>
#include <stdlib.h>
#include <string>
#include <typeinfo>
using namespace std;

/**
* 定义移动类：Movable
* 纯虚函数：move
*/
class Movable
{
  public:
    virtual void move() = 0;
};

/**
* 定义公交车类：Bus
* 公有继承移动类
* 特有方法carry
*/
class Bus : public Movable
{
  public:
    void move()
    {
      cout << "Bus -- move" << endl;
    }
  
    void carry()
    {
      cout << "Bus -- carry" << endl;
    }
};

/**
* 定义坦克类：Tank
* 公有继承移动类
* 特有方法fire
*/
class Tank :public Movable
{
  public:
    void move()
    {
      cout << "Tank -- move" << endl;
    }

    void fire()
    {
      cout << "Tank -- fire" << endl;
    }
};

/**
* 定义函数doSomething含参数
* 使用dynamic_cast转换类型
*/
void doSomething(Movable *obj)
{
  obj->move();

  if (typeid(*obj) == typeid(Bus))
  {
   Bus *bus = dynamic_cast<Bus *>(obj);
   bus->carry();
  }

  if (typeid(*obj) == typeid(Tank))
  {
   Tank *tank = dynamic_cast<Tank *>(obj);
   tank->fire();
  }
}

int main(void)
{
  Bus *b = new Bus;
  Tank *t = new Tank;
  doSomething(b);
  doSomething(t);
  delete b;
  delete t;
  return 0;
}
```