package com.plantrecognition.app.network;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class RecognitionResponse {
    @SerializedName("plant_id")
    private int plantId;
    
    @SerializedName("class_id")
    private int classId;
    
    @SerializedName("chinese_name")
    private String chineseName;
    
    @SerializedName("english_name")
    private String englishName;
    
    @SerializedName("scientific_name")
    private String scientificName;
    
    @SerializedName("confidence")
    private float confidence;
    
    @SerializedName("family")
    private String family;
    
    @SerializedName("genus")
    private String genus;
    
    @SerializedName("description")
    private String description;
    
    @SerializedName("characteristics")
    private String characteristics;
    
    @SerializedName("flowering_period")
    private String floweringPeriod;
    
    @SerializedName("care_tips")
    private String careTips;
    
    @SerializedName("difficulty")
    private String difficulty;
    
    @SerializedName("image_url")
    private String imageUrl;
    
    @SerializedName("similar_results")
    private List<PlantInfo> similarResults;
    
    public int getPlantId() { return plantId; }
    public void setPlantId(int plantId) { this.plantId = plantId; }
    
    public int getClassId() { return classId; }
    public void setClassId(int classId) { this.classId = classId; }
    
    public String getChineseName() { return chineseName; }
    public void setChineseName(String chineseName) { this.chineseName = chineseName; }
    
    public String getEnglishName() { return englishName; }
    public void setEnglishName(String englishName) { this.englishName = englishName; }
    
    public String getScientificName() { return scientificName; }
    public void setScientificName(String scientificName) { this.scientificName = scientificName; }
    
    public float getConfidence() { return confidence; }
    public void setConfidence(float confidence) { this.confidence = confidence; }
    
    public String getFamily() { return family; }
    public void setFamily(String family) { this.family = family; }
    
    public String getGenus() { return genus; }
    public void setGenus(String genus) { this.genus = genus; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public String getCharacteristics() { return characteristics; }
    public void setCharacteristics(String characteristics) { this.characteristics = characteristics; }
    
    public String getFloweringPeriod() { return floweringPeriod; }
    public void setFloweringPeriod(String floweringPeriod) { this.floweringPeriod = floweringPeriod; }
    
    public String getCareTips() { return careTips; }
    public void setCareTips(String careTips) { this.careTips = careTips; }
    
    public String getDifficulty() { return difficulty; }
    public void setDifficulty(String difficulty) { this.difficulty = difficulty; }
    
    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
    
    public List<PlantInfo> getSimilarResults() { return similarResults; }
    public void setSimilarResults(List<PlantInfo> similarResults) { this.similarResults = similarResults; }
}
