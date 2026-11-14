package com.securityasspro.app;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.database.Cursor;
import android.provider.OpenableColumns;
import android.webkit.WebView;
import android.webkit.WebSettings;
import android.webkit.WebViewClient;
import android.webkit.JavascriptInterface;
import android.graphics.Color;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.InputStream;
import java.security.MessageDigest;
import java.util.Locale;

public class MainActivity extends Activity {

    private WebView webView;
    private static final int REQUEST_FILES = 1001;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().setStatusBarColor(Color.rgb(8, 13, 27));
        getWindow().setNavigationBarColor(Color.rgb(8, 13, 27));

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(8, 13, 27));

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(false);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);

        webView.addJavascriptInterface(new AndroidBridge(), "Android");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(
                    WebView view,
                    String url
            ) {
                return !url.startsWith("file:///android_asset/");
            }
        });

        setContentView(webView);
        webView.loadUrl("file:///android_asset/index.html");
    }

    public class AndroidBridge {

        @JavascriptInterface
        public void openFilePicker() {
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("*/*");
                intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                startActivityForResult(intent, REQUEST_FILES);
            });
        }
    }

    @Override
    protected void onActivityResult(
            int requestCode,
            int resultCode,
            Intent data
    ) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode != REQUEST_FILES) return;

        if (resultCode != RESULT_OK || data == null) {
            sendMessage("Sélection annulée.");
            return;
        }

        JSONArray results = new JSONArray();

        try {
            if (data.getClipData() != null) {
                int count = data.getClipData().getItemCount();

                for (int i = 0; i < count; i++) {
                    Uri uri = data.getClipData().getItemAt(i).getUri();
                    results.put(analyzeFile(uri));
                }

            } else if (data.getData() != null) {
                results.put(analyzeFile(data.getData()));
            }

            sendResults(results);

        } catch (Exception e) {
            sendMessage("Erreur pendant l'analyse : " + e.getMessage());
        }
    }

    private JSONObject analyzeFile(Uri uri) {

        JSONObject result = new JSONObject();

        try {
            String name = getFileName(uri);
            long size = getFileSize(uri);

            MessageDigest digest = MessageDigest.getInstance("SHA-256");

            try (InputStream input = getContentResolver()
                    .openInputStream(uri)) {

                if (input == null) {
                    throw new Exception("Impossible de lire ce fichier.");
                }

                byte[] buffer = new byte[8192];
                int bytesRead;

                while ((bytesRead = input.read(buffer)) != -1) {
                    digest.update(buffer, 0, bytesRead);
                }
            }

            StringBuilder hash = new StringBuilder();

            for (byte b : digest.digest()) {
                hash.append(String.format(Locale.US, "%02x", b & 0xff));
            }

            JSONArray alerts = new JSONArray();
            String status = "OK";

            String lowerName = name.toLowerCase(Locale.ROOT);

            String[] suspiciousExtensions = {
                ".apk", ".exe", ".bat", ".cmd",
                ".scr", ".vbs", ".ps1", ".jar"
            };

            for (String extension : suspiciousExtensions) {
                if (lowerName.endsWith(extension)) {
                    alerts.put(
                        "Extension à examiner : " + extension
                    );
                    status = "A_VERIFIER";
                    break;
                }
            }

            if (size == 0) {
                alerts.put("Fichier vide.");
                status = "A_VERIFIER";
            }

            result.put("nom_fichier", name);
            result.put("taille", size);
            result.put("sha256", hash.toString());
            result.put("statut", status);
            result.put("alertes", alerts);

        } catch (Exception e) {
            try {
                result.put("nom_fichier", getFileName(uri));
                result.put("statut", "ERREUR");
                result.put("alertes", new JSONArray()
                    .put(e.getMessage() == null
                        ? "Erreur de lecture."
                        : e.getMessage()));
            } catch (Exception ignored) {
            }
        }

        return result;
    }

    private String getFileName(Uri uri) {
        String name = "Fichier inconnu";

        try (Cursor cursor = getContentResolver()
                .query(uri, null, null, null, null)) {

            if (cursor != null
                    && cursor.moveToFirst()) {

                int index = cursor.getColumnIndex(
                    OpenableColumns.DISPLAY_NAME
                );

                if (index >= 0) {
                    name = cursor.getString(index);
                }
            }
        } catch (Exception ignored) {
        }

        return name;
    }

    private long getFileSize(Uri uri) {
        try (Cursor cursor = getContentResolver()
                .query(uri, null, null, null, null)) {

            if (cursor != null && cursor.moveToFirst()) {
                int index = cursor.getColumnIndex(
                    OpenableColumns.SIZE
                );

                if (index >= 0 && !cursor.isNull(index)) {
                    return cursor.getLong(index);
                }
            }
        } catch (Exception ignored) {
        }

        return -1;
    }

    private void sendResults(JSONArray results) {
        String json = JSONObject.quote(results.toString());

        runOnUiThread(() -> webView.evaluateJavascript(
            "if(window.onNativeScanResults){" +
            "window.onNativeScanResults(JSON.parse(" + json + "));" +
            "}",
            null
        ));
    }

    private void sendMessage(String message) {
        String safeMessage = JSONObject.quote(message);

        runOnUiThread(() -> webView.evaluateJavascript(
            "if(window.onNativeScanMessage){" +
            "window.onNativeScanMessage(" + safeMessage + ");" +
            "}",
            null
        ));
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
