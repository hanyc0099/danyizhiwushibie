package com.plantrecognition.app.ui.history;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.plantrecognition.app.R;
import com.plantrecognition.app.network.ApiClient;
import com.plantrecognition.app.network.ApiResponse;
import com.plantrecognition.app.network.HistoryRecord;
import com.plantrecognition.app.ui.plant.PlantDetailActivity;
import com.plantrecognition.app.utils.UserManager;
import java.util.ArrayList;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class HistoryFragment extends Fragment implements HistoryAdapter.OnHistoryClickListener {

    private RecyclerView recyclerView;
    private HistoryAdapter adapter;
    private List<HistoryRecord> historyList = new ArrayList<>();
    private UserManager userManager;
    private OnNavigateListener navigateListener;

    public interface OnNavigateListener {
        void onNavigateToFavorites();
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_history, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        userManager = UserManager.getInstance(requireContext());

        initViews(view);
        setupRecyclerView();
    }

    @Override
    public void onResume() {
        super.onResume();
        loadHistory();
    }

    private void initViews(View view) {
        recyclerView = view.findViewById(R.id.recyclerView);
    }

    private void setupRecyclerView() {
        adapter = new HistoryAdapter(historyList, this);
        adapter.setOnHistoryLongClickListener((record, position) -> {
            showDeleteDialog(record, position);
        });
        recyclerView.setLayoutManager(new LinearLayoutManager(requireContext()));
        recyclerView.setAdapter(adapter);
    }

    private void showDeleteDialog(HistoryRecord record, int position) {
        new AlertDialog.Builder(requireContext())
                .setTitle("删除记录")
                .setMessage("确定要删除这条识别记录吗？")
                .setPositiveButton("删除", (dialog, which) -> deleteHistory(record, position))
                .setNegativeButton("取消", null)
                .show();
    }

    private void deleteHistory(HistoryRecord record, int position) {
        String token = userManager.getToken();
        if (token == null || token.isEmpty()) {
            return;
        }

        ApiClient.getApiService().deleteHistory("Bearer " + token, record.getId())
                .enqueue(new Callback<ApiResponse<Void>>() {
                    @Override
                    public void onResponse(Call<ApiResponse<Void>> call, Response<ApiResponse<Void>> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            ApiResponse<Void> apiResponse = response.body();
                            if (apiResponse.isSuccess()) {
                                historyList.remove(position);
                                adapter.notifyItemRemoved(position);
                                Toast.makeText(requireContext(), "删除成功", Toast.LENGTH_SHORT).show();
                            } else {
                                Toast.makeText(requireContext(), apiResponse.getMessage(), Toast.LENGTH_SHORT).show();
                            }
                        } else {
                            Toast.makeText(requireContext(), "删除失败", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiResponse<Void>> call, Throwable t) {
                        Toast.makeText(requireContext(), "网络错误: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    private void loadHistory() {
        String token = userManager.getToken();
        if (token == null || token.isEmpty()) {
            return;
        }

        ApiClient.getApiService().getHistoryList("Bearer " + token, 1, 20)
                .enqueue(new Callback<ApiResponse<List<HistoryRecord>>>() {
                    @Override
                    public void onResponse(Call<ApiResponse<List<HistoryRecord>>> call, Response<ApiResponse<List<HistoryRecord>>> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            ApiResponse<List<HistoryRecord>> apiResponse = response.body();
                            if (apiResponse.isSuccess() && apiResponse.getData() != null) {
                                historyList.clear();
                                historyList.addAll(apiResponse.getData());
                                adapter.notifyDataSetChanged();
                            }
                        } else {
                            Toast.makeText(requireContext(), "获取记录失败", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiResponse<List<HistoryRecord>>> call, Throwable t) {
                        Toast.makeText(requireContext(), "网络错误: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    @Override
    public void onHistoryClick(HistoryRecord record) {
        // 添加日志调试
        android.util.Log.d("HistoryFragment", "点击记录: id=" + record.getId() + 
                ", plant_name=" + record.getPlantName() + 
                ", class_id=" + record.getClassId() + 
                ", plant_id=" + record.getPlantId());
        
        Intent intent = new Intent(requireContext(), PlantDetailActivity.class);
        // 使用 class_id 查询植物详情
        intent.putExtra("plant_id", record.getClassId());
        // 传递识别记录的ID和图片，用于显示识别时的图片
        intent.putExtra("history_id", record.getId());
        intent.putExtra("history_image_url", record.getImageUrl());
        startActivity(intent);
    }
}
