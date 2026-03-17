package com.plantrecognition.app.ui.home;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.cardview.widget.CardView;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import com.plantrecognition.app.R;
import com.plantrecognition.app.network.ApiClient;
import com.plantrecognition.app.network.ApiResponse;
import com.plantrecognition.app.network.HistoryRecord;
import com.plantrecognition.app.network.HistoryStatistics;
import com.plantrecognition.app.ui.history.HistoryAdapter;
import com.plantrecognition.app.ui.plant.PlantDetailActivity;
import com.plantrecognition.app.ui.recognize.RecognizeActivity;
import com.plantrecognition.app.utils.UserManager;
import java.util.ArrayList;
import java.util.List;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class HomeFragment extends Fragment implements HistoryAdapter.OnHistoryClickListener {

    private ImageView ivProfile;
    private CardView cardRecognize;
    private CardView cardGallery;
    private TextView tvTodayCount;
    private TextView tvTotalCount;
    private RecyclerView rvRecommend;
    private HistoryAdapter recentAdapter;
    private List<HistoryRecord> recentList = new ArrayList<>();
    private UserManager userManager;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_home, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        userManager = UserManager.getInstance(requireContext());

        initViews(view);
        setupUserInfo();
        setupRecentRecyclerView();
        setListeners();
    }

    private void initViews(View view) {
        ivProfile = view.findViewById(R.id.ivProfile);
        cardRecognize = view.findViewById(R.id.cardRecognize);
        cardGallery = view.findViewById(R.id.cardGallery);
        tvTodayCount = view.findViewById(R.id.tvTodayCount);
        tvTotalCount = view.findViewById(R.id.tvTotalCount);
        rvRecommend = view.findViewById(R.id.rvRecommend);
    }

    private void setupUserInfo() {
        String avatar = userManager.getAvatar();
        if (avatar != null && !avatar.isEmpty() && ivProfile != null) {
            String fullAvatarUrl;
            if (avatar.startsWith("http://") || avatar.startsWith("https://")) {
                fullAvatarUrl = avatar;
            } else if (avatar.startsWith("/uploads/")) {
                fullAvatarUrl = ApiClient.getBaseUrl() + "/api/v1" + avatar;
            } else if (avatar.startsWith("/")) {
                fullAvatarUrl = ApiClient.getBaseUrl() + avatar;
            } else {
                fullAvatarUrl = avatar;
            }
            Glide.with(this)
                    .load(fullAvatarUrl)
                    .circleCrop()
                    .placeholder(R.drawable.ic_avatar_default)
                    .into(ivProfile);
        }
    }

    private void setupRecentRecyclerView() {
        if (rvRecommend != null) {
            recentAdapter = new HistoryAdapter(recentList, this);
            rvRecommend.setLayoutManager(new LinearLayoutManager(requireContext()));
            rvRecommend.setAdapter(recentAdapter);
            rvRecommend.setNestedScrollingEnabled(false);
        }
    }

    private void loadRecentHistory() {
        String token = userManager.getToken();
        if (token == null || token.isEmpty()) {
            return;
        }

        // 加载最近5条记录用于显示
        ApiClient.getApiService().getHistoryList("Bearer " + token, 1, 5)
                .enqueue(new Callback<ApiResponse<List<HistoryRecord>>>() {
                    @Override
                    public void onResponse(Call<ApiResponse<List<HistoryRecord>>> call, Response<ApiResponse<List<HistoryRecord>>> response) {
                        if (!isAdded()) return;
                        if (response.isSuccessful() && response.body() != null) {
                            ApiResponse<List<HistoryRecord>> apiResponse = response.body();
                            if (apiResponse.isSuccess() && apiResponse.getData() != null) {
                                recentList.clear();
                                recentList.addAll(apiResponse.getData());
                                if (recentAdapter != null) {
                                    recentAdapter.notifyDataSetChanged();
                                }
                            }
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiResponse<List<HistoryRecord>>> call, Throwable t) {
                        // 静默失败
                    }
                });

        // 加载统计数据（今日识别数和累计识别数）
        loadStatistics(token);
    }

    private void loadStatistics(String token) {
        ApiClient.getApiService().getHistoryStatistics("Bearer " + token)
                .enqueue(new Callback<ApiResponse<HistoryStatistics>>() {
                    @Override
                    public void onResponse(Call<ApiResponse<HistoryStatistics>> call, Response<ApiResponse<HistoryStatistics>> response) {
                        if (!isAdded()) return;
                        if (response.isSuccessful() && response.body() != null) {
                            ApiResponse<HistoryStatistics> apiResponse = response.body();
                            if (apiResponse.isSuccess() && apiResponse.getData() != null) {
                                HistoryStatistics stats = apiResponse.getData();
                                if (tvTodayCount != null) {
                                    tvTodayCount.setText(String.valueOf(stats.getTodayCount()));
                                }
                                if (tvTotalCount != null) {
                                    tvTotalCount.setText(String.valueOf(stats.getTotalCount()));
                                }
                            }
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiResponse<HistoryStatistics>> call, Throwable t) {
                        // 静默失败
                    }
                });
    }

    private void setListeners() {
        if (cardRecognize != null) {
            cardRecognize.setOnClickListener(v -> {
                Intent intent = new Intent(requireContext(), RecognizeActivity.class);
                intent.putExtra("from_camera", true);
                startActivity(intent);
            });
        }

        if (cardGallery != null) {
            cardGallery.setOnClickListener(v -> {
                Intent intent = new Intent(requireContext(), RecognizeActivity.class);
                intent.putExtra("from_camera", false);
                startActivity(intent);
            });
        }

        if (ivProfile != null) {
            ivProfile.setOnClickListener(v -> {
            });
        }
    }

    @Override
    public void onResume() {
        super.onResume();
        setupUserInfo();
        loadRecentHistory();
    }

    @Override
    public void onHistoryClick(HistoryRecord record) {
        Intent intent = new Intent(requireContext(), PlantDetailActivity.class);
        // 使用 class_id 查询植物详情
        intent.putExtra("plant_id", record.getClassId());
        // 传递识别记录的ID和图片，用于显示识别时的图片
        intent.putExtra("history_id", record.getId());
        intent.putExtra("history_image_url", record.getImageUrl());
        startActivity(intent);
    }

    private void updateStats(List<HistoryRecord> records) {
        if (records == null) return;

        int totalCount = records.size();
        int todayCount = 0;

        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());
        String today = sdf.format(new Date());

        for (HistoryRecord record : records) {
            String createdAt = record.getCreatedAt();
            if (createdAt != null && createdAt.startsWith(today)) {
                todayCount++;
            }
        }

        if (tvTodayCount != null) {
            tvTodayCount.setText(String.valueOf(todayCount));
        }
        if (tvTotalCount != null) {
            tvTotalCount.setText(String.valueOf(totalCount));
        }
    }
}
