package com.plantrecognition.app.utils;

public class UserSession {
    private static UserSession instance;
    private int userId;
    private String username;
    private String token;
    
    private UserSession() {}
    
    public static synchronized UserSession getInstance() {
        if (instance == null) {
            instance = new UserSession();
        }
        return instance;
    }
    
    public void setUser(int userId, String username, String token) {
        this.userId = userId;
        this.username = username;
        this.token = token;
    }
    
    public void clear() {
        userId = 0;
        username = null;
        token = null;
    }
    
    public int getUserId() { return userId; }
    public String getUsername() { return username; }
    public String getToken() { return token; }
    public boolean isLoggedIn() { return token != null && !token.isEmpty(); }
}
