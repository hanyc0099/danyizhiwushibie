package com.plantrecognition.app.ui.explore;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.plantrecognition.app.R;
import com.plantrecognition.app.network.ApiClient;
import com.plantrecognition.app.network.ApiResponse;
import com.plantrecognition.app.network.PlantInfo;
import com.plantrecognition.app.ui.plant.PlantDetailActivity;
import java.util.ArrayList;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ExploreFragment extends Fragment implements PlantAdapter.OnPlantClickListener {

    private RecyclerView recyclerView;
    private PlantAdapter adapter;
    private List<PlantInfo> plantList = new ArrayList<>();
    private List<PlantInfo> allPlants = new ArrayList<>();
    private EditText etSearch;
    private ImageButton btnSearch;
    private int currentPage = 1;
    private static final int PAGE_SIZE = 20;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_explore, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        initViews(view);
        setupRecyclerView();
        loadPlants();
    }

    private void initViews(View view) {
        recyclerView = view.findViewById(R.id.recyclerView);
        etSearch = view.findViewById(R.id.etSearch);
        btnSearch = view.findViewById(R.id.btnSearch);

        // 设置搜索按钮点击事件
        if (btnSearch != null) {
            btnSearch.setOnClickListener(v -> performSearch());
        }

        // 设置输入框回车搜索
        if (etSearch != null) {
            etSearch.setOnEditorActionListener((v, actionId, event) -> {
                if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                    performSearch();
                    return true;
                }
                return false;
            });
        }
    }

    private void performSearch() {
        String keyword = etSearch.getText().toString().trim();
        if (keyword.isEmpty()) {
            // 如果搜索关键词为空，显示所有植物
            plantList.clear();
            plantList.addAll(allPlants);
            adapter.notifyDataSetChanged();
            return;
        }

        // 本地搜索过滤
        List<PlantInfo> filteredList = new ArrayList<>();
        String lowerKeyword = keyword.toLowerCase();
        for (PlantInfo plant : allPlants) {
            String chineseName = plant.getChineseName() != null ? plant.getChineseName().toLowerCase() : "";
            String scientificName = plant.getScientificName() != null ? plant.getScientificName().toLowerCase() : "";
            if (chineseName.contains(lowerKeyword) || scientificName.contains(lowerKeyword)) {
                filteredList.add(plant);
            }
        }

        plantList.clear();
        plantList.addAll(filteredList);
        adapter.notifyDataSetChanged();

        if (filteredList.isEmpty()) {
            Toast.makeText(requireContext(), "未找到匹配的植物", Toast.LENGTH_SHORT).show();
        }
    }

    private void setupRecyclerView() {
        adapter = new PlantAdapter(plantList, this);
        recyclerView.setLayoutManager(new GridLayoutManager(requireContext(), 2));
        recyclerView.setAdapter(adapter);
    }

    private void loadPlants() {
        ApiClient.getApiService().getPlantList(currentPage, PAGE_SIZE)
                .enqueue(new Callback<ApiResponse<List<PlantInfo>>>() {
                    @Override
                    public void onResponse(Call<ApiResponse<List<PlantInfo>>> call, Response<ApiResponse<List<PlantInfo>>> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            ApiResponse<List<PlantInfo>> apiResponse = response.body();
                            if (apiResponse.isSuccess() && apiResponse.getData() != null) {
                                plantList.addAll(apiResponse.getData());
                                allPlants.addAll(apiResponse.getData());
                                adapter.notifyDataSetChanged();
                            }
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiResponse<List<PlantInfo>>> call, Throwable t) {
                        Toast.makeText(requireContext(), "加载失败: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    @Override
    public void onPlantClick(PlantInfo plant) {
        Intent intent = new Intent(requireContext(), PlantDetailActivity.class);
        intent.putExtra("plant_id", plant.getId());
        startActivity(intent);
    }
}
