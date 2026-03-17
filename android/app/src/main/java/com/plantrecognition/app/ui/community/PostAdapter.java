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
import com.plantrecognition.app.network.Post;
import java.util.List;

public class PostAdapter extends RecyclerView.Adapter<PostAdapter.PostViewHolder> {

    private List<Post> postList;
    private OnPostClickListener listener;

    public interface OnPostClickListener {
        void onPostClick(Post post);
    }

    public PostAdapter(List<Post> postList, OnPostClickListener listener) {
        this.postList = postList;
        this.listener = listener;
    }

    @NonNull
    @Override
    public PostViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_post, parent, false);
        return new PostViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull PostViewHolder holder, int position) {
        Post post = postList.get(position);
        holder.bind(post);
        holder.itemView.setOnClickListener(v -> {
            if (listener != null) {
                listener.onPostClick(post);
            }
        });
    }

    @Override
    public int getItemCount() {
        return postList != null ? postList.size() : 0;
    }

    static class PostViewHolder extends RecyclerView.ViewHolder {
        private ImageView ivUserAvatar;
        private TextView tvUserName;
        private TextView tvPostTime;
        private TextView tvPostTitle;
        private TextView tvPostContent;

        public PostViewHolder(@NonNull View itemView) {
            super(itemView);
            ivUserAvatar = itemView.findViewById(R.id.ivUserAvatar);
            tvUserName = itemView.findViewById(R.id.tvUserName);
            tvPostTime = itemView.findViewById(R.id.tvPostTime);
            tvPostTitle = itemView.findViewById(R.id.tvPostTitle);
            tvPostContent = itemView.findViewById(R.id.tvPostContent);
        }

        public void bind(Post post) {
            if (tvUserName != null) {
                tvUserName.setText(post.getUsername());
            }
            if (tvPostContent != null) {
                tvPostContent.setText(post.getContent());
            }
            if (tvPostTime != null) {
                tvPostTime.setText(post.getCreatedAt());
            }

            if (post.getAvatar() != null && !post.getAvatar().isEmpty() && ivUserAvatar != null) {
                String avatarUrl = post.getAvatar();
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
                        .into(ivUserAvatar);
            }
        }
    }
}
