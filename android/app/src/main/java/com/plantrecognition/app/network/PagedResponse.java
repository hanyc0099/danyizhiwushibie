package com.plantrecognition.app.network;

import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 * 分页响应数据包装类
 * 用于解析后端返回的分页数据结构
 */
public class PagedResponse<T> {
    @SerializedName("total")
    private int total;

    @SerializedName("page")
    private int page;

    @SerializedName("page_size")
    private int pageSize;

    @SerializedName("items")
    private List<T> items;

    public int getTotal() { return total; }
    public void setTotal(int total) { this.total = total; }

    public int getPage() { return page; }
    public void setPage(int page) { this.page = page; }

    public int getPageSize() { return pageSize; }
    public void setPageSize(int pageSize) { this.pageSize = pageSize; }

    public List<T> getItems() { return items; }
    public void setItems(List<T> items) { this.items = items; }
}
