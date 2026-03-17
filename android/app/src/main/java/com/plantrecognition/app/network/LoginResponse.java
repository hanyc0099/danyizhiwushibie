package com.plantrecognition.app.network;

import com.google.gson.annotations.SerializedName;

/**
 * 登录响应 - 后端返回格式: {"token": "...", "user": {...}}
 */
public class LoginResponse {
    @SerializedName("token")
    private String token;

    @SerializedName("user")
    private UserData user;

    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }

    public int getId() { return user != null ? user.id : 0; }
    public String getUsername() { return user != null ? user.username : ""; }
    public String getNickname() { return user != null ? user.nickname : ""; }
    public String getAvatar() { return user != null ? user.avatarUrl : null; }

    public static class UserData {
        @SerializedName("id")
        int id;

        @SerializedName("username")
        String username;

        @SerializedName("nickname")
        String nickname;

        @SerializedName("avatar_url")
        String avatarUrl;

        @SerializedName("bio")
        String bio;
    }
}
