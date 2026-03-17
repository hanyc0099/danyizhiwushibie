package com.plantrecognition.app.recognition;

import android.content.Context;
import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.Bitmap.Config;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;
import org.opencv.android.Utils;
import org.opencv.core.Mat;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;
import org.tensorflow.lite.Interpreter;
import org.tensorflow.lite.support.common.FileUtil;
import org.tensorflow.lite.support.common.TensorProcessor;
import org.tensorflow.lite.support.common.ops.NormalizeOp;
import org.tensorflow.lite.support.image.ImageProcessor;
import org.tensorflow.lite.support.image.TensorImage;
import org.tensorflow.lite.support.image.ops.ResizeOp;
import org.tensorflow.lite.support.label.TensorLabel;
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.MappedByteBuffer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 本地植物识别器 - TensorFlow Lite版本
 * 完全离线运行，无需网络
 */
public class LocalPlantRecognizerTFLite {

    private static final String TAG = "LocalPlantRecognizer";
    private static final int INPUT_SIZE = 224;
    private static final String MODEL_NAME = "plant_50class.tflite";
    private static final String LABELS_NAME = "labels_50class.txt";
    private static final String INFO_NAME = "plant_50class.json";
    private static final String MAPPING_NAME = "class_mapping.json";

    private Interpreter interpreter;
    private List<String> labels = new ArrayList<>();
    private List<PlantInfo> plantInfos = new ArrayList<>();
    private Map<Integer, Integer> classMapping = new HashMap<>(); // 模型索引 -> 数据库class_id
    private boolean isInitialized = false;
    private boolean useOpenCV = false;
    
    // TFLite图像处理器
    private ImageProcessor imageProcessor;
    private TensorProcessor probabilityProcessor;

