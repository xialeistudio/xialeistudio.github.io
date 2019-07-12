{%if theme.group.enabled %}
<div class="sidebar-group">
    {%if theme.group.qq %}
    <div>
    <i class="fa fa-qq"></i> QQ交流群
    <strong class="block">{{theme.group.qq}}</strong>
    </div>
    {% endif %}

    {%if theme.group.wechat %}
    <div>
        <i class="fa fa-wechat"></i> 微信交流群
        <img width="100" height="100" src="{{theme.group.wechat}}" class="qrcode" /> 
    </div>
    {% endif %}
    <div>{{theme.group.text}}</div>
</div> 
{% endif %}