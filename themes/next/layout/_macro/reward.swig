<div style="padding: 10px 0; margin: 20px auto; width: 90%; text-align: center;">
  <div>{{ theme.reward_comment }}</div>
  <div id="QR">

    {% if theme.wechatpay %}
      <div id="wechat" style="display: inline-block">
        <img id="wechat_qr" width="150" src="{{ theme.wechatpay }}" alt="{{ theme.author }} {{ __('reward.wechatpay') }}"/>
        <p>{{ __('reward.wechatpay') }}</p>
      </div>
    {% endif %}

    {% if theme.alipay %}
      <div id="alipay" style="display: inline-block">
        <img id="alipay_qr" width="150" src="{{ theme.alipay }}" alt="{{ theme.author }} {{ __('reward.alipay') }}"/>
        <p>{{ __('reward.alipay') }}</p>
      </div>
    {% endif %}

    {% if theme.bitcoin %}
      <div id="bitcoin" style="display: inline-block">
        <img id="bitcoin_qr" src="{{ theme.bitcoin }}" alt="{{ theme.author }} {{ __('reward.bitcoin') }}"/>
        <p>{{ __('reward.bitcoin') }}</p>
      </div>
    {% endif %}

  </div>
</div>
