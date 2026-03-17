package com.plantrecognition.app.network;

import com.google.gson.annotations.SerializedName;

public class HistoryStatistics {
    @SerializedName("today_count")
    private int todayCount;

    @SerializedName("total_count")
    private int totalCount;

    public int getTodayCount() { return todayCount; }
    public void setTodayCount(int todayCount) { this.todayCount = todayCount; }

    public int getTotalCount() { return totalCount; }
    public void setTotalCount(int totalCount) { this.totalCount = totalCount; }
}
