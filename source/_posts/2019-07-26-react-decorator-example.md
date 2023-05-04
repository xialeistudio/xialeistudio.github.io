---
title: 使用Typescript装饰器来劫持React组件
date: 2019-07-26 19:31:15
categories:
- engineering
---
最近在捣鼓Typescript的装饰器，NodeJs项目的装饰器比较好理解，但是React项目的装饰器由于有JSX，走了一点弯路，但是总之来说是`新技能get`

## typescript对装饰器的说明

> 装饰器是一种特殊类型的声明，它能够被附加到类声明，方法， 访问符，属性或参数上。 装饰器使用 @expression这种形式，expression求值后必须为一个函数，它会在运行时被调用，被装饰的声明信息做为参数传入。

装饰器为我们提供了`运行时修改数据`的能力。

## React例子

Parent.tsx

```typescript
@Component
export default class App extends PureComponent {
  handleClick() {
    console.log('parent click');
  }
  render() {
    return (
      <div className="App" onClick={this.handleClick}>parent</div>
    );
  }
}
```

Component装饰器

```typescript
function Component<T extends { new(...args: any[]): any }>(component: T) { // 泛型限定
  return class extends component {
    handleClick() { // 劫持onClick
      super.handleClick()
      console.log('child clicked');
    }
    render() {
      const parent = super.render()
      // 劫持onClick
      return React.cloneElement(parent, { onClick: this.handleClick })
    }
  }
}
```
点击渲染之后的`parent`字符，可以看到劫持成功

![clipboard.png](https://user-gold-cdn.xitu.io/2019/7/26/16c2e0b64f0d48a7?imageView2/0/w/1280/h/960/format/webp/ignore-error/1)

## 项目地址
[react-decorator-example](https://github.com/xialeistudio/react-decorator-example)
## 结论

本文写的只是比较简单的装饰器用法，但是可以基于此文的原来来开发如`登录后才能访问的组件`之类的装饰器，将业务逻辑更好的组织起来。

对TS有兴趣的伙伴可以加我微信交流~

