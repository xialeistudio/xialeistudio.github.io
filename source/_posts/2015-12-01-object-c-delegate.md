---
layout: post
title: object-c委托实例
date: 2015-12-01 15:41:45.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
---
## 定义

+ delegate是一种设计模式，不是object-c特有
+ object-c通过protocol实现delegat

## 作用
+ 业务逻辑解耦
+ 加强程序可读性

## 使用
1. 声明protocol
2. 实现protocol
3. 指定delegate
4. 调用delegate方法

## 实例
本文以UIImagePickerController举例。   
UIImagePickerController本身需要实现<UIImagePickerControllerDelegate,UINavigationControllerDelegate>两个protocol，本文为了解释delegate的工作过程，在此之上封装一层。   
1.新建cocoa touch class 继承NSObject，命名UITool   

### UITool.h
```object-c
UITool.h

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

enum{
    ImageErrorUnSupportedSourceType = -1//不支持的来源类型
}ImageError;
@protocol ToolImageDelegate <NSObject>
/**
 *  选择图片回调
 *
 *  @param info 图片数据
 */
-(void)didSelectImage:(NSDictionary *)info;

@end

@interface UITool : NSObject
<UIImagePickerControllerDelegate,UINavigationControllerDelegate>
{
    id<ToolImageDelegate>imageDelegate;
}
/**
 *  单例
 *
 *  @return 单例
 */
+(instancetype)sharedManager;
/**
 *  选择图片
 *
 *  @param sourceType     来源类型
 *  @param viewController 视图
 *  @param error          错误
 *
 *  @return 是否出错
 */
-(BOOL)selectPicture
                :(UIImagePickerControllerSourceType)sourceType
                :(UIViewController<ToolImageDelegate> *)viewController
                :(NSError **)error;
@end
```

## UITool.m

```object-c
UITool.m
#import "UITool.h"
/**
 *  单例
 *
 *  @return 单例
 */
+(instancetype)sharedManager{
    static UITool *instance         = nil;
    static dispatch_once_t predicate;
    dispatch_once(&predicate,^{
    instance                        = [[self alloc]init];
    });
    return instance;
}
/**
 *  选择图片
 *
 *  @param sourceType     来源地址
 *  @param viewController 视图
 *  @param error          错误
 *
 *  @return 是否成功
 */
-(BOOL)selectPicture:(UIImagePickerControllerSourceType)sourceType :(UIViewController<ToolImageDelegate> *)viewController :(NSError **)error{
    if (![UIImagePickerController isSourceTypeAvailable:sourceType]) {
        NSDictionary *info  = [NSDictionary dictionaryWithObject:@"UnSupported source type" forKey:NSLocalizedDescriptionKey];
        *error = [NSError errorWithDomain:@"com.xialeistudio.core.UITool" code:ImageErrorUnSupportedSourceType userInfo:info];
        return NO;
    }
    
    //委托处理
    imageDelegate = viewController;
    
    UIImagePickerController *picker = [[UIImagePickerController alloc] init];
    picker.sourceType = sourceType;
    picker.allowsEditing= YES;
    picker.delegate = self;
    [viewController presentViewController:picker animated:YES completion:nil];
    return YES;
}

/**
 *  取消图片选择回调
 *
 *  @param picker 图片选择器
 */
-(void)imagePickerControllerDidCancel:(UIImagePickerController *)picker{
    [picker dismissViewControllerAnimated:YES completion:^{
        [imageDelegate didSelectImage:nil];
    }];
}
/**
 *  图片成功回调
 *
 *  @param picker 图片选择器
 *  @param info   回调数据
 */
-(void)imagePickerController:(UIImagePickerController *)picker didFinishPickingMediaWithInfo:(NSDictionary<NSString *,id> *)info{
    [picker dismissViewControllerAnimated:YES completion:^{
        [imageDelegate didSelectImage:info];
    }];
}
@end
```

按照**委托的使用4步**来说，我们自定义的委托已经实现了两步。   
**imageDelegate**就是我们的delegate，只要实现了该委托的子类，我们调用**didSelectImage**方法就不会出错。

### 视图
打开Interface Builder，放入一个button和一个ImageView，并做好输出口连接。

### ViewController.h

```object-c
ViewController.h
#import <UIKit/UIKit.h>
#import "UITool.h"

@interface ImagePickerViewController : UIViewController
<ToolImageDelegate>
- (IBAction)fromCamera:(id)sender;
@property (weak, nonatomic) IBOutlet UIImageView *cameraImage;

@end
```

### ViewController.m

```object-c
ViewController.m

#import "ImagePickerViewController.h"

@interface ImagePickerViewController ()

@end

@implementation ImagePickerViewController

- (void)viewDidLoad {
    [super viewDidLoad];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
}


- (IBAction)fromCamera:(id)sender {
    NSError *error = nil;
    if (![[UITool sharedManager] selectPicture:UIImagePickerControllerSourceTypeCamera :self :&error]) {
        NSLog(@"error:%@",[error localizedDescription]);
    }
}

-(void)didSelectImage:(NSDictionary *)info{
    if (info ==nil) {
        NSLog(@"未选择图片");
    }else{
        UIImage *originImage = [info objectForKey:UIImagePickerControllerOriginalImage];
        [self.cameraImage setImage:originImage];
    }
}
@end
```

### 总结
 在调用UITool的selectPicture方法时第二个参数(UIViewController<ToolImageDelegate> *)，强制要求传入的viewController实现ToolImageDelegate协议，在UIImagePickerController回调成功之后就会执行imagePickerControllerDidCancel和didFinishPickingMediaWithInfo方法，由于我们在该方法中进行了委托方法的调用，所以最终会执行ViewController的didSelectImage方法。