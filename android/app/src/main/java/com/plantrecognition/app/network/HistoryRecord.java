package com.plantrecognition.app.network;

import com.google.gson.annotations.SerializedName;

public class HistoryRecord {
    @SerializedName("id")
    private int id;
    
    @SerializedName("plant_id")
    private int plantId;
    
    @SerializedName("class_id")
    private int classId;
    
    @SerializedName("plant_name")
    private String plantName;
    
    @SerializedName("image_path")
    private String imagePath;
    
    @SerializedName("image_url")
    private String imageUrl;
    
    @SerializedName("confidence")
    private float confidence;
    
    @SerializedName("created_at")
    private String createdAt;
    
    @SerializedName("is_favorite")
    private boolean isFavorite;
    
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    
    public int getPlantId() { return plantId; }
    public void setPlantId(int plantId) { this.plantId = plantId; }
    
    public int getClassId() { return classId; }
    public void setClassId(int classId) { this.classId = classId; }
    
    public String getPlantName() { return plantName; }
    public void setPlantName(String plantName) { this.plantName = plantName; }
    
    public String getImagePath() { return imagePath; }
    public void setImagePath(String imagePath) { this.imagePath = imagePath; }
    
    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
    
    public float getConfidence() { return confidence; }
    public void setConfidence(float confidence) { this.confidence = confidence; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    
    public boolean isFavorite() { return isFavorite; }
    public void setFavorite(boolean favorite) { isFavorite = favorite; }
}
