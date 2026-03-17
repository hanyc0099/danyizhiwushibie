package com.plantrecognition.app.ui.history;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import com.plantrecognition.app.R;
import com.plantrecognition.app.network.HistoryRecord;
import java.util.List;

public class CollectionAdapter extends RecyclerView.Adapter<CollectionAdapter.CollectionViewHolder> {

    private List<HistoryRecord> collectionList;
    private OnCollectionClickListener listener;

    public interface OnCollectionClickListener {
        void onCollectionClick(HistoryRecord record);
    }

    public CollectionAdapter(List<HistoryRecord> collectionList, OnCollectionClickListener listener) {
        this.collectionList = collectionList;
        this.listener = listener;
    }

    @NonNull
    @Override
    public CollectionViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_collection, parent, false);
        return new CollectionViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull CollectionViewHolder holder, int position) {
        HistoryRecord record = collectionList.get(position);
        holder.bind(record);
        holder.itemView.setOnClickListener(v -> {
            if (listener != null) {
                listener.onCollectionClick(record);
            }
        });
    }

    @Override
    public int getItemCount() {
        return collectionList != null ? collectionList.size() : 0;
    }

    static class CollectionViewHolder extends RecyclerView.ViewHolder {
        private ImageView ivCollectionImage;
        private TextView tvPlantName;

        public CollectionViewHolder(@NonNull View itemView) {
            super(itemView);
            ivCollectionImage = itemView.findViewById(R.id.ivCollectionImage);
            tvPlantName = itemView.findViewById(R.id.tvPlantName);
        }

        public void bind(HistoryRecord record) {
            String plantName = record.getPlantName() != null ? record.getPlantName() : "未知植物";
            tvPlantName.setText(plantName);

            String imageUrl = record.getImageUrl() != null ? record.getImageUrl() : record.getImagePath();
            if (imageUrl != null && !imageUrl.isEmpty()) {
                String fullUrl;
                if (imageUrl.startsWith("http://") || imageUrl.startsWith("https://")) {
                    fullUrl = imageUrl;
                } else if (imageUrl.startsWith("/uploads/")) {
                    fullUrl = com.plantrecognition.app.network.ApiClient.getBaseUrl() + "/api/v1" + imageUrl;
                } else if (imageUrl.startsWith("/")) {
                    fullUrl = com.plantrecognition.app.network.ApiClient.getBaseUrl() + imageUrl;
                } else {
                    fullUrl = imageUrl;
                }
                Glide.with(itemView.getContext())
                        .load(fullUrl)
                        .placeholder(R.drawable.ic_plant_placeholder)
                        .error(R.drawable.ic_plant_placeholder)
                        .into(ivCollectionImage);
            } else {
                ivCollectionImage.setImageResource(R.drawable.ic_plant_placeholder);
            }
        }
    }
}
