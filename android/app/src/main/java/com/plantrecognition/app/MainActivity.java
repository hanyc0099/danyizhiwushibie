package com.plantrecognition.app;

import android.content.Intent;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.plantrecognition.app.ui.explore.ExploreFragment;
import com.plantrecognition.app.ui.history.HistoryFragment;
import com.plantrecognition.app.ui.home.HomeFragment;
import com.plantrecognition.app.ui.profile.ProfileFragment;
import com.plantrecognition.app.ui.recognize.RecognizeActivity;
import com.plantrecognition.app.utils.UserManager;

public class MainActivity extends AppCompatActivity implements
        ProfileFragment.OnNavigateListener,
        HistoryFragment.OnNavigateListener {

    private BottomNavigationView bottomNavigation;
    private UserManager userManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        userManager = UserManager.getInstance(this);

        // 检查登录状态
        if (!userManager.isLoggedIn()) {
            // 未登录，跳转到登录页面
            Intent intent = new Intent(this, com.plantrecognition.app.ui.login.LoginActivity.class);
            startActivity(intent);
            finish();
            return;
        }

        initViews();
        setupBottomNavigation();

        // 默认显示首页
        if (savedInstanceState == null) {
            loadFragment(new HomeFragment());
        }
    }

    private void initViews() {
        bottomNavigation = findViewById(R.id.bottomNavigation);
    }

    private void setupBottomNavigation() {
        bottomNavigation.setOnItemSelectedListener(item -> {
            int itemId = item.getItemId();
            if (itemId == R.id.nav_home) {
                loadFragment(new HomeFragment());
                return true;
            } else if (itemId == R.id.nav_explore) {
                loadFragment(new ExploreFragment());
                return true;
            } else if (itemId == R.id.nav_history) {
                loadFragment(new HistoryFragment());
                return true;
            } else if (itemId == R.id.nav_profile) {
                ProfileFragment profileFragment = new ProfileFragment();
                profileFragment.setOnNavigateListener(MainActivity.this);
                loadFragment(profileFragment);
                return true;
            }
            return false;
        });
    }

    private void loadFragment(Fragment fragment) {
        getSupportFragmentManager()
                .beginTransaction()
                .replace(R.id.fragmentContainer, fragment)
                .commit();
    }

    @Override
    public void onNavigateToLogin() {
        Intent intent = new Intent(this, com.plantrecognition.app.ui.login.LoginActivity.class);
        startActivity(intent);
        finish();
    }

    @Override
    public void onNavigateToHistory() {
        bottomNavigation.setSelectedItemId(R.id.nav_history);
    }

    @Override
    public void onNavigateToFavorites() {
        // 可以跳转到收藏页面或显示提示
    }

    public void navigateToTab(int tabIndex) {
        switch (tabIndex) {
            case 0:
                bottomNavigation.setSelectedItemId(R.id.nav_home);
                break;
            case 1:
                bottomNavigation.setSelectedItemId(R.id.nav_explore);
                break;
            case 2:
                bottomNavigation.setSelectedItemId(R.id.nav_history);
                break;
            case 3:
                bottomNavigation.setSelectedItemId(R.id.nav_profile);
                break;
        }
    }
}
