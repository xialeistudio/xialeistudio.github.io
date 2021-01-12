---
layout: post
title: React Flux ES6记事本应用
date: 2016-03-24 15:20:00.000000000 +08:00
type: post
published: true
status: publish
categories:
- frontend
- react
---

## 项目地址

[react-notepad-es6](https://github.com/xialeistudio/react-notepad-es6.git)

React出来有很久了，与angularjs最大的不同在于React只是一个处理UI层面的库，可以认为是“V”，而angularjs则是一整套解决方案。   

随着前端开发的组件化思想越来越浓烈，angularjs很多场合已经显得力不从心了。而这时候，核心为“模块化、组件化”的React可以派上永用场。真正用来开发项目的话，React肯定是不足的，缺少C和M模块。   

Facebook官方推荐的Flux可以认为是一个简单的解决方案，Flux没什么特别含义，就是一个facebook随便找的一个词而已。至于什么是Flux，本文不做解释，本文以Flux来开发一个记事本应用。

## 项目目录

```
|----action    Action Creator

    |---- NoteAction.js    记事本应用需要的动作

|----css    样式文件目录

    |---- style.scss    样式文件

|----dispatcher    分发器目录

    |---- AppDispatcher.js    分发器

|----store    Store目录

    |---- NoteStore.js     存储日记数据以及处理AppDispatcher派发事件

|----view    视图&组件目录

    |---- Note.jsx    单条日记

    |---- NoteBox.jsx    整个日记组件的父容器

    |---- NoteForm.jsx    日记创建/编辑表单

    |----NoteList.jsx    日记列表组件

|----entry.js    webpack入口文件

|----index.html    项目页面

|----webpack.config.js    webpack配置文件
```

## 项目思路
1. NoteList.jsx组件包含多个Note.jsx，NoteList.jsx的数据来源于NoteStore.js。
2. 创建日记时，NoteForm.jsx需要调用NoteAction的add方法最终触发AppDispatcher.dispatch方法
3. NoteStore注册AppDispatcher的监听器实现对dispatch事件的监听
4. 编辑日记时，Note.jsx调用NoteAction的setNote方法设置需要编辑的日记，通过AppDispatcher的调度之后最终将日记数据显示在NoteForm.jsx组件中。

## 项目实现
### 安装依赖
本文采用ES6语法进行开发， 所以需要安装babel编译器，打开终端执行以下命令：

```bash
npm init -y
npm install webpack webpack-dev-server -g
npm install flux microevent react react-dom --save
npm install babel-loader css-loader jsx-loader sass-loader style-loader --save-dev
npm instlal babel-preset-es2015 babel-preset-react --save-dev
npm install microevent --save
```

### webpack.config.js

```javascript
/**
 * Created by xialei on 2016/3/23 0023.
 */
module.exports = {
  entry: './entry.jsx',
  output: {
    publicPath: 'http://localhost:8000/assets',
    filename: 'bundle.js',
    path: './assets'
  },
  module: {
    loaders: [
    {test: /\.js$/, loader: 'babel'},
    {
      test: /.jsx?$/,
      loader: 'babel-loader',
      exclude: /node_modules/,
      query: {
        presets: ['es2015', 'react']
      }
    },
    {test: /\.css$/, loader: 'style!css'},
    {test: /\.scss$/, loader: 'style!css!sass'}
    ]
  },
  resolve: {
    extensions: ['', '.js', '.jsx']
  }
};
```

### dispatcher/AppDispatcher.js

```javascript
import Flux from 'flux';
let AppDispatcher = new Flux.Dispatcher();
export default AppDispatcher;
```

### action/NoteAction.js
ActionCreator主要是为了简化代码量，不然每次需要触发动作的时候都需要调用AppDispatcher.dispatch方法。   
根据项目实际情况，可以总结出需要以下动作：
+ 创建日记
+ 更新日记
+ 删除日记
+ 编辑日记

由于ActionCreator是为了简化AppDispatcher.dispatch的方法调用，所以需要引入该模块。   

```javascript
/**
 * Created by xialei on 2016/3/23 0023.
 */
import AppDispatcher from '../dispatcher/AppDispatcher';
export default class NoteAction {
  static create(item) {
    AppDispatcher.dispatch({
      eventName: 'create-note',
      item: item
    });
  }

  static update(item) {
    AppDispatcher.dispatch({
      eventName: 'update-note',
      item: item
    });
  }

  static remove(item) {
    AppDispatcher.dispatch({
      eventName: 'remove-note',
      item: item
    });
  }

  static setNote(item) {
    AppDispatcher.dispatch({
      eventName: 'set-note',
      item: item
    });
  }
}
```

### store/NoteScore.js
有了分发，就要有接收，所以接下来编辑 store/NoteScore.js文件，这里需要注意的是由于V中不要直接调用AppDispatcher.dispatch，但是V是肯定需要监听事件的，所以这里使用**MicroEvent**库来进行事件处理。

```javascript
/**
 * Created by xialei on 2016/3/23 0023.
 */
import AppDispatcher from '../dispatcher/AppDispatcher';
import MicroEvent from 'microevent';
class NoteStore {
  constructor() {
    this.items = [];
  }
}

MicroEvent.mixin(NoteStore);
let store = new NoteStore();

AppDispatcher.register((payload)=> {
  switch (payload.eventName) {
    case 'create-note':
      store.items.push(payload.item);
      store.trigger('change');
      break;
    case 'update-note':
      store.items.forEach(function(i, index2) {
        if (i.id == payload.item.id) {
          store.items[index2] = payload.item;
          store.trigger('change');
        }
      });
      break;
    case 'remove-note':
      store.items.forEach(function(i, index2) {
        if (i.id == payload.item.id) {
          store.items.splice(index2, 1);
          store.trigger('change');
        }
      });
      break;
    case 'set-note':
      store.trigger('set', payload.item);
      break;
  }
  return true;
});
export default store;
```

### view/Note.jsx
该组件主要负责单条日记的显示和操作，所以该组件需要有一个初始属性以及编辑/删除方法，由于编辑日记最终会放在NoteForm.jsx组件进行，所以此处使用props而不是state。

```javascript
/**
 * Created by xialei on 2016/3/23 0023.
 */
import React from 'react';
import NoteAction from '../action/NoteAction';
export default class Note extends React.Component {
  constructor() {
    super();
    this.handleDelete = this.handleDelete.bind(this);
    this.handleUpdate = this.handleUpdate.bind(this);
  }

  handleUpdate() {
    NoteAction.setNote(this.props.note);
  }

  handleDelete() {
    if (confirm('确定删除吗?')) {
      NoteAction.remove(this.props.note);
    }
  }

  render() {
    return (
      <div className="note-item">
        <div className="id">{this.props.note.id}</div>
        <div className="text">{this.props.note.text}</div>
        <div className="operation">
          <button type="button" onClick={this.handleUpdate}>编辑</button>
          <button type="button" onClick={this.handleDelete}>删除</button>
        </div>
      </div>
    );
  }
}
```

由于采用了ES6语法，所以此处需要对this做特殊处理，否则会提示props undefined之类的错误。

### view/NoteBox.jsx
该组件的作用是将日记列表和日记表单显示出来，所以该组件只有一个构造方法和render方法。

```javascript
/**
 * Created by xialei on 2016/3/23 0023.
 */
import NoteList from './NoteList';
import NoteForm from './NoteForm';
import React from 'react';
export default class NoteBox extends React.Component {
  render() {
    return (
      <div className="note-box">
        <NoteList/>
        <NoteForm/>
      </div>
    );
  }
}
```

### view/NoteForm.jsx
该组件需要完成的事情比较多：
1. 需要对编辑和创建进行分别处理
2. 需要监听Note.jsx组件触发的编辑事件
3. 可编辑的文本域

根据以上要求，可以得出以下结论：

1. 需要使用state，以及设置一个初始的state
2. 在textarea的onChange事件中，将值设置到state中去
3. 需要监听NoteStore触发的“set”事件，将需要编辑的日记显示在textarea中

```javascript
/**
 * Created by xialei on 2016/3/23 0023.
 */
import React from 'react';
import NoteAction from '../action/NoteAction';
import NoteStore from '../store/NoteStore';
export default class NoteForm extends React.Component {
  constructor() {
    super();
    this.handleClick = this.handleClick.bind(this);
    this.handleSetNote = this.handleSetNote.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.resetForm = this.resetForm.bind(this);
    this.state = {
      note: {
        id: 0,
        text: ''
      }
    };
  }

  componentDidMount() {
    NoteStore.bind('set', this.handleSetNote);
  }

  componentWillUnmount() {
    NoteStore.unbind('set', this.handleSetNote);
  }

  isCreate() {
    return this.state.note.id == 0;
  }

  handleClick() {
  let text = this.refs.input.value;
  if (text.length == 0) {
    alert('请输入日记内容');
    this.refs.input.focus();
    return;
  }
  if (this.isCreate()) {
    let id = 1;
    if (NoteStore.items.length > 0) {
      id = NoteStore.items[NoteStore.items.length - 1].id + 1;
    }
    NoteAction.create({
      id: id,
      text: text
    });
   }
  else {
    let note = this.state.note;
    note.text = text;
    NoteAction.update(note);
  }
    this.resetForm();
  }

  render() {
  let note = this.state.note.text;
  let btnText = this.isCreate() ? '创建' : '编辑';
  let tips = this.isCreate() ? '' : '当前编辑 [' + this.state.note.id + '] 号日记';
  return (
    <div className="note-form">
    <div>{tips}</div>
    <textarea ref="input" rows="8" placeholder="日记内容" value={note} onChange={this.handleChange}/>
      <button type="button" onClick={this.handleClick}>{btnText}</button>
      <button type="button" onClick={this.resetForm}>重置</button>
    </div>
  );
 }

  handleChange(e) {
  let id = this.state.note.id || 0;
  this.setState({
    note: {
      id: id,
      text: e.target.value
    }
  });
 }

  handleSetNote(note) {
    this.setState({note: note});
    console.log('set ', this.state.note);
  }

  resetForm() {
    this.setState({
      note: {
        id: 0,
        text: ''
      }
    });
  }
}
```

### view/NoteList.jsx
该组件负责渲染NoteStore中的日记列表以及对NoteStore触发的change事件作出相应，实时显示最新数据。

```javascript
/**
 * Created by xialei on 2016/3/23 0023.
 */
import React from 'react';
import NoteStore from '../store/NoteStore';
import Note from './Note';
export default class NoteList extends React.Component {
  constructor() {
    super();
    this.handleChanged = this.handleChanged.bind(this);
  }

  componentDidMount() {
    NoteStore.bind('change', this.handleChanged);
  }

  componentWillUnmount() {
    NoteStore.unbind('change', this.handleChanged);
  }

  handleChanged() {
    this.forceUpdate();
  }

  render() {
    const notes = NoteStore.items.map((item)=> {
      return <Note note={item} key={item.id}/>;
    });
    return (
      <div className="note-list">{notes}</div>
    );
  }
}
```

## entry.jsx
该文件主要将NoteBox.jsx组件渲染到html容器中。

```javascript
/**
 * Created by xialei on 2016/3/23 0023.
 */
import ReactDOM from 'react-dom';
import NoteBox from './view/NoteBox';
import './css/style.scss';
ReactDOM.render(<NoteBox/>, document.querySelector('#content'));
```

## index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Title</title>
  <script src="./node_modules/react/dist/react-with-addons.js"></script>
</head>
<body>
  <div id="content"></div>
  <script src="http://localhost:8000/webpack-dev-server.js"></script>
  <script src="http://localhost:8000/assets/bundle.js"></script>
</body>
</html>
```

## 项目运行

```bash
webpack-dev-server --progress --colors --port 8000
```

[demo](http://ngdemo.sinaapp.com/react-notepad)