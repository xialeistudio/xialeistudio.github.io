{%if theme.group.enabled %}
<div style="margin-top:8px">
    {%if theme.group.qq %}
    <div>
    <i class="fa fa-qq"></i> QQ交流群
    <strong style="color:red;display:block">{{theme.group.qq}}</strong>
    </div>
    {% endif %}

    {%if theme.group.wechat %}
    <div style="margin-top:4px">
        <i class="fa fa-wechat"></i> 微信交流群
        <img width="100" height="100" src="{{theme.group.wechat}}" class="qrcode" /> 
    </div>
    {% endif %}
    <div>{{theme.group.text}}</div>
</div> 
{% endif %}