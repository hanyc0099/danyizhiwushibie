package com.plantrecognition.app.network;

import com.google.gson.annotations.SerializedName;

public class UserInfo {
    @SerializedName("id")
    private int id;
    
    @SerializedName("username")
    private String username;
    
    @SerializedName("nickname")
    private String nickname;
    
    @SerializedName("avatar_url")
    private String avatar;
    
    @SerializedName("bio")
    private String bio;
    
    @SerializedName("recognition_count")
    private int recognitionCount;
    
    @SerializedName("collection_count")
    private int collectionCount;
    
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    
    public String getNickname() { return nickname; }
    public void setNickname(String nickname) { this.nickname = nickname; }
    
    public String getAvatar() { return avatar; }
    public void setAvatar(String avatar) { this.avatar = avatar; }
    
    public String getBio() { return bio; }
    public void setBio(String bio) { this.bio = bio; }
    
    public int getRecognitionCount() { return recognitionCount; }
    public void setRecognitionCount(int recognitionCount) { this.recognitionCount = recognitionCount; }
    
    public int getCollectionCount() { return collectionCount; }
    public void setCollectionCount(int collectionCount) { this.collectionCount = collectionCount; }
}
