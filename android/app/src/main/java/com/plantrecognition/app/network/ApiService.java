package com.plantrecognition.app.network;

import java.util.List;
import java.util.Map;
import okhttp3.MultipartBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;
import retrofit2.http.Path;
import retrofit2.http.Query;

public interface ApiService {
    
    @POST("auth/register")
    Call<ApiResponse<RegisterResponse>> register(@Body RegisterRequest request);
    
    @POST("auth/login")
    Call<ApiResponse<LoginResponse>> login(@Body LoginRequest request);
    
    @GET("user/info")
    Call<ApiResponse<UserInfo>> getUserInfo(@Header("Authorization") String token);
    
    @POST("user/profile")
    Call<ApiResponse<Map<String, Object>>> updateProfile(@Header("Authorization") String token, @Body Map<String, Object> request);
    
    @Multipart
    @POST("recognize")
    Call<ApiResponse<RecognitionResponse>> recognizeImage(@Part MultipartBody.Part image);
    
    @GET("plants")
    Call<ApiResponse<PagedResponse<PlantInfo>>> getPlantList(@Query("page") int page, @Query("page_size") int pageSize);

    @GET("plants/{id}")
    Call<ApiResponse<PlantInfo>> getPlantDetail(@Path("id") int id);
    
    @POST("history/save")
    Call<ApiResponse<Map<String, Object>>> saveHistory(@Header("Authorization") String token, @Body Map<String, Object> request);
    
    @GET("history/list")
    Call<ApiResponse<List<HistoryRecord>>> getHistoryList(@Header("Authorization") String token, @Query("page") int page, @Query("page_size") int pageSize);

    @GET("history/statistics")
    Call<ApiResponse<HistoryStatistics>> getHistoryStatistics(@Header("Authorization") String token);

    @DELETE("history/{history_id}")
    Call<ApiResponse<Void>> deleteHistory(@Header("Authorization") String token, @Path("history_id") int historyId);

    @Multipart
    @POST("upload/image")
    Call<ApiResponse<UploadResponse>> uploadImage(@Part MultipartBody.Part file);
}
