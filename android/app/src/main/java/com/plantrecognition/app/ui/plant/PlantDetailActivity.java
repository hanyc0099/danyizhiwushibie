package com.plantrecognition.app.ui.plant;

import android.os.Bundle;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.bumptech.glide.Glide;
import com.plantrecognition.app.R;
import com.plantrecognition.app.network.ApiClient;
import com.plantrecognition.app.network.ApiResponse;
import com.plantrecognition.app.network.PlantInfo;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class PlantDetailActivity extends AppCompatActivity {

    private ImageView ivPlantImage;
    private ImageView btnBack;
    private TextView tvPlantName;
    private TextView tvScientificName;
    private TextView tvFamily;
    private TextView tvGenus;
    private TextView tvDescription;
    private TextView tvCharacteristics;
    private TextView tvFloweringPeriod;
    private TextView tvCareTips;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_plant_detail);

        initViews();
        setListeners();

        int plantId = getIntent().getIntExtra("plant_id", 0);
        android.util.Log.d("PlantDetailActivity", "接收到的 plant_id (class_id): " + plantId);
        if (plantId > 0) {
            loadPlantDetail(plantId);
        }
    }

    private void initViews() {
        ivPlantImage = findViewById(R.id.ivPlantImage);
        btnBack = findViewById(R.id.btnBack);
        tvPlantName = findViewById(R.id.tvPlantName);
        tvScientificName = findViewById(R.id.tvScientificName);
        tvFamily = findViewById(R.id.tvFamily);
        tvGenus = findViewById(R.id.tvGenus);
        tvDescription = findViewById(R.id.tvDescription);
        tvCharacteristics = findViewById(R.id.tvCharacteristics);
        tvFloweringPeriod = findViewById(R.id.tvFloweringPeriod);
        tvCareTips = findViewById(R.id.tvCareTips);
    }

    private void setListeners() {
        btnBack.setOnClickListener(v -> finish());
    }

    private void loadPlantDetail(int plantId) {
        ApiClient.getApiService().getPlantDetail(plantId).enqueue(new Callback<ApiResponse<PlantInfo>>() {
            @Override
            public void onResponse(Call<ApiResponse<PlantInfo>> call, Response<ApiResponse<PlantInfo>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    ApiResponse<PlantInfo> apiResponse = response.body();
                    if (apiResponse.isSuccess() && apiResponse.getData() != null) {
                        PlantInfo plant = apiResponse.getData();
                        android.util.Log.d("PlantDetailActivity", "API返回: " + plant.getChineseName() + 
                                " (id=" + plant.getId() + ")");
                        displayPlantInfo(plant);
                    } else {
                        Toast.makeText(PlantDetailActivity.this, "获取植物信息失败", Toast.LENGTH_SHORT).show();
                    }
                } else {
                    Toast.makeText(PlantDetailActivity.this, "获取植物信息失败", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<ApiResponse<PlantInfo>> call, Throwable t) {
                Toast.makeText(PlantDetailActivity.this, "网络错误: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void displayPlantInfo(PlantInfo plant) {
        tvPlantName.setText(plant.getChineseName());
        tvScientificName.setText(plant.getScientificName());
        tvFamily.setText("科: " + (plant.getFamily() != null ? plant.getFamily() : "未知"));
        tvGenus.setText("属: " + (plant.getGenus() != null ? plant.getGenus() : "未知"));
        tvDescription.setText(plant.getDescription() != null ? plant.getDescription() : "暂无描述");
        tvCharacteristics.setText(plant.getCharacteristics() != null ? plant.getCharacteristics() : "暂无特征信息");
        tvFloweringPeriod.setText(plant.getFloweringPeriod() != null ? plant.getFloweringPeriod() : "未知");
        tvCareTips.setText(plant.getCareTips() != null ? plant.getCareTips() : "暂无养护建议");

        // 优先显示识别时的图片（如果有）
        String historyImageUrl = getIntent().getStringExtra("history_image_url");
        String imageUrl = (historyImageUrl != null && !historyImageUrl.isEmpty()) 
                ? historyImageUrl 
                : plant.getImageUrl();
        
        if (imageUrl != null && !imageUrl.isEmpty()) {
            String fullUrl;
            if (imageUrl.startsWith("http://") || imageUrl.startsWith("https://")) {
                fullUrl = imageUrl;
            } else if (imageUrl.startsWith("/uploads/") || imageUrl.startsWith("/dataset/")) {
                // 静态文件服务挂载在根路径，不在 /api/v1 前缀下
                fullUrl = ApiClient.getBaseUrl() + imageUrl;
            } else if (imageUrl.startsWith("/")) {
                fullUrl = ApiClient.getBaseUrl() + imageUrl;
            } else {
                fullUrl = imageUrl;
            }
            Glide.with(this)
                    .load(fullUrl)
                    .placeholder(R.drawable.ic_plant_placeholder)
                    .error(R.drawable.ic_plant_placeholder)
                    .into(ivPlantImage);
        }
    }
}
