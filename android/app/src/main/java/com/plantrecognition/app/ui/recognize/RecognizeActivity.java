package com.plantrecognition.app.ui.recognize;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.util.Log;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;
import com.plantrecognition.app.R;
import com.plantrecognition.app.ui.result.ResultActivity;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

public class RecognizeActivity extends AppCompatActivity {

    private static final String TAG = "RecognizeActivity";
    private static final int REQUEST_CAMERA_PERMISSION = 100;
    private static final int REQUEST_STORAGE_PERMISSION = 101;
    private static final int REQUEST_IMAGE_CAPTURE = 102;
    private static final int REQUEST_IMAGE_PICK = 103;

    private boolean fromCamera;
    private Uri photoUri;  // 保存完整分辨率照片的URI

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        fromCamera = getIntent().getBooleanExtra("from_camera", true);

        if (fromCamera) {
            checkCameraPermission();
        } else {
            checkStoragePermission();
        }
    }

    private void checkCameraPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.CAMERA}, REQUEST_CAMERA_PERMISSION);
        } else {
            openCamera();
        }
    }

    private void checkStoragePermission() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_MEDIA_IMAGES) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_MEDIA_IMAGES}, REQUEST_STORAGE_PERMISSION);
            } else {
                openGallery();
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_EXTERNAL_STORAGE}, REQUEST_STORAGE_PERMISSION);
            } else {
                openGallery();
            }
        }
    }

    private void openCamera() {
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

        // 创建临时文件保存完整分辨率照片
        try {
            File photoFile = createImageFile();
            if (photoFile != null) {
                // 使用FileProvider获取URI（Android 7.0+需要）
                photoUri = FileProvider.getUriForFile(
                    this,
                    getApplicationContext().getPackageName() + ".fileprovider",
                    photoFile
                );

                // 指定输出位置，相机会保存完整分辨率图像
                intent.putExtra(MediaStore.EXTRA_OUTPUT, photoUri);

                Log.d(TAG, "相机将保存完整图像到: " + photoFile.getAbsolutePath());
                startActivityForResult(intent, REQUEST_IMAGE_CAPTURE);
            } else {
                Toast.makeText(this, "无法创建临时文件", Toast.LENGTH_SHORT).show();
                finish();
            }
        } catch (Exception e) {
            Log.e(TAG, "打开相机失败", e);
            Toast.makeText(this, "无法打开相机: " + e.getMessage(), Toast.LENGTH_SHORT).show();
            finish();
        }
    }

    /**
     * 创建临时图像文件
     */
    private File createImageFile() {
        try {
            String imageFileName = "PHOTO_" + System.currentTimeMillis() + ".jpg";
            File storageDir = getCacheDir();
            return new File(storageDir, imageFileName);
        } catch (Exception e) {
            Log.e(TAG, "创建图像文件失败", e);
            return null;
        }
    }

    private void openGallery() {
        Intent intent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        startActivityForResult(intent, REQUEST_IMAGE_PICK);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_CAMERA_PERMISSION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                openCamera();
            } else {
                Toast.makeText(this, "需要相机权限", Toast.LENGTH_SHORT).show();
                finish();
            }
        } else if (requestCode == REQUEST_STORAGE_PERMISSION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                openGallery();
            } else {
                Toast.makeText(this, "需要存储权限", Toast.LENGTH_SHORT).show();
                finish();
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode == RESULT_OK) {
            if (requestCode == REQUEST_IMAGE_CAPTURE) {
                // 使用完整分辨率图像（已保存到photoUri指定的文件）
                if (photoUri != null) {
                    String imagePath = getPathFromUri(photoUri);
                    if (imagePath != null) {
                        Log.d(TAG, "相机拍摄完成，图像路径: " + imagePath);
                        goToResult(imagePath);
                    } else {
                        Toast.makeText(this, "无法读取照片", Toast.LENGTH_SHORT).show();
                        finish();
                    }
                } else {
                    Toast.makeText(this, "照片保存失败", Toast.LENGTH_SHORT).show();
                    finish();
                }
            } else if (requestCode == REQUEST_IMAGE_PICK && data != null) {
                Uri imageUri = data.getData();
                if (imageUri != null) {
                    String imagePath = getPathFromUri(imageUri);
                    if (imagePath != null) {
                        Log.d(TAG, "从相册选择图像: " + imagePath);
                        goToResult(imagePath);
                    } else {
                        Toast.makeText(this, "无法读取图片", Toast.LENGTH_SHORT).show();
                        finish();
                    }
                }
            }
        } else {
            finish();
        }
    }

    private String getPathFromUri(Uri uri) {
        try {
            InputStream inputStream = getContentResolver().openInputStream(uri);
            if (inputStream == null) {
                Log.e(TAG, "无法打开URI: " + uri);
                return null;
            }

            File file = new File(getCacheDir(), "temp_image_" + System.currentTimeMillis() + ".jpg");
            try (OutputStream outputStream = new FileOutputStream(file)) {
                byte[] buffer = new byte[4096];
                int length;
                while ((length = inputStream.read(buffer)) > 0) {
                    outputStream.write(buffer, 0, length);
                }
            }
            inputStream.close();

            Log.d(TAG, "图像已复制到: " + file.getAbsolutePath() + ", 大小: " + file.length() + " bytes");
            return file.getAbsolutePath();
        } catch (IOException e) {
            Log.e(TAG, "读取URI失败", e);
            return null;
        }
    }

    private void goToResult(String imagePath) {
        if (imagePath != null) {
            Intent intent = new Intent(this, ResultActivity.class);
            intent.putExtra("image_path", imagePath);
            intent.putExtra("from_camera", fromCamera);
            startActivity(intent);
        } else {
            Toast.makeText(this, "图像路径无效", Toast.LENGTH_SHORT).show();
        }
        finish();
    }
}
