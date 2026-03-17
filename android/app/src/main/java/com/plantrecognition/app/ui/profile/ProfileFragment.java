package com.plantrecognition.app.ui.profile;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.cardview.widget.CardView;
import androidx.fragment.app.Fragment;
import com.bumptech.glide.Glide;
import com.plantrecognition.app.R;
import com.plantrecognition.app.network.ApiClient;
import com.plantrecognition.app.network.ApiResponse;
import com.plantrecognition.app.network.UserInfo;
import com.plantrecognition.app.MainActivity;
import com.plantrecognition.app.utils.UserManager;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ProfileFragment extends Fragment {

    private ImageView ivAvatar;
    private TextView tvNickname;
    private TextView tvBadge;
    private CardView cardCollection;
    private Button btnLogout;
    private UserManager userManager;
    private OnNavigateListener navigateListener;

    public interface OnNavigateListener {
        void onNavigateToLogin();
        void onNavigateToHistory();
        void onNavigateToFavorites();
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_profile, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        userManager = UserManager.getInstance(requireContext());

        initViews(view);
        setListeners();
        loadUserInfo();
    }

    private void initViews(View view) {
        ivAvatar = view.findViewById(R.id.ivAvatar);
        tvNickname = view.findViewById(R.id.tvNickname);
        tvBadge = view.findViewById(R.id.tvBadge);
        cardCollection = view.findViewById(R.id.cardCollection);
        btnLogout = view.findViewById(R.id.btnLogout);
    }

    private void setListeners() {
        if (ivAvatar != null) {
            ivAvatar.setOnClickListener(v -> {
                Intent intent = new Intent(requireContext(), EditProfileActivity.class);
                startActivity(intent);
            });
        }

        if (cardCollection != null) {
            cardCollection.setOnClickListener(v -> {
                // Navigate to History tab (index 2)
                if (getActivity() instanceof MainActivity) {
                    ((MainActivity) getActivity()).navigateToTab(2);
                }
            });
        }

        if (btnLogout != null) {
            btnLogout.setOnClickListener(v -> {
                new AlertDialog.Builder(requireContext())
                        .setTitle("退出登录")
                        .setMessage("确定要退出登录吗？")
                        .setPositiveButton("确定", (dialog, which) -> {
                            userManager.clearUserInfo();
                            if (navigateListener != null) {
                                navigateListener.onNavigateToLogin();
                            }
                        })
                        .setNegativeButton("取消", null)
                        .show();
            });
        }
    }

    private void loadUserInfo() {
        String nickname = userManager.getNickname();
        String username = userManager.getUsername();
        String avatar = userManager.getAvatar();

        if (nickname != null && !nickname.isEmpty() && tvNickname != null) {
            tvNickname.setText(nickname);
        } else if (tvNickname != null) {
            tvNickname.setText(username);
        }

        if (avatar != null && !avatar.isEmpty() && ivAvatar != null) {
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
                    .placeholder(R.drawable.ic_avatar_default)
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
                                    // User info loaded successfully
                                }
                            }
                        }

                        @Override
                        public void onFailure(Call<ApiResponse<UserInfo>> call, Throwable t) {
                        }
                    });
        }
    }

    @Override
    public void onResume() {
        super.onResume();
        loadUserInfo();
    }

    public void setOnNavigateListener(OnNavigateListener listener) {
        this.navigateListener = listener;
    }
}