    public LocalPlantRecognizerTFLite(Context context) {
        StringBuilder errorMsg = new StringBuilder();
        
        try {
            // 尝试加载OpenCV（可选）
            try {
                System.loadLibrary("opencv_java4");
                useOpenCV = true;
                Log.d(TAG, "OpenCV库加载成功");
            } catch (UnsatisfiedLinkError e) {
                Log.w(TAG, "OpenCV库加载失败，将使用原生预处理: " + e.getMessage());
                useOpenCV = false;
            }

            // 检查assets文件
            checkAssets(context);
            
            // 初始化TFLite解释器
            try {
                initInterpreter(context);
            } catch (Exception e) {
                errorMsg.append("TFLite初始化失败: ").append(e.getMessage()).append("\n");
                Log.e(TAG, "TFLite初始化失败", e);
                throw e;
            }
            
            // 加载标签
            try {
                loadLabels(context);
            } catch (Exception e) {
                errorMsg.append("标签加载失败: ").append(e.getMessage()).append("\n");
                Log.e(TAG, "标签加载失败", e);
                throw e;
            }
            
            // 加载植物信息
            try {
                loadPlantInfo(context);
            } catch (Exception e) {
                errorMsg.append("植物信息加载失败: ").append(e.getMessage()).append("\n");
                Log.e(TAG, "植物信息加载失败", e);
                throw e;
            }

            // 加载类别映射
            try {
                loadClassMapping(context);
            } catch (Exception e) {
                errorMsg.append("类别映射加载失败: ").append(e.getMessage()).append("\n");
                Log.e(TAG, "类别映射加载失败", e);
                throw e;
            }

            // 初始化图像处理器
            imageProcessor = new ImageProcessor.Builder()
                .add(new ResizeOp(INPUT_SIZE, INPUT_SIZE, ResizeOp.ResizeMethod.BILINEAR))
                .build();
                
            // 初始化概率处理器
            probabilityProcessor = new TensorProcessor.Builder()
                .add(new NormalizeOp(0.0f, 255.0f))
                .build();
            
            isInitialized = true;
            Log.d(TAG, "本地识别器初始化成功，支持 " + labels.size() + " 种植物");
        } catch (Exception e) {
            Log.e(TAG, "本地识别器初始化失败: " + errorMsg.toString() + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * 检查assets文件是否存在
     */
    private void checkAssets(Context context) {
        AssetManager assetManager = context.getAssets();
        try {
            String[] assets = assetManager.list("");
            Log.d(TAG, "=== Assets目录内容 ===");
            boolean hasModel = false;
            boolean hasLabels = false;
            boolean hasInfo = false;
            for (String asset : assets) {
                Log.d(TAG, "Asset: " + asset);
                if (asset.equals(MODEL_NAME)) hasModel = true;
                if (asset.equals(LABELS_NAME)) hasLabels = true;
                if (asset.equals(INFO_NAME)) hasInfo = true;
            }
            
            if (!hasModel) Log.e(TAG, "错误: 未找到模型文件 " + MODEL_NAME);
            if (!hasLabels) Log.e(TAG, "错误: 未找到标签文件 " + LABELS_NAME);
            if (!hasInfo) Log.e(TAG, "错误: 未找到信息文件 " + INFO_NAME);
            
        } catch (IOException e) {
            Log.e(TAG, "无法列出assets: " + e.getMessage());
        }
    }
    
    /**
     * 初始化TFLite解释器
     */
    private void initInterpreter(Context context) throws IOException {
        try {
            // 加载模型文件
            MappedByteBuffer modelBuffer = FileUtil.loadMappedFile(context, MODEL_NAME);
            Log.d(TAG, "模型文件加载成功，大小: " + modelBuffer.capacity() + " bytes");
            
            // 配置解释器选项
            Interpreter.Options options = new Interpreter.Options();
            options.setNumThreads(4);  // 使用4线程加速
            
            // 创建解释器
            interpreter = new Interpreter(modelBuffer, options);
            Log.d(TAG, "TFLite解释器创建成功");
            
            // 打印输入输出信息
            int[] inputShape = interpreter.getInputTensor(0).shape();
            int[] outputShape = interpreter.getOutputTensor(0).shape();
            Log.d(TAG, "模型输入形状: " + arrayToString(inputShape));
            Log.d(TAG, "模型输出形状: " + arrayToString(outputShape));
            
        } catch (Exception e) {
            Log.e(TAG, "TFLite解释器初始化失败: " + e.getMessage());
            Log.e(TAG, "异常类型: " + e.getClass().getName());
            throw new IOException("模型加载失败: " + e.getMessage(), e);
        }
    }

    /**
     * 检查是否初始化成功
     */
    public boolean isInitialized() {
        return isInitialized && interpreter != null;
    }

    /**
     * 识别植物
     * @param bitmap 输入图像
     * @return 识别结果
     */
    public RecognitionResult recognize(Bitmap bitmap) {
        if (!isInitialized || interpreter == null) {
            return RecognitionResult.error("模型未加载，请检查assets文件");
        }

        try {
            // 1. 预处理图像
            Bitmap processedBitmap;
            if (useOpenCV) {
                processedBitmap = preprocessWithOpenCV(bitmap);
            } else {
                processedBitmap = preprocessNative(bitmap);
            }

            // 2. 获取输入形状
            int[] inputShape = interpreter.getInputTensor(0).shape();
            Log.d(TAG, "模型输入形状: " + arrayToString(inputShape));
            
            // 根据模型格式选择输入方式
            float[][][][] inputArray;
            
            if (inputShape.length == 4 && inputShape[1] == 3 && inputShape[2] == 224 && inputShape[3] == 224) {
                // NCHW格式 [1, 3, 224, 224]
                inputArray = bitmapToNCHW(processedBitmap);
            } else if (inputShape.length == 4 && inputShape[1] == 224 && inputShape[2] == 224 && inputShape[3] == 3) {
                // NHWC格式 [1, 224, 224, 3]
                inputArray = bitmapToNHWC(processedBitmap);
            } else {
                return RecognitionResult.error("不支持的输入格式: " + arrayToString(inputShape));
            }

            // 3. 准备输出缓冲区 [1, numClasses]
            int[] outputShape = interpreter.getOutputTensor(0).shape();
            int numClasses = outputShape[1];
            float[][] outputArray = new float[1][numClasses];

            // 4. 运行推理
            interpreter.run(inputArray, outputArray);

            // 5. 获取概率（模型输出已是概率分布，无需再softmax）
            float[] probabilities = outputArray[0];

            // 6. 获取Top-1结果
            int maxIndex = 0;
            float maxProb = probabilities[0];
            for (int i = 1; i < probabilities.length; i++) {
                if (probabilities[i] > maxProb) {
                    maxProb = probabilities[i];
                    maxIndex = i;
                }
            }

            // 7. 获取植物信息
            if (maxIndex >= plantInfos.size() || maxIndex >= labels.size()) {
                return RecognitionResult.error("识别结果索引超出范围");
            }
            
            PlantInfo info = plantInfos.get(maxIndex);
            String label = labels.get(maxIndex);

            // 7. 如果置信度太低，提示未知
            if (maxProb < 0.5) {
                return RecognitionResult.error("未能识别出植物（置信度太低: " + String.format("%.2f%%", maxProb * 100) + "）");
            }

            // 获取正确的数据库class_id
            Integer dbClassId = classMapping.get(maxIndex);
            if (dbClassId == null) {
                dbClassId = maxIndex; // 如果没有映射，使用模型索引
                Log.w(TAG, "未找到模型索引 " + maxIndex + " 的映射，使用默认值");
            }

            Log.d(TAG, "识别结果: " + label + " (" + info.scientificName + "), 置信度: " + String.format("%.2f%%", maxProb * 100) + ", 数据库class_id: " + dbClassId);

            return RecognitionResult.success(
                label,
                info.scientificName,
                maxProb,
                info.description,
                info.careTips,
                dbClassId,  // plantId 使用数据库class_id
                dbClassId   // classId 使用数据库class_id
            );

        } catch (Exception e) {
            Log.e(TAG, "识别失败: " + e.getMessage());
            e.printStackTrace();
            return RecognitionResult.error("识别失败: " + e.getMessage());
        }
    }

    /**
     * OpenCV图像预处理（修复版：正确处理颜色通道）
     */
    private Bitmap preprocessWithOpenCV(Bitmap bitmap) {
        Mat inputMat = new Mat();
        Utils.bitmapToMat(bitmap, inputMat);

        // 1. 转换为RGB（修复：Android Bitmap是RGBA格式，不是BGR）
        Mat rgbMat = new Mat();
        Imgproc.cvtColor(inputMat, rgbMat, Imgproc.COLOR_RGBA2RGB);

        // 2. 尺寸归一化（移除高斯降噪，避免损失细节）
        Mat resizedMat = new Mat();
        Imgproc.resize(rgbMat, resizedMat, new Size(INPUT_SIZE, INPUT_SIZE), 0, 0, Imgproc.INTER_LINEAR);

        // Mat -> Bitmap
        Bitmap outputBitmap = Bitmap.createBitmap(INPUT_SIZE, INPUT_SIZE, Config.ARGB_8888);
        Utils.matToBitmap(resizedMat, outputBitmap);

        // 释放资源
        inputMat.release();
        rgbMat.release();
        resizedMat.release();

        return outputBitmap;
    }

    /**
     * 原生预处理（OpenCV失败时使用）
     */
    private Bitmap preprocessNative(Bitmap bitmap) {
        return Bitmap.createScaledBitmap(bitmap, INPUT_SIZE, INPUT_SIZE, true);
    }

    /**
     * Softmax函数
     */
    private float[] softmax(float[] scores) {
        float maxScore = scores[0];
        for (float score : scores) {
            if (score > maxScore) maxScore = score;
        }

        float sum = 0;
        float[] expScores = new float[scores.length];
        for (int i = 0; i < scores.length; i++) {
            expScores[i] = (float) Math.exp(scores[i] - maxScore);
            sum += expScores[i];
        }

        float[] probs = new float[scores.length];
        for (int i = 0; i < scores.length; i++) {
            probs[i] = expScores[i] / sum;
        }

        return probs;
    }

    /**
     * 将Bitmap转换为NCHW格式 [1, 3, 224, 224]
     * Keras模型期望输入: [0, 255]范围的原始像素值
     */
    private float[][][][] bitmapToNCHW(Bitmap bitmap) {
        Bitmap scaledBitmap = Bitmap.createScaledBitmap(bitmap, INPUT_SIZE, INPUT_SIZE, true);
        Bitmap rgbBitmap = scaledBitmap.copy(Bitmap.Config.ARGB_8888, false);
        
        int width = rgbBitmap.getWidth();
        int height = rgbBitmap.getHeight();
        
        float[][][][] nchw = new float[1][3][INPUT_SIZE][INPUT_SIZE];
        
        int[] pixels = new int[width * height];
        rgbBitmap.getPixels(pixels, 0, width, 0, 0, width, height);
        
        // 直接使用[0, 255]范围的像素值，不做归一化
        for (int h = 0; h < INPUT_SIZE; h++) {
            for (int w = 0; w < INPUT_SIZE; w++) {
                int pixel = pixels[h * width + w];
                
                nchw[0][0][h][w] = (float) ((pixel >> 16) & 0xFF);
                nchw[0][1][h][w] = (float) ((pixel >> 8) & 0xFF);
                nchw[0][2][h][w] = (float) (pixel & 0xFF);
            }
        }
        
        if (scaledBitmap != bitmap) {
            scaledBitmap.recycle();
        }
        if (rgbBitmap != scaledBitmap) {
            rgbBitmap.recycle();
        }
        
        return nchw;
    }
    
    /**
     * 将Bitmap转换为NHWC格式 [1, 224, 224, 3]
     * Keras模型期望输入: [0, 255]范围的原始像素值
     */
    private float[][][][] bitmapToNHWC(Bitmap bitmap) {
        Bitmap scaledBitmap = Bitmap.createScaledBitmap(bitmap, INPUT_SIZE, INPUT_SIZE, true);
        Bitmap rgbBitmap = scaledBitmap.copy(Bitmap.Config.ARGB_8888, false);
        
        int width = rgbBitmap.getWidth();
        int height = rgbBitmap.getHeight();
        
        float[][][][] nhwc = new float[1][INPUT_SIZE][INPUT_SIZE][3];
        
        int[] pixels = new int[width * height];
        rgbBitmap.getPixels(pixels, 0, width, 0, 0, width, height);
        
        // 直接使用[0, 255]范围的像素值，不做归一化
        for (int h = 0; h < INPUT_SIZE; h++) {
            for (int w = 0; w < INPUT_SIZE; w++) {
                int pixel = pixels[h * width + w];
                
                nhwc[0][h][w][0] = (float) ((pixel >> 16) & 0xFF);
                nhwc[0][h][w][1] = (float) ((pixel >> 8) & 0xFF);
                nhwc[0][h][w][2] = (float) (pixel & 0xFF);
            }
        }
        
        if (scaledBitmap != bitmap) {
            scaledBitmap.recycle();
        }
        if (rgbBitmap != scaledBitmap) {
            rgbBitmap.recycle();
        }
        
        return nhwc;
    }

    /**
     * 加载标签
     */
    private void loadLabels(Context context) throws IOException {
        AssetManager assetManager = context.getAssets();
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(assetManager.open(LABELS_NAME))
        );
        String line;
        while ((line = reader.readLine()) != null) {
            labels.add(line.trim());
        }
        reader.close();
        Log.d(TAG, "加载了 " + labels.size() + " 个标签");
    }

    /**
     * 加载植物信息
     */
    private void loadPlantInfo(Context context) throws Exception {
        AssetManager assetManager = context.getAssets();
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(assetManager.open(INFO_NAME))
        );
        StringBuilder jsonBuilder = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            jsonBuilder.append(line);
        }
        reader.close();

        JSONObject json = new JSONObject(jsonBuilder.toString());
        JSONArray classes = json.getJSONArray("classes");
        JSONArray scientific = json.getJSONArray("scientific");
        JSONArray descriptions = json.getJSONArray("descriptions");
        JSONArray careTips = json.getJSONArray("care_tips");

        for (int i = 0; i < classes.length(); i++) {
            PlantInfo info = new PlantInfo();
            info.id = i + 1;
            info.classId = i;
            info.name = classes.getString(i);
            info.scientificName = scientific.getString(i);
            info.description = descriptions.getString(i);
            info.careTips = careTips.getString(i);
            plantInfos.add(info);
        }
        Log.d(TAG, "加载了 " + plantInfos.size() + " 个植物信息");
    }

