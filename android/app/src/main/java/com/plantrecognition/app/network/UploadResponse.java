package com.plantrecognition.app.network;

import com.google.gson.annotations.SerializedName;

public class UploadResponse {
    @SerializedName("url")
    private String url;
    
    @SerializedName("filename")
    private String filename;
    
    @SerializedName("size")
    private long size;
    
    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }
    
    public String getFilename() { return filename; }
    public void setFilename(String filename) { this.filename = filename; }
    
    public long getSize() { return size; }
    public void setSize(long size) { this.size = size; }
}
