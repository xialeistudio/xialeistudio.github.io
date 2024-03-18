---
slug: android-datepickertimepicker-display-inline
title: android datepicker和timepicker显示在一行
date: 2014-11-19 23:54:52.000000000 +08:00
categories:
- Engineering
---
android默认的datepicker和默认的timepicker可以放在一行（Linelayout），但是timepicker右边会“挤出”屏幕，尝试设置layout_weight和layout_height对于布局有效，但是控件显示就不完整了。到这一步发现xml不局文件已经处理不了，所以自然想到应该利用java来处理了。

## 效果图
![效果图](https://og5r5kasb.qnssl.com/wp-content/uploads/2014/11/98281416412408.jpg)
## 布局代码

```xml
<LinearLayout
    android:orientation="horizontal"
    android:layout_width="fill_parent"
    android:layout_height="fill_parent"
    android:paddingLeft="10dp">

    <DatePicker
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:id="@+id/datePicker"
    android:calendarViewShown="false" />

    <TimePicker
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:id="@+id/timePicker" />
</LinearLayout>
```

## JAVA代码
### UI.java

```java
public static void resizePicker(FrameLayout tp) {
        List<NumberPicker> npList = findNumberPicker(tp);
        for (NumberPicker np : npList) {
            resizeNumberPicker(np);
        }
}

private static List<NumberPicker> findNumberPicker(ViewGroup viewGroup) {
        List<NumberPicker> npList = new ArrayList<NumberPicker>();
        View child = null;
        if (null != viewGroup) {
            for (int i = 0; i < viewGroup.getChildCount(); i++) {
                child = viewGroup.getChildAt(i);
                if (child instanceof NumberPicker) {
                    npList.add((NumberPicker) child);
                } else if (child instanceof LinearLayout) {
                    List<NumberPicker> result = findNumberPicker((ViewGroup) child);
                    if (result.size() > 0) {
                        return result;
                    }
                }
            }
        }
        return npList;
}

private static void resizeNumberPicker(NumberPicker np) {
   LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(100, RadioGroup.LayoutParams.WRAP_CONTENT);
   params.setMargins(10, 0, 10, 0);
   np.setLayoutParams(params);
}
```

## Main.java
View的查找自己应该知道写了。

```java
UI.resizePicker(datePicker);
UI.resizePicker(timePicker);

datePicker.setMinDate(System.currentTimeMillis() - 1000);
datePicker.init(year, monthOfYear, dayOfMonth, new DatePicker.OnDateChangedListener() {

public void onDateChanged(DatePicker view, int year,
                          int monthOfYear, int dayOfMonth) {
                //得到时间
                String time = timePicker.getCurrentHour() + ":" + timePicker.getCurrentMinute();
                datetime = year + "-" + (monthOfYear + 1) + "-" + dayOfMonth + " " + time;
            }

        });

        timePicker.setIs24HourView(true);
        timePicker.setOnTimeChangedListener(new TimePicker.OnTimeChangedListener() {
            public void onTimeChanged(TimePicker view, int hourOfDay, int minute) {
                String date = datePicker.getYear() + "-" + 
                (datePicker.getMonth() + 1) + 
                "-" + datePicker.getDayOfMonth();
                datetime = date + " " + 
                timePicker.getCurrentHour() + ":" + 
                timePicker.getCurrentMinute();
            }
        });
```

## 原理
datepicker和timepicker都是继承FrameLayout，内部为很多NumberPicker，所以，查找到所有NumberPicker的List，然后设置样式即可。