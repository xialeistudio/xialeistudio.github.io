---
slug: fix-gittalk-github
title: 修复GitTalk出现Forbidden问题
date: 2021-02-25 12:00:23
categories:
- Engineering
tags:
- gittalk
---

## GitTalk失效原因

对于所有自建博客的博主来书，GitTalk应该不陌生。GitTalk通过Github的OpenAPI以及issues功能实现社区评论，确实是一大亮点。

今天在查看文章的时候发现评论区出现了Forbidden错误，通过检查网络请求发现获取Github Token时请求了以下链接

```
https://cors-anywhere.herokuapp.com/https://github.com/login/oauth/access_token
```

通过查询GitTalk官方文档发现github.com的oauth是不允许跨域请求的，cors-anywhere.herokuapp.com是一个第三方提供的CORS代理服务，会默认放行所有CORS请求。目前由于该CORS代理服务遭到滥用，因此做了限制，导致GitTalk失效。

## 解决方案

> 通过自己的nginx进行反向代理转发即可。

### 修改gitalk初始化参数

笔者使用的是hexo+icarus主题，其他主题或者博客系统也是类似做法。

编辑themes/icarus/layout/comment/gitalk.ejs

```javascript
<script>
    var gitalk = new Gitalk({
        clientID: '<%= get_config('comment.client_id') %>',
        clientSecret: '<%= get_config('comment.client_secret') %>',
        id: '<%= md5(page.path) %>',
        repo: '<%= get_config('comment.repo') %>',
        owner: '<%= get_config('comment.owner') %>',
        admin: <%- JSON.stringify(get_config('comment.admin'))%>,
        createIssueManually: <%= get_config('comment.create_issue_manually', false) %>,
        distractionFreeMode: <%= get_config('comment.distraction_free_mode', false) %>,
        proxy: '/github/login/oauth/access_token' // 新添加的
    })
    gitalk.render('comment-container')
</script>
```

### nginx配置

编辑nginx配置，笔者的博客域名为www.ddhigh.com，因此需要限制CORS来源域名，否则将有盗用风险!

```nginx
location /github {
	add_header Access-Control-Allow-Origin www.ddhigh.com;
  add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
  add_header Access-Control-Allow-Headers 'DNT,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization';
  if ($request_method = 'OPTIONS') {
  	return 204;
  }
  proxy_pass https://github.com/; # 尾部斜杠不能少
}
```

执行nginx -s reload配置。

### 访问测试

访问新写的文章https://www.ddhigh.com/2021/02/25/golang-get-started.html，可以看到界面上已经正常了。

![image-20210225121050348](https://static.ddhigh.com/blog/2021-02-25-121050-2.png)

查看Chrome网络状况，可以看到已经走了自己配置的CORS跨域了。

```
Request URL: https://www.ddhigh.com/github/login/oauth/access_token
Request Method: POST
Status Code: 200 
Remote Address: 106.52.24.199:443
Referrer Policy: strict-origin-when-cross-origin
```

