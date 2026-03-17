package com.plantrecognition.app.network;

import com.google.gson.annotations.SerializedName;

public class ApiResponse<T> {
    @SerializedName("code")
    private int code;

    @SerializedName("success")
    private Boolean success;

    @SerializedName("message")
    private String message;

    @SerializedName("data")
    private T data;

    public int getCode() { return code; }
    public void setCode(int code) { this.code = code; }

    public boolean isSuccess() {
        // 如果后端返回了 success 字段，使用它；否则根据 code 判断
        if (success != null) {
            return success;
        }
        return code == 200;
    }

    public void setSuccess(boolean success) { this.success = success; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public T getData() { return data; }
    public void setData(T data) { this.data = data; }
}
