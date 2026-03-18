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
import com.plantrecognition.app.network.ApiClient;
import com.plantrecognition.app.network.HistoryRecord;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class HistoryAdapter extends RecyclerView.Adapter<HistoryAdapter.HistoryViewHolder> {

    private List<HistoryRecord> historyList;
    private OnHistoryClickListener listener;
    private OnHistoryLongClickListener longClickListener;

    public interface OnHistoryClickListener {
        void onHistoryClick(HistoryRecord record);
    }

    public interface OnHistoryLongClickListener {
        void onHistoryLongClick(HistoryRecord record, int position);
    }

    public HistoryAdapter(List<HistoryRecord> historyList, OnHistoryClickListener listener) {
        this.historyList = historyList;
        this.listener = listener;
    }

    public void setOnHistoryLongClickListener(OnHistoryLongClickListener listener) {
        this.longClickListener = listener;
    }

    @NonNull
    @Override
    public HistoryViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_history, parent, false);
        return new HistoryViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull HistoryViewHolder holder, int position) {
        HistoryRecord record = historyList.get(position);
        holder.bind(record);
        holder.itemView.setOnClickListener(v -> {
            if (listener != null) {
                listener.onHistoryClick(record);
            }
        });
        holder.itemView.setOnLongClickListener(v -> {
            if (longClickListener != null) {
                longClickListener.onHistoryLongClick(record, position);
                return true;
            }
            return false;
        });
    }

    @Override
    public int getItemCount() {
        return historyList != null ? historyList.size() : 0;
    }

    static class HistoryViewHolder extends RecyclerView.ViewHolder {
        private ImageView ivHistoryImage;
        private TextView tvPlantName;
        private TextView tvConfidence;
        private TextView tvDate;

        public HistoryViewHolder(@NonNull View itemView) {
            super(itemView);
            ivHistoryImage = itemView.findViewById(R.id.ivHistoryImage);
            tvPlantName = itemView.findViewById(R.id.tvPlantName);
            tvConfidence = itemView.findViewById(R.id.tvConfidence);
            tvDate = itemView.findViewById(R.id.tvDate);
        }

        public void bind(HistoryRecord record) {
            String plantName = record.getPlantName() != null ? record.getPlantName() : "未知植物";
            tvPlantName.setText(plantName);
            tvConfidence.setText(String.format("识别率: %.1f%%", record.getConfidence() * 100));
            tvDate.setText(formatDate(record.getCreatedAt()));

            String imageUrl = record.getImageUrl() != null ? record.getImageUrl() : record.getImagePath();
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

                Glide.with(itemView.getContext())
                        .load(fullUrl)
                        .placeholder(R.color.divider)
                        .into(ivHistoryImage);
            } else {
                ivHistoryImage.setImageResource(R.color.divider);
            }
        }

        private String formatDate(String createdAt) {
            if (createdAt == null || createdAt.isEmpty()) {
                return "";
            }
            try {
                Date date = null;
                
                // 尝试解析 ISO 8601 格式: 2026-03-14T00:49:39.439068
                if (createdAt.contains("T")) {
                    SimpleDateFormat isoFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault());
                    date = isoFormat.parse(createdAt);
                } else {
                    // 尝试解析普通格式: 2026-03-18 18:46:04
                    SimpleDateFormat normalFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
                    date = normalFormat.parse(createdAt);
                }
                
                if (date != null) {
                    // 格式化为: 2026-03-14 00:49
                    SimpleDateFormat outputFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault());
                    return outputFormat.format(date);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
            return createdAt;
        }
    }
}
