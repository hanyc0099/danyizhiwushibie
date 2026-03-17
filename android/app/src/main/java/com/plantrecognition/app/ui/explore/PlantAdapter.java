package com.plantrecognition.app.ui.explore;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import com.plantrecognition.app.R;
import com.plantrecognition.app.network.PlantInfo;
import java.util.List;

public class PlantAdapter extends RecyclerView.Adapter<PlantAdapter.PlantViewHolder> {

    private List<PlantInfo> plantList;
    private OnPlantClickListener listener;

    public interface OnPlantClickListener {
        void onPlantClick(PlantInfo plant);
    }

    public PlantAdapter(List<PlantInfo> plantList, OnPlantClickListener listener) {
        this.plantList = plantList;
        this.listener = listener;
    }

    @NonNull
    @Override
    public PlantViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_plant, parent, false);
        return new PlantViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull PlantViewHolder holder, int position) {
        PlantInfo plant = plantList.get(position);
        holder.bind(plant);
        holder.itemView.setOnClickListener(v -> {
            if (listener != null) {
                listener.onPlantClick(plant);
            }
        });
    }

    @Override
    public int getItemCount() {
        return plantList != null ? plantList.size() : 0;
    }

    static class PlantViewHolder extends RecyclerView.ViewHolder {
        private ImageView ivPlantImage;
        private TextView tvPlantName;

        public PlantViewHolder(@NonNull View itemView) {
            super(itemView);
            ivPlantImage = itemView.findViewById(R.id.ivPlant);
            tvPlantName = itemView.findViewById(R.id.tvName);
        }

        public void bind(PlantInfo plant) {
            tvPlantName.setText(plant.getChineseName());
            String imageUrl = plant.getImageUrl();
            if (imageUrl != null && !imageUrl.isEmpty()) {
                String fullUrl;
                if (imageUrl.startsWith("http://") || imageUrl.startsWith("https://")) {
                    fullUrl = imageUrl;
                } else if (imageUrl.startsWith("/uploads/") || imageUrl.startsWith("/dataset/")) {
                    // 静态文件服务挂载在根路径，不在 /api/v1 前缀下
                    fullUrl = com.plantrecognition.app.network.ApiClient.getBaseUrl() + imageUrl;
                } else if (imageUrl.startsWith("/")) {
                    fullUrl = com.plantrecognition.app.network.ApiClient.getBaseUrl() + imageUrl;
                } else {
                    fullUrl = imageUrl;
                }
                Glide.with(itemView.getContext())
                        .load(fullUrl)
                        .placeholder(R.drawable.ic_plant_placeholder)
                        .error(R.drawable.ic_plant_placeholder)
                        .into(ivPlantImage);
            } else {
                // 没有图片时显示植物名首字作为占位
                ivPlantImage.setImageResource(R.drawable.ic_plant_placeholder);
            }
        }
    }
}
