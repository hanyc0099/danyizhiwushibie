package com.plantrecognition.app.ui.community;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import com.plantrecognition.app.R;
import com.plantrecognition.app.network.Comment;
import java.util.List;

public class CommentAdapter extends RecyclerView.Adapter<CommentAdapter.CommentViewHolder> {

    private List<Comment> commentList;

    public CommentAdapter(List<Comment> commentList) {
        this.commentList = commentList;
    }

    @NonNull
    @Override
    public CommentViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_comment, parent, false);
        return new CommentViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull CommentViewHolder holder, int position) {
        Comment comment = commentList.get(position);
        holder.bind(comment);
    }

    @Override
    public int getItemCount() {
        return commentList != null ? commentList.size() : 0;
    }

    static class CommentViewHolder extends RecyclerView.ViewHolder {
        private ImageView ivAvatar;
        private TextView tvUsername;
        private TextView tvContent;
        private TextView tvDate;

        public CommentViewHolder(@NonNull View itemView) {
            super(itemView);
            ivAvatar = itemView.findViewById(R.id.ivAvatar);
            tvUsername = itemView.findViewById(R.id.tvUsername);
            tvContent = itemView.findViewById(R.id.tvContent);
            tvDate = itemView.findViewById(R.id.tvDate);
        }

        public void bind(Comment comment) {
            if (tvUsername != null) {
                tvUsername.setText(comment.getUsername());
            }
            if (tvContent != null) {
                tvContent.setText(comment.getContent());
            }
            if (tvDate != null) {
                tvDate.setText(comment.getCreatedAt());
            }

            if (comment.getAvatar() != null && !comment.getAvatar().isEmpty() && ivAvatar != null) {
                String avatarUrl = comment.getAvatar();
                String fullUrl;
                if (avatarUrl.startsWith("http://") || avatarUrl.startsWith("https://")) {
                    fullUrl = avatarUrl;
                } else if (avatarUrl.startsWith("/uploads/")) {
                    fullUrl = com.plantrecognition.app.network.ApiClient.getBaseUrl() + "/api/v1" + avatarUrl;
                } else if (avatarUrl.startsWith("/")) {
                    fullUrl = com.plantrecognition.app.network.ApiClient.getBaseUrl() + avatarUrl;
                } else {
                    fullUrl = avatarUrl;
                }
                Glide.with(itemView.getContext())
                        .load(fullUrl)
                        .circleCrop()
                        .placeholder(R.drawable.ic_avatar_default)
                        .into(ivAvatar);
            }
        }
    }
}
