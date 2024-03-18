---
slug: ios-scrollview-autolayout
title: ios ScrollView AutoLayout
date: 2016-06-02 08:13:49.000000000 +08:00
categories:
- Engineering
---
XCode的Interface Builder解决了开发者使用代码进行布局的问题，但是在使用 **ScrollView** 时，如果没有方法，IB中的layout是会乱掉的，在网上查找资料加上自己的实际操作之后，总结了以下步骤：
1. 在根view中添加好子控件，排好版
2. 选中所有子控件，选择菜单 *Editor In* => *View*，命名为 **contentView**，此时编辑器会报警，暂时不理会
3. 给contentView添加上下左右4个约束，值全部为**0**
4. 选择contentView，选择菜单 *Editor In* => *ScrollView*
5. 设置ScrollView的上下左右4个约束，值全部为**0**
6. 给contentView加上height约束，并在Interface Builder中设置合适的约束值。

