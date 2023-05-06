---
title: golang multipart上传文件到远端（如上传微信临时素材）
date: 2018-03-01 15:51:02
categories:
- Engineering
---

最近在开发一个关注之后通过客服消息推送一张海报给用户的功能，海报图片是本地生成好的，需要上传到微信临时素材之后通过客服消息推送给用户。
上传文件需要`multipart/form-data`格式的表单，所以golang默认的http.POST方法是实现不了的。需要自行实现body参数逻辑。

## 上传请求初始化

```golang
// 新建上传请求
func NewUploadRequest(link string, params map[string]string, name, path string) (*http.Request, error) {
	fp, err := os.Open(path) // 打开文件句柄
	if err != nil {
		return nil, err
	}
	defer fp.Close()
	body := &bytes.Buffer{} // 初始化body参数
	writer := multipart.NewWriter(body) // 实例化multipart
	part, err := writer.CreateFormFile(name, filepath.Base(path)) // 创建multipart 文件字段
	if err != nil {
		return nil, err
	}
	_, err = io.Copy(part, fp) // 写入文件数据到multipart
	for key, val := range params {
		_ = writer.WriteField(key, val) // 写入body中额外参数，比如七牛上传时需要提供token
	}
	err = writer.Close()
	if err != nil {
		return nil, err
	}
	req, err := http.NewRequest("POST", link, body) // 新建请求
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "multipart/form-data") // 设置请求头,!!!非常重要，否则远端无法识别请求
	return req, nil
}
```

## 上传流程

```golang
func (m *Task) upload(appid string) (string, error) {
	filename, err := m.download() // 下载远端海报文件到本地路径
	if err != nil {
		return "", err
	}
	// 获取accessToken
	accessToken, err := m.passport.GetAccessToken(appid)
	if err != nil {
		return "", err
	}
	params := &url.Values{
		"access_token": []string{accessToken},
		"type":         []string{"image"},
	}
	req, err := util.NewUploadRequest("https://api.weixin.qq.com/cgi-bin/media/upload?"+params.Encode(), nil, "media", filename) // 上传到微信
	if err != nil {
		return "", err
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	ret := make(map[string]interface{})
	if err := json.NewDecoder(resp.Body).Decode(&ret); err != nil {
		return "", err
	}
	if mediaId, ok := ret["media_id"]; ok {
		return mediaId.(string), nil
	} else if errmsg, ok := ret["errmsg"]; ok {
		return "", errors.New(errmsg.(string))
	} else {
		return "", errors.New("上传失败")
	}
}
```