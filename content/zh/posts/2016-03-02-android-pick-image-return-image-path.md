---
slug: android-pick-image-return-image-path
title: android选择图片返回统一图片地址
date: 2016-03-02 18:43:34.000000000 +08:00
categories:
- Engineering
---
android从选择图片有两种方法，但是返回值确不同，本文将指导大家如何统一这两种方式的返回值。

```java
//关键代码
@Event(R.id.btnPhoto)
   private void onBtnPhotoClicked(View view) {
       Intent intent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
       startActivityForResult(intent, Config.Constants.CODE_PICK_IMAGE_FROM_PHOTO);
   }

   @Event(R.id.btnCamera)
   private void onBtnCameraClicked(View view) {
       Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
       startActivityForResult(intent, Config.Constants.CODE_PICK_IMAGE_FROM_CAMERA);
   }
   
   @Override
   protected void onActivityResult(int requestCode, int resultCode, Intent data) {
       switch (requestCode) {
           case Config.Constants.CODE_PICK_IMAGE_FROM_CAMERA:
               if (data != null && data.hasExtra("data")) {
                   Bitmap bitmap = data.getParcelableExtra("data");
                   bitmap = BitmapUtil.scale(bitmap, 640.0f / bitmap.getWidth());
                   try {
                       File path = new File(((MyApplication) getApplication()).appPath, DateUtil.format(new Date(), "yyyyMMddHHmmss") + ".jpg");
                       FileOutputStream outputStream = new FileOutputStream(path);
                       bitmap.compress(Bitmap.CompressFormat.JPEG, 100, outputStream);
                       outputStream.close();
                       Intent intent = new Intent();
                       intent.putExtra("path", path.getAbsolutePath());
                       setResult(RESULT_OK, intent);
                   } catch (IOException e) {
                        e.printStackTrace();
                   }
               }
               finish();
               break;
           case Config.Constants.CODE_PICK_IMAGE_FROM_PHOTO:
               if(data != null){
                   Uri uri = data.getData();
                   Bitmap bitmap;
                   ContentResolver contentResolver = getContentResolver();
                   try {
                       bitmap = MediaStore.Images.Media.getBitmap(contentResolver, uri);
                       bitmap = BitmapUtil.scale(bitmap, 640.0f / bitmap.getWidth());
                       File path = new File(((MyApplication) getApplication()).appPath, DateUtil.format(new Date(), "yyyyMMddHHmmss") + ".jpg");
                       FileOutputStream outputStream = new FileOutputStream(path);
                       bitmap.compress(Bitmap.CompressFormat.JPEG, 100, outputStream);
                       outputStream.close();
                       Intent intent = new Intent();
                       intent.putExtra("path", path.getAbsolutePath());
                       setResult(RESULT_OK, intent);
                   } catch (IOException e) {
                       e.printStackTrace();
                   }
               }
               finish();
               break;
           default:
               super.onActivityResult(requestCode, resultCode, data);
       }
   }
//BitmapUtil.java
public static Bitmap scale(Bitmap bitmap, float scale) {
    Matrix matrix = new Matrix();
    matrix.postScale(scale, scale);
    return Bitmap.createBitmap(bitmap, 0, 0, bitmap.getWidth(), bitmap.getHeight(), matrix, true);
}

//MyApplication
public File appPath;

@Override
public void onCreate() {
    super.onCreate();
    //创建目录
    appPath = new File(Environment.getExternalStorageDirectory(), getPackageName());
    if (!appPath.isDirectory()) {
        appPath.mkdir();
    }
}
```

经过统一处理之后，返回值均为图片的绝对路径地址。