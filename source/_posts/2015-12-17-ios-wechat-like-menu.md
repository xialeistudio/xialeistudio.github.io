---
layout: post
title: ios仿微信右上角弹出菜单
date: 2015-12-17 12:41:42.000000000 +08:00
type: post
published: true
status: publish
categories:
- ios
---

## 项目地址
[ios仿微信右上角弹出菜单](https://github.com/xialeistudio/wechat-like-menu)
## 效果图
![效果图](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/12/2.gif)
## 实现过程
本人倾向于使用storyboard来做布局，所以实现起来也是不难的   
1.新建 Single View Application。

2.打开Main.storyboard。

3.选择默认的View Controller，点击菜单"Editor"=>"Embed In"=>"Navigation Controller",确认Navigation Controller是Initial View Controller。

4.拖两个viewController到Interface builder，并做好连接，效果如图1所示。
![图1](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/12/2.pic_.jpg)

5.选择第二个 Segue，属性设置如图2所示。   
![图2](https://og5r5kasb.qnssl.com/wp-content/uploads/2015/12/4.pic_.jpg)

6.打开ViewController.m，覆盖 prepareForSegue方法

```object-c
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
    if ([segue.identifier isEqualToString:@"showMenu"]) {
        UIViewController *viewController = segue.destinationViewController;
        if ([[[UIDevice currentDevice] systemVersion] floatValue] >= 8.0) {
            viewController.modalPresentationStyle = UIModalPresentationOverCurrentContext;
        } else {
            self.modalPresentationStyle = UIModalPresentationCurrentContext;
        }
    }
}
```

由于IOS8更换了Enum的名称，所以这里需要做下判断
7.新建Cocao Touch Class=>View2Controller

8.在Interface Builder中把第二个viewController的Class设置为View2Controller，并把“取消”按钮绑定到View2Controller.m

9.打开View2Controller.m

```object-c
//
//  View2Controller.m
//  viewtransition
//
//  Created by xialeistudio on 15/12/17.
//  Copyright © 2015年 Group Friend Information. All rights reserved.
//

#import "View2Controller.h"

@interface View2Controller ()
- (IBAction)cancelClicked:(id)sender;

@property(weak, nonatomic) IBOutlet UIView *menuView;

@end

@implementation View2Controller {
    UITapGestureRecognizer *_tap;
}
- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view.
    _tap = [[UITapGestureRecognizer alloc] init];
    [_tap addTarget:self action:@selector(closeView)];
    [self.view addGestureRecognizer:_tap];
}

- (void)closeView {
    _menuView.frame = CGRectMake(_menuView.frame.origin.x, self.view.frame.size.height - _menuView.frame.size.height, _menuView.frame.size.width, _menuView.frame.size.height);
    [UIView animateWithDuration:.3 delay:0 options:UIViewAnimationOptionCurveEaseInOut
                     animations:^{
                         _menuView.frame = CGRectMake(_menuView.frame.origin.x, self.view.frame.size.height, _menuView.frame.size.width, _menuView.frame.size.height);
                     }
                     completion:^(BOOL isFinished) {
                         if (isFinished) {
                             [self dismissViewControllerAnimated:NO completion:nil];
                         }
                     }];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (void)viewWillAppear:(BOOL)animated {
    _menuView.frame = CGRectMake(_menuView.frame.origin.x, self.view.frame.size.height, _menuView.frame.size.width, _menuView.frame.size.height);
    [UIView animateWithDuration:.3 animations:^{
        _menuView.frame = CGRectMake(_menuView.frame.origin.x, self.view.frame.size.height - _menuView.frame.size.height, _menuView.frame.size.width, _menuView.frame.size.height);
    }];
}

/*
#pragma mark - Navigation

// In a storyboard-based application, you will often want to do a little preparation before navigation
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
    // Get the new view controller using [segue destinationViewController].
    // Pass the selected object to the new view controller.
}
*/

- (IBAction)cancelClicked:(id)sender {
    [self closeView];
}
@end
```

关键是 viewWillAppear 和 closeView 中的动画处理。