    /**
     * 加载类别映射（模型索引 -> 数据库class_id）
     */
    private void loadClassMapping(Context context) throws Exception {
        AssetManager assetManager = context.getAssets();
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(assetManager.open(MAPPING_NAME))
        );
        StringBuilder jsonBuilder = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            jsonBuilder.append(line);
        }
        reader.close();

        JSONArray mappingArray = new JSONArray(jsonBuilder.toString());
        for (int i = 0; i < mappingArray.length(); i++) {
            JSONObject item = mappingArray.getJSONObject(i);
            int modelIndex = item.getInt("model_index");
            int dbClassId = item.getInt("db_class_id");
            classMapping.put(modelIndex, dbClassId);
        }
        Log.d(TAG, "加载了 " + classMapping.size() + " 个类别映射");
    }

    /**
     * 辅助方法：数组转字符串
     */
    private String arrayToString(int[] array) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < array.length; i++) {
            sb.append(array[i]);
            if (i < array.length - 1) sb.append(", ");
        }
        sb.append("]");
        return sb.toString();
    }

    /**
     * 释放资源
     */
    public void close() {
        if (interpreter != null) {
            interpreter.close();
            interpreter = null;
        }
    }

    /**
     * 植物信息数据类
     */
    private static class PlantInfo {
        int id;
        int classId;
        String name;
        String scientificName;
        String description;
        String careTips;
    }

    /**
     * 识别结果类
     */
    public static class RecognitionResult {
        public final boolean success;
        public final String plantName;
        public final String scientificName;
        public final float confidence;
        public final String description;
        public final String careTips;
        public final String errorMessage;
        public final int plantId;
        public final int classId;

        private RecognitionResult(boolean success, String plantName, String scientificName, 
                                 float confidence, String description, String careTips, String errorMessage,
                                 int plantId, int classId) {
            this.success = success;
            this.plantName = plantName;
            this.scientificName = scientificName;
            this.confidence = confidence;
            this.description = description;
            this.careTips = careTips;
            this.errorMessage = errorMessage;
            this.plantId = plantId;
            this.classId = classId;
        }

        public static RecognitionResult success(String plantName, String scientificName, 
                                               float confidence, String description, String careTips,
                                               int plantId, int classId) {
            return new RecognitionResult(true, plantName, scientificName, confidence, description, careTips, null, plantId, classId);
        }

        public static RecognitionResult error(String errorMessage) {
            return new RecognitionResult(false, null, null, 0, null, null, errorMessage, 0, 0);
        }
    }
}
