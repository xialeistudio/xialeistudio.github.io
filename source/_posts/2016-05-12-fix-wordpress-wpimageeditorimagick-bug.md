---
layout: post
title: wordpress WPImageEditorImagick 漏洞临时修复方案
date: 2016-05-12 14:05:35.000000000 +08:00
type: post
published: true
status: publish
categories:
- Engineering
tags:
- wordpress
---
4.5.1存在该漏洞，但是更新到4.5.2发现漏洞依旧存在。   
临时修复方案如下：   
文件路径：

```
/wp-includes/media.php的_wp_image_editor_choose
```

将

```php
$implementations = apply_filters( 'wp_image_editors', array( 'WP_Image_Editor_Imagick' ,'WP_Image_Editor_GD' ) );
```

改为

```php
$implementations = apply_filters( 'wp_image_editors', array(  'WP_Image_Editor_GD', 'WP_Image_Editor_Imagick' ) );
```

*此方法为临时解决方案，请大家及时更新最新版本的wordpress*