---
layout: post
title: android直接挂断电话
date: 2015-01-29 22:43:47.000000000 +08:00
type: post
published: true
status: publish
categories:
- android
tags:
- android
- hangup call
meta:
  _edit_last: '1'
  views: '2316'
  _wp_old_slug: android-han-gup
  _thumbnail_id: '241'
---
最近在写一个用来发短信的机器人（android),当然需要屏蔽所有来电了。多的话不说了，直接看步骤。（IDE为android studio）：
1.在 src/main下新建 aidl 目录。

2.在src/main/aidl下新建包 com.android.internal.telephony。

3.在com.android.internal.telephony新建文件 ITelephony.aidl，内容如下:

```java
/*
 * Copyright (C) 2007 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.internal.telephony;

import android.os.Bundle;
import java.util.List;
import android.telephony.NeighboringCellInfo;

/**
 * Interface used to interact with the phone.  Mostly this is used by the
 * TelephonyManager class.  A few places are still using this directly.
 * Please clean them up if possible and use TelephonyManager insteadl.
 *
 * {@hide}
 */
interface ITelephony {

    /**
     * Dial a number. This doesn't place the call. It displays
     * the Dialer screen.
     * @param number the number to be dialed. If null, this
     * would display the Dialer screen with no number pre-filled.
     */
    void dial(String number);

    /**
     * Place a call to the specified number.
     * @param number the number to be called.
     */
    void call(String number);

    /**
     * If there is currently a call in progress, show the call screen.
     * The DTMF dialpad may or may not be visible initially, depending on
     * whether it was up when the user last exited the InCallScreen.
     *
     * @return true if the call screen was shown.
     */
    boolean showCallScreen();

    /**
     * Variation of showCallScreen() that also specifies whether the
     * DTMF dialpad should be initially visible when the InCallScreen
     * comes up.
     *
     * @param showDialpad if true, make the dialpad visible initially,
     *                    otherwise hide the dialpad initially.
     * @return true if the call screen was shown.
     *
     * @see showCallScreen
     */
    boolean showCallScreenWithDialpad(boolean showDialpad);

    /**
     * End call or go to the Home screen
     *
     * @return whether it hung up
     */
    boolean endCall();

    /**
     * Answer the currently-ringing call.
     *
     * If there's already a current active call, that call will be
     * automatically put on hold.  If both lines are currently in use, the
     * current active call will be ended.
     *
     * TODO: provide a flag to let the caller specify what policy to use
     * if both lines are in use.  (The current behavior is hardwired to
     * "answer incoming, end ongoing", which is how the CALL button
     * is specced to behave.)
     *
     * TODO: this should be a oneway call (especially since it's called
     * directly from the key queue thread).
     */
    void answerRingingCall();

    /**
     * Silence the ringer if an incoming call is currently ringing.
     * (If vibrating, stop the vibrator also.)
     *
     * It's safe to call this if the ringer has already been silenced, or
     * even if there's no incoming call.  (If so, this method will do nothing.)
     *
     * TODO: this should be a oneway call too (see above).
     *       (Actually *all* the methods here that return void can
     *       probably be oneway.)
     */
    void silenceRinger();

    /**
     * Check if we are in either an active or holding call
     * @return true if the phone state is OFFHOOK.
     */
    boolean isOffhook();

    /**
     * Check if an incoming phone call is ringing or call waiting.
     * @return true if the phone state is RINGING.
     */
    boolean isRinging();

    /**
     * Check if the phone is idle.
     * @return true if the phone state is IDLE.
     */
    boolean isIdle();

    /**
     * Check to see if the radio is on or not.
     * @return returns true if the radio is on.
     */
    boolean isRadioOn();

    /**
     * Check if the SIM pin lock is enabled.
     * @return true if the SIM pin lock is enabled.
     */
    boolean isSimPinEnabled();

    /**
     * Cancels the missed calls notification.
     */
    void cancelMissedCallsNotification();

    /**
     * Supply a pin to unlock the SIM.  Blocks until a result is determined.
     * @param pin The pin to check.
     * @return whether the operation was a success.
     */
    boolean supplyPin(String pin);

    /**
     * Handles PIN MMI commands (PIN/PIN2/PUK/PUK2), which are initiated
     * without SEND (so dial is not appropriate).
     *
     * @param dialString the MMI command to be executed.
     * @return true if MMI command is executed.
     */
    boolean handlePinMmi(String dialString);

    /**
     * Toggles the radio on or off.
     */
    void toggleRadioOnOff();

    /**
     * Set the radio to on or off
     */
    boolean setRadio(boolean turnOn);

    /**
     * Request to update location information in service state
     */
    void updateServiceLocation();

    /**
     * Enable location update notifications.
     */
    void enableLocationUpdates();

    /**
     */
    void disableLocationUpdates();

    /**
     * Enable a specific APN type.
     */
    int enableApnType(String type);

    /**
     * Disable a specific APN type.
     */
    int disableApnType(String type);

    /**
     * Allow mobile data connections.
     */
    boolean enableDataConnectivity();

    /**
     * Disallow mobile data connections.
     */
    boolean disableDataConnectivity();

    /**
     * Report whether data connectivity is possible.
     */
    boolean isDataConnectivityPossible();

    Bundle getCellLocation();

    /**
     * Returns the neighboring cell information of the device.
     */
    List getNeighboringCellInfo();

     int getCallState();
     int getDataActivity();
     int getDataState();
}
```

4.android studio 菜单 Build->Rebuild project

5.在Activity中注册监听（写在onCreate()）

```java
TelephonyManager mTelephonyManager = (TelephonyManager) this
                .getSystemService(TELEPHONY_SERVICE);
        mTelephonyManager.listen(phoneStateListener,
                PhoneStateListener.LISTEN_CALL_STATE);
```

6.在Activity中新建以下方法以获得telephony的实例

```java
/**
     * @param context
     * @return
     */
    private static ITelephony getITelephony(Context context) {
        TelephonyManager mTelephonyManager = (TelephonyManager) context
                .getSystemService(TELEPHONY_SERVICE);
        Class c = TelephonyManager.class;
        Method getITelephonyMethod = null;
        try {
            getITelephonyMethod = c.getDeclaredMethod("getITelephony",
                    (Class[]) null); // 获取声明的方法
            getITelephonyMethod.setAccessible(true);
        } catch (SecurityException e) {
            e.printStackTrace();
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        }

        try {
            ITelephony iTelephony = (ITelephony) getITelephonyMethod.invoke(
                    mTelephonyManager, (Object[]) null); // 获取实例
            return iTelephony;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
```

7.在activity类中建立内部类

```java
PhoneStateListener phoneStateListener = new PhoneStateListener() {

        @Override
        public void onCallStateChanged(int state, String incomingNumber) {

            ITelephony iTelephony = getITelephony(MainActivity.this);
            switch (state) {
                case TelephonyManager.CALL_STATE_RINGING:
                    iTelephony = getITelephony(getApplicationContext()); //获取电话接口
                    if (iTelephony != null) {
                        try {
                            iTelephony.endCall(); // 挂断电话
                            Message msg = new Message();
                            msg.what = SYS_MSG;
                            msg.obj ="成功挂断["+incomingNumber+"]的电话";
                            handler.sendMessage(msg);
                        } catch (RemoteException e) {
                            Message msg = new Message();
                            msg.what = SYS_MSG;
                            msg.obj ="挂断["+incomingNumber+"]的电话失败";
                            handler.sendMessage(msg);
                        }
                    }
                    break;
                default:
                    break;
            }
        }

    };
```
