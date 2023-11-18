---
slug: baidu-share-support-https
title: 百度分享不支持HTTPS解决办法
date: 2019-07-12 19:10:52
categories:
- Engineering
---

这两天接入文章页百度分享时发现本地可以显示分享按钮，但是发布到线上之后发现分享按钮不会展示。打开浏览器调试工具发现，HTTPS下的百度分享资源未加载，起初以为是HTTPS站点下面使用的是HTTP协议的链接，但是查看源代码发现是自适应协议的， 所以问题应该是处在百度这里。

打开`https://bdimg.share.baidu.com/static/api/js/share.js`发现浏览器提示`NET::ERR_CERT_COMMON_NAME_INVALID`，也就是`访问的域名和证书配置的域名不匹配`，证书的域名是`*.baidu.com`，访问的域名是`bdimg.share.baidu.com`，泛域名是不可以跨级使用的。

虽然是百度的问题，但是咱也不可能要他去改这个分享，所以只能自己来处理了。

## 可能的处理方案

1. 全站使用HTTP，放弃该方案（现在都9012年了，免费证书一大把，基本都是HTTPS站点了）
2. 将百度分享的资源打包下来进行部署
   1. 部署到自己的服务器（成本低，易迁移，但是服务器带宽是个问题）
   2. 部署到CDN，本文以七牛为例

## 资源路径

百度分享相关JS我已经分享到github了，[一键直达仓库](https://github.com/xialeistudio/baidu-share-resource)

## 处理过程

1. 将百度分享的资源解压到本地
2. 使用PHP遍历目录上传到七牛(本文用的SPL进行文件夹遍历)
3. 替换使用的百度分享JS路径

### 使用PHP变量目录上传到七牛

文件目录如下：

```
|--static(百度分享资源目录)
|--DirectorySync.php
|--FilterScanner.php
|--index.php
```

DirectorySync.php
```php

/**
 * 目录同步器
 * Class DirectorySync
 * @package sync
 * @author xialeistudio
 * @date 2019-07-11
 */
class DirectorySync
{
    private $accessKey;
    private $secretKey;
    private $bucket;

    /**
     * @var Auth
     */
    private $auth;

    /**
     * DirectorySync constructor.
     * @param $accessKey
     * @param $secretKey
     * @param $bucket
     */
    public function __construct($accessKey, $secretKey, $bucket)
    {
        $this->accessKey = $accessKey;
        $this->secretKey = $secretKey;
        $this->bucket = $bucket;
        $this->auth = new Auth($accessKey, $secretKey);
    }


    /**
     * 同步目录
     * @param array $list
     * @throws \Exception
     * @author xialeistudio
     * @date 2019-07-11
     */
    public function sync(array $list)
    {
        $uploader = new UploadManager();
        $token = $this->auth->uploadToken($this->bucket);
        foreach ($list as $path => $keyPrefix) {
            $scanner = new FilterScanner($path);
            foreach ($scanner as $filename) {
                printf("uploading %s \n", $filename);
                /** @var Error $error */
                list($ret, $error) = $uploader->putFile($token, $keyPrefix . $filename, $filename);
                if (!empty($error)) {
                    printf("uploading %s error: %s\n", $filename, $error->message());
                }
            }
        }
    }
}
```

FilterScanner.php
```php
/**
 * 文件扫描器
 * Class FilterScanner
 * @package sync
 * @author xialeistudio
 * @date 2019-07-11
 */
class FilterScanner extends FilterIterator
{
    /**
     * FilterScanner constructor.
     * @param $path
     */
    public function __construct($path)
    {
        parent::__construct(new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path)));
    }

    /**
     * Check whether the current element of the iterator is acceptable
     * @link https://php.net/manual/en/filteriterator.accept.php
     * @return bool true if the current element is acceptable, otherwise false.
     * @since 5.1.0
     */
    public function accept()
    {
        return substr($this->current(), -1, 1) != '.' && substr($this->current(), -2, 2) != '..';
    }
}
```

index.php

```php
$sync = new DirectorySync(ACCESS_KEY, SECRET_KEY, BUCKET);
$sync->sync([
    'static' => ''
]);
```

上传之前需要修改一下百度分享js相关的域名。打开`static/api/js/share.js`，搜索到如下代码：

```js
jscfg: {domain: {staticUrl: "/"}}
```

将`staticUrl`改成七牛的域名，本站使用的是`static.ddhigh.com`，所以改完之后的代码如下：

```js
jscfg: {domain: {staticUrl: "//static.ddhigh.com/"}}
```

完事之后执行`php index.php`上传到七牛，此时就可以随意部署了~。

## 部署到应用

将以往使用`bdimg.share.baidu.com/static/api/js/share.js`的地方换成`//static.ddhigh.com/static/api/js/share.js`即可，其他资源会自动加载。

*本站的CDN域名做了防盗链处理，各位如果直接用我的share.js链接是会有问题的*

## hexo Next百度分享的额外处理

上传到七牛这个步骤完成之后，搜索文件`baidushare.swig`，找到最下面的如下代码：

```js
with(document)0[(getElementsByTagName('head')[0]||body).appendChild(createElement('script')).src='//bdimg.share.baidu.com/static/api/js/share.js?cdnversion='+~(-new Date()/36e5)];
```

将链接替换为自己的CDN链接，我这边替换后的结果如下：

```js
with(document)0[(getElementsByTagName('head')[0]||body).appendChild(createElement('script')).src='//static.ddhigh.com/static/api/js/share.js?cdnversion='+~(-new Date()/36e5)];
```
