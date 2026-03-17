package com.plantrecognition.app.network;

import com.google.gson.annotations.SerializedName;

public class PlantInfo {
    @SerializedName("id")
    private int id;
    
    @SerializedName("class_id")
    private int classId;
    
    @SerializedName("chinese_name")
    private String chineseName;
    
    @SerializedName("english_name")
    private String englishName;
    
    @SerializedName("scientific_name")
    private String scientificName;
    
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
    
    @SerializedName("image_url")
    private String imageUrl;
    
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    
    public int getClassId() { return classId; }
    public void setClassId(int classId) { this.classId = classId; }
    
    public String getChineseName() { return chineseName; }
    public void setChineseName(String chineseName) { this.chineseName = chineseName; }
    
    public String getEnglishName() { return englishName; }
    public void setEnglishName(String englishName) { this.englishName = englishName; }
    
    public String getScientificName() { return scientificName; }
    public void setScientificName(String scientificName) { this.scientificName = scientificName; }
    
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
    
    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
}
