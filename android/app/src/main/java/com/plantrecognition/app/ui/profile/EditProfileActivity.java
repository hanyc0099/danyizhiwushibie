package com.plantrecognition.app.ui.profile;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import com.bumptech.glide.Glide;
import com.plantrecognition.app.R;
import com.plantrecognition.app.network.ApiClient;
import com.plantrecognition.app.network.ApiResponse;
import com.plantrecognition.app.network.UploadResponse;
import com.plantrecognition.app.network.UserInfo;
import com.plantrecognition.app.utils.UserManager;
import java.io.File;
import java.util.HashMap;
import java.util.Map;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class EditProfileActivity extends AppCompatActivity {

    private static final int PICK_IMAGE = 1;

    private ImageView ivAvatar;
    private ImageView btnBack;
    private EditText etNickname;
    private EditText etBio;
    private Button btnSave;
    private UserManager userManager;
    private Uri selectedImageUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_edit_profile);

        userManager = UserManager.getInstance(this);

        initViews();
        loadUserInfo();
        setListeners();
    }

    private void initViews() {
        ivAvatar = findViewById(R.id.ivEditAvatar);
        btnBack = findViewById(R.id.btnBack);
        etNickname = findViewById(R.id.etNickname);
        etBio = findViewById(R.id.etBio);
        btnSave = findViewById(R.id.btnSave);
    }

    private void loadUserInfo() {
        String nickname = userManager.getNickname();
        String avatar = userManager.getAvatar();

        if (nickname != null && !nickname.isEmpty()) {
            etNickname.setText(nickname);
        }

        if (avatar != null && !avatar.isEmpty()) {
            String fullAvatarUrl;
            if (avatar.startsWith("http://") || avatar.startsWith("https://")) {
                fullAvatarUrl = avatar;
            } else if (avatar.startsWith("/uploads/")) {
                fullAvatarUrl = ApiClient.getBaseUrl() + "/api/v1" + avatar;
            } else if (avatar.startsWith("/")) {
                fullAvatarUrl = ApiClient.getBaseUrl() + avatar;
            } else {
                fullAvatarUrl = avatar;
            }
            Glide.with(this)
                    .load(fullAvatarUrl)
                    .circleCrop()
                    .placeholder(R.mipmap.ic_launcher)
                    .into(ivAvatar);
        }

        String token = userManager.getToken();
        if (token != null && !token.isEmpty()) {
            ApiClient.getApiService().getUserInfo("Bearer " + token)
                    .enqueue(new Callback<ApiResponse<UserInfo>>() {
                        @Override
                        public void onResponse(Call<ApiResponse<UserInfo>> call, Response<ApiResponse<UserInfo>> response) {
                            if (response.isSuccessful() && response.body() != null) {
                                ApiResponse<UserInfo> apiResponse = response.body();
                                if (apiResponse.isSuccess() && apiResponse.getData() != null) {
                                    UserInfo userInfo = apiResponse.getData();
                                    if (userInfo.getBio() != null) {
                                        etBio.setText(userInfo.getBio());
                                    }
                                }
                            }
                        }

                        @Override
                        public void onFailure(Call<ApiResponse<UserInfo>> call, Throwable t) {
                        }
                    });
        }
    }

    private void setListeners() {
        btnBack.setOnClickListener(v -> finish());

        ivAvatar.setOnClickListener(v -> {
            Intent intent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
            startActivityForResult(intent, PICK_IMAGE);
        });

        btnSave.setOnClickListener(v -> saveProfile());
    }

    private void saveProfile() {
        String nickname = etNickname.getText().toString().trim();
        String bio = etBio.getText().toString().trim();

        if (nickname.isEmpty()) {
            etNickname.setError("请输入昵称");
            return;
        }

        btnSave.setEnabled(false);

        if (selectedImageUri != null) {
            uploadAvatarAndProfile(nickname, bio);
        } else {
            updateProfile(nickname, bio, null);
        }
    }

    private void uploadAvatarAndProfile(String nickname, String bio) {
        try {
            File file = new File(getRealPathFromUri(selectedImageUri));
            if (file == null || !file.exists()) {
                Toast.makeText(this, "无法获取图片", Toast.LENGTH_SHORT).show();
                btnSave.setEnabled(true);
                return;
            }
            
            RequestBody requestBody = RequestBody.create(MediaType.parse("image/*"), file);
            MultipartBody.Part imagePart = MultipartBody.Part.createFormData("file", file.getName(), requestBody);
            
            ApiClient.getApiService().uploadImage(imagePart)
                    .enqueue(new Callback<ApiResponse<UploadResponse>>() {
                        @Override
                        public void onResponse(Call<ApiResponse<UploadResponse>> call, Response<ApiResponse<UploadResponse>> response) {
                            if (response.isSuccessful() && response.body() != null && response.body().isSuccess()) {
                                String avatarUrl = response.body().getData().getUrl();
                                updateProfile(nickname, bio, avatarUrl);
                            } else {
                                Toast.makeText(EditProfileActivity.this, "头像上传失败", Toast.LENGTH_SHORT).show();
                                btnSave.setEnabled(true);
                            }
                        }

                        @Override
                        public void onFailure(Call<ApiResponse<UploadResponse>> call, Throwable t) {
                            Toast.makeText(EditProfileActivity.this, "网络错误: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                            btnSave.setEnabled(true);
                        }
                    });
        } catch (Exception e) {
            Toast.makeText(this, "处理图片失败: " + e.getMessage(), Toast.LENGTH_SHORT).show();
            btnSave.setEnabled(true);
        }
    }

    private String getRealPathFromUri(Uri uri) {
        try {
            // Try to get path from content resolver
            String[] projection = {MediaStore.Images.Media.DATA};
            android.database.Cursor cursor = getContentResolver().query(uri, projection, null, null, null);
            if (cursor != null && cursor.moveToFirst()) {
                int columnIndex = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA);
                String path = cursor.getString(columnIndex);
                cursor.close();
                if (path != null && new File(path).exists()) {
                    return path;
                }
            }
            
            // If cursor method fails, try to copy to temp file
            return copyUriToTempFile(uri);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    private String copyUriToTempFile(Uri uri) {
        try {
            java.io.InputStream inputStream = getContentResolver().openInputStream(uri);
            if (inputStream == null) return null;
            
            File tempFile = new File(getCacheDir(), "temp_avatar_" + System.currentTimeMillis() + ".jpg");
            java.io.FileOutputStream outputStream = new java.io.FileOutputStream(tempFile);
            
            byte[] buffer = new byte[4096];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }
            
            inputStream.close();
            outputStream.close();
            
            return tempFile.getAbsolutePath();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    private void updateProfile(String nickname, String bio, String avatarUrl) {
        Map<String, Object> request = new HashMap<>();
        request.put("nickname", nickname);
        request.put("bio", bio);
        if (avatarUrl != null) {
            request.put("avatar_url", avatarUrl);
        }

        String token = userManager.getToken();
        ApiClient.getApiService().updateProfile("Bearer " + token, request)
                .enqueue(new Callback<ApiResponse<Map<String, Object>>>() {
                    @Override
                    public void onResponse(Call<ApiResponse<Map<String, Object>>> call, Response<ApiResponse<Map<String, Object>>> response) {
                        btnSave.setEnabled(true);
                        if (response.isSuccessful() && response.body() != null) {
                            ApiResponse<Map<String, Object>> apiResponse = response.body();
                            if (apiResponse.isSuccess()) {
                                String finalAvatar = avatarUrl != null ? avatarUrl : userManager.getAvatar();
                                userManager.saveUserInfo(
                                        userManager.getUserId(),
                                        userManager.getUsername(),
                                        nickname,
                                        finalAvatar,
                                        userManager.getToken()
                                );
                                Toast.makeText(EditProfileActivity.this, "保存成功", Toast.LENGTH_SHORT).show();
                                finish();
                            } else {
                                Toast.makeText(EditProfileActivity.this, apiResponse.getMessage(), Toast.LENGTH_SHORT).show();
                            }
                        } else {
                            Toast.makeText(EditProfileActivity.this, "保存失败", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<ApiResponse<Map<String, Object>>> call, Throwable t) {
                        btnSave.setEnabled(true);
                        Toast.makeText(EditProfileActivity.this, "网络错误: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == PICK_IMAGE && resultCode == RESULT_OK && data != null) {
            selectedImageUri = data.getData();
            Glide.with(this)
                    .load(selectedImageUri)
                    .circleCrop()
                    .into(ivAvatar);
        }
    }
}
