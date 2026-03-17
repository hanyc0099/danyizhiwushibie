package com.plantrecognition.app.ui.result;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.media.ExifInterface;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;
import com.plantrecognition.app.R;
import com.plantrecognition.app.network.ApiClient;
import com.plantrecognition.app.network.ApiResponse;
import com.plantrecognition.app.network.HistoryRecord;
import com.plantrecognition.app.network.UploadResponse;
import com.plantrecognition.app.recognition.LocalPlantRecognizerTFLite;
import com.plantrecognition.app.utils.UserManager;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ResultActivity extends AppCompatActivity {

    private static final String TAG = "ResultActivity";
    private ImageView ivPlantImage;
    private TextView tvPlantName;
    private TextView tvScientificName;
    private TextView tvConfidence;
    private TextView tvDescription;
    private View progressBar;
    private ImageView btnSave;
    private CardView cardSimilar;

    private String imagePath;
    private boolean fromCamera;
    private LocalPlantRecognizerTFLite localRecognizer;
    private ExecutorService executorService;
    private UserManager userManager;
    
    private int plantId;
    private int classId;
    private String plantName;
    private float confidence;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_result);

        imagePath = getIntent().getStringExtra("image_path");
        fromCamera = getIntent().getBooleanExtra("from_camera", false);

        // 初始化本地识别器 (TensorFlow Lite版本)
        localRecognizer = new LocalPlantRecognizerTFLite(this);
        executorService = Executors.newSingleThreadExecutor();
        userManager = UserManager.getInstance(this);

        initViews();
        setListeners();
        loadImage();
        recognizeImage();
    }

    private void initViews() {
        ivPlantImage = findViewById(R.id.ivPlantImage);
        tvPlantName = findViewById(R.id.tvPlantName);
        tvScientificName = findViewById(R.id.tvScientificName);
        tvConfidence = findViewById(R.id.tvConfidence);
        tvDescription = findViewById(R.id.tvDescription);
        progressBar = findViewById(R.id.progressBar);
        btnSave = findViewById(R.id.btnSave);
        cardSimilar = findViewById(R.id.cardSimilar);
    }

    private void setListeners() {
        findViewById(R.id.btnBack).setOnClickListener(v -> finish());
        findViewById(R.id.btnRetry).setOnClickListener(v -> recognizeImage());
        btnSave.setOnClickListener(v -> saveHistory());
    }

    private void loadImage() {
        if (imagePath != null) {
            Bitmap bitmap = loadBitmapWithCorrectOrientation(imagePath);
            if (bitmap != null) {
                ivPlantImage.setImageBitmap(bitmap);
            }
        }
    }

    /**
     * 加载图像并根据EXIF信息校正方向
     */
    private Bitmap loadBitmapWithCorrectOrientation(String path) {
        try {
            // 读取EXIF信息
            ExifInterface exif = new ExifInterface(path);
            int orientation = exif.getAttributeInt(
                ExifInterface.TAG_ORIENTATION,
                ExifInterface.ORIENTATION_NORMAL
            );

            Log.d(TAG, "图像EXIF方向: " + orientation);

            // 加载原始图像
            Bitmap bitmap = BitmapFactory.decodeFile(path);
            if (bitmap == null) {
                Log.e(TAG, "无法加载图像: " + path);
                return null;
            }

            // 根据EXIF方向旋转图像
            Matrix matrix = new Matrix();
            switch (orientation) {
                case ExifInterface.ORIENTATION_ROTATE_90:
                    Log.d(TAG, "旋转90度");
                    matrix.postRotate(90);
                    break;
                case ExifInterface.ORIENTATION_ROTATE_180:
                    Log.d(TAG, "旋转180度");
                    matrix.postRotate(180);
                    break;
                case ExifInterface.ORIENTATION_ROTATE_270:
                    Log.d(TAG, "旋转270度");
                    matrix.postRotate(270);
                    break;
                case ExifInterface.ORIENTATION_FLIP_HORIZONTAL:
                    Log.d(TAG, "水平翻转");
                    matrix.postScale(-1, 1);
                    break;
                case ExifInterface.ORIENTATION_FLIP_VERTICAL:
                    Log.d(TAG, "垂直翻转");
                    matrix.postScale(1, -1);
                    break;
                default:
                    Log.d(TAG, "无需旋转");
                    return bitmap;
            }

            // 应用变换
            Bitmap rotatedBitmap = Bitmap.createBitmap(
                bitmap, 0, 0, bitmap.getWidth(), bitmap.getHeight(), matrix, true
            );

            // 释放原始bitmap
            if (rotatedBitmap != bitmap) {
                bitmap.recycle();
            }

            return rotatedBitmap;
        } catch (IOException e) {
            Log.e(TAG, "读取EXIF信息失败", e);
            // 如果读取EXIF失败，直接返回原始图像
            return BitmapFactory.decodeFile(path);
        }
    }

    private void recognizeImage() {
        progressBar.setVisibility(View.VISIBLE);
        tvPlantName.setText("识别中...");

        executorService.execute(() -> {
            // 使用相同的方法加载图像，确保方向正确
            Bitmap bitmap = loadBitmapWithCorrectOrientation(imagePath);
            if (bitmap != null) {
                Log.d(TAG, "开始识别，图像尺寸: " + bitmap.getWidth() + "x" + bitmap.getHeight());
                LocalPlantRecognizerTFLite.RecognitionResult result = localRecognizer.recognize(bitmap);

                runOnUiThread(() -> {
                    progressBar.setVisibility(View.GONE);
                    if (result.success) {
                        displayResult(result);
                    } else {
                        showError(result.errorMessage);
                    }
                });
            } else {
                runOnUiThread(() -> {
                    progressBar.setVisibility(View.GONE);
                    showError("无法加载图片");
                });
            }
        });
    }

    private void displayResult(LocalPlantRecognizerTFLite.RecognitionResult result) {
        plantId = result.plantId;
        classId = result.classId;
        plantName = result.plantName;
        confidence = result.confidence;
        
        tvPlantName.setText(result.plantName);
        tvScientificName.setText(result.scientificName);
        tvConfidence.setText(String.format("置信度: %.1f%%", result.confidence * 100));
        tvDescription.setText(result.description + "\n\n养护建议：" + result.careTips);
    }

    private void showError(String message) {
        tvPlantName.setText("识别失败");
        tvScientificName.setText("");
        tvConfidence.setText("");
        tvDescription.setText(message != null ? message : "无法识别，请重试");
        cardSimilar.setVisibility(View.GONE);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (executorService != null) {
            executorService.shutdown();
        }
    }
    
    private void saveHistory() {
        String token = userManager.getToken();
        if (token == null || token.isEmpty()) {
            Toast.makeText(this, "请先登录", Toast.LENGTH_SHORT).show();
            return;
        }
        
        if (plantId <= 0) {
            Toast.makeText(this, "没有可保存的识别结果", Toast.LENGTH_SHORT).show();
            return;
        }
        
        Toast.makeText(this, "正在保存...", Toast.LENGTH_SHORT).show();
        
        File file = new File(imagePath);
        RequestBody requestBody = RequestBody.create(MediaType.parse("image/*"), file);
        MultipartBody.Part imagePart = MultipartBody.Part.createFormData("file", file.getName(), requestBody);
        
        ApiClient.getApiService().uploadImage(imagePart)
                .enqueue(new Callback<ApiResponse<UploadResponse>>() {
                    @Override
                    public void onResponse(Call<ApiResponse<UploadResponse>> call, 
                            Response<ApiResponse<UploadResponse>> response) {
                        if (response.isSuccessful() && response.body() != null && response.body().isSuccess()) {
                            String imageUrl = response.body().getData().getUrl();
                            saveHistoryToServer(imageUrl);
                        } else {
                            Toast.makeText(ResultActivity.this, "图片上传失败", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiResponse<UploadResponse>> call, Throwable t) {
                        Toast.makeText(ResultActivity.this, "网络错误: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }
    
    private void saveHistoryToServer(String imageUrl) {
        String token = userManager.getToken();
        
        Map<String, Object> request = new HashMap<>();
        // plant_id 和 class_id 都应该保存 classId（模型类别ID 0-49）
        // 因为后端数据库中 plant_id 关联的是 plants.class_id
        request.put("plant_id", classId);
        request.put("class_id", classId);
        request.put("plant_name", plantName);
        request.put("confidence", confidence);
        request.put("image_path", imageUrl);
        
        ApiClient.getApiService().saveHistory("Bearer " + token, request)
                .enqueue(new Callback<ApiResponse<Map<String, Object>>>() {
                    @Override
                    public void onResponse(Call<ApiResponse<Map<String, Object>>> call, 
                            Response<ApiResponse<Map<String, Object>>> response) {
                        if (response.isSuccessful() && response.body() != null && response.body().isSuccess()) {
                            Toast.makeText(ResultActivity.this, "保存成功", Toast.LENGTH_SHORT).show();
                        } else {
                            Toast.makeText(ResultActivity.this, "保存失败", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiResponse<Map<String, Object>>> call, Throwable t) {
                        Toast.makeText(ResultActivity.this, "网络错误: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }
}
