package com.plantrecognition.app.network;

import com.google.gson.annotations.SerializedName;

public class Post {
    @SerializedName("id")
    private int id;
    
    @SerializedName("user_id")
    private int userId;
    
    @SerializedName("username")
    private String username;
    
    @SerializedName("avatar")
    private String avatar;
    
    @SerializedName("content")
    private String content;
    
    @SerializedName("images")
    private String images;
    
    @SerializedName("likes_count")
    private int likesCount;
    
    @SerializedName("comments_count")
    private int commentsCount;
    
    @SerializedName("created_at")
    private String createdAt;
    
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    
    public int getUserId() { return userId; }
    public void setUserId(int userId) { this.userId = userId; }
    
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    
    public String getAvatar() { return avatar; }
    public void setAvatar(String avatar) { this.avatar = avatar; }
    
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    
    public String getImages() { return images; }
    public void setImages(String images) { this.images = images; }
    
    public int getLikesCount() { return likesCount; }
    public void setLikesCount(int likesCount) { this.likesCount = likesCount; }
    
    public int getCommentsCount() { return commentsCount; }
    public void setCommentsCount(int commentsCount) { this.commentsCount = commentsCount; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}
