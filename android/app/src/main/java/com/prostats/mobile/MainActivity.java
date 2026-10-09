package com.prostats.mobile;

import android.app.Activity;
import android.content.ClipData;
import android.content.ContentValues;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.Window;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * ProStats Mobile: hosts the offline web app (assets/www) in a WebView.
 * The app is served from a private https origin so IndexedDB/localStorage are stable,
 * and a small JS bridge ("ProStatsNative") saves/shares the .json career file.
 */
public class MainActivity extends Activity {
    static final String HOST = "app.prostats.local";
    private static final int REQ_FILE = 41;

    private WebView web;
    private ValueCallback<Uri[]> fileCallback;
    private String pendingImport;
    private boolean pageReady = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Window w = getWindow();
        w.setStatusBarColor(Color.parseColor("#0A1120"));
        w.setNavigationBarColor(Color.parseColor("#121B2C"));

        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0A1120"));
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(true);
        s.setTextZoom(100);
        s.setMediaPlaybackRequiresUserGesture(true);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                if (!HOST.equals(u.getHost())) return null;
                String path = u.getPath();
                if (path == null || path.equals("/") || path.isEmpty()) path = "/index.html";
                try {
                    InputStream in = getAssets().open("www" + path);
                    return new WebResourceResponse(mimeFor(path), "utf-8", in);
                } catch (IOException e) {
                    return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found", null,
                            new ByteArrayInputStream(new byte[0]));
                }
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                if (HOST.equals(u.getHost())) return false;
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, u));
                } catch (Exception ignored) { }
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = callback;
                boolean images = false;
                String[] accept = params.getAcceptTypes();
                if (accept != null) {
                    for (String a : accept) {
                        if (a != null && a.startsWith("image")) images = true;
                    }
                }
                Intent i = new Intent(Intent.ACTION_GET_CONTENT);
                i.addCategory(Intent.CATEGORY_OPENABLE);
                i.setType(images ? "image/*" : "*/*");
                if (params.getMode() == FileChooserParams.MODE_OPEN_MULTIPLE) {
                    i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                }
                try {
                    startActivityForResult(Intent.createChooser(i, null), REQ_FILE);
                } catch (Exception e) {
                    fileCallback.onReceiveValue(null);
                    fileCallback = null;
                    return false;
                }
                return true;
            }
        });

        web.addJavascriptInterface(new Bridge(), "ProStatsNative");
        web.loadUrl("https://" + HOST + "/index.html");
        handleIntent(getIntent());
    }

    static String mimeFor(String path) {
        String p = path.toLowerCase();
        if (p.endsWith(".html")) return "text/html";
        if (p.endsWith(".js")) return "application/javascript";
        if (p.endsWith(".css")) return "text/css";
        if (p.endsWith(".png")) return "image/png";
        if (p.endsWith(".svg")) return "image/svg+xml";
        if (p.endsWith(".json") || p.endsWith(".webmanifest")) return "application/json";
        return "application/octet-stream";
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQ_FILE || fileCallback == null) return;
        Uri[] result = null;
        if (resultCode == RESULT_OK && data != null) {
            ClipData clip = data.getClipData();
            if (clip != null && clip.getItemCount() > 0) {
                result = new Uri[clip.getItemCount()];
                for (int i = 0; i < clip.getItemCount(); i++) result[i] = clip.getItemAt(i).getUri();
            } else if (data.getData() != null) {
                result = new Uri[]{data.getData()};
            }
        }
        fileCallback.onReceiveValue(result);
        fileCallback = null;
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        handleIntent(intent);
    }

    /** "Open with ProStats" / "Share to ProStats" for a .json save file. */
    private void handleIntent(Intent intent) {
        if (intent == null) return;
        Uri uri = null;
        if (Intent.ACTION_VIEW.equals(intent.getAction())) {
            uri = intent.getData();
        } else if (Intent.ACTION_SEND.equals(intent.getAction())) {
            Object extra = intent.getParcelableExtra(Intent.EXTRA_STREAM);
            if (extra instanceof Uri) uri = (Uri) extra;
            if (uri == null) {
                String txt = intent.getStringExtra(Intent.EXTRA_TEXT);
                if (txt != null && txt.trim().startsWith("{")) { deliverImport(txt); return; }
            }
        }
        if (uri == null) return;
        try {
            InputStream in = getContentResolver().openInputStream(uri);
            if (in == null) return;
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            byte[] buf = new byte[16384];
            int n;
            while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
            in.close();
            deliverImport(new String(bos.toByteArray(), StandardCharsets.UTF_8));
        } catch (Exception e) {
            Toast.makeText(this, "Não foi possível abrir o arquivo.", Toast.LENGTH_LONG).show();
        }
    }

    private void deliverImport(String text) {
        pendingImport = text;
        if (pageReady) flushImport();
    }

    private void flushImport() {
        if (pendingImport == null) return;
        final String js = "window.psImportText && window.psImportText(" + JSONObject.quote(pendingImport) + ")";
        pendingImport = null;
        web.post(new Runnable() {
            @Override public void run() { web.evaluateJavascript(js, null); }
        });
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        web.evaluateJavascript("(window.psBack && window.psBack()) ? 'y' : 'n'", new ValueCallback<String>() {
            @Override public void onReceiveValue(String value) {
                if (value == null || !value.contains("y")) finish();
            }
        });
    }

    private File writeCache(String name, String content) throws IOException {
        File dir = new File(getCacheDir(), "share");
        if (!dir.exists() && !dir.mkdirs()) throw new IOException("cache");
        File f = new File(dir, name);
        FileOutputStream out = new FileOutputStream(f);
        out.write(content.getBytes(StandardCharsets.UTF_8));
        out.close();
        return f;
    }

    static String safeName(String name) {
        String n = name == null ? "save.json" : name.replaceAll("[^A-Za-z0-9._-]", "_");
        if (!n.toLowerCase().endsWith(".json")) n = n + ".json";
        return n;
    }

    class Bridge {
        @JavascriptInterface
        public void ready() {
            runOnUiThread(new Runnable() {
                @Override public void run() { pageReady = true; flushImport(); }
            });
        }

        /** Saves the file to Downloads/ProStats and returns a readable location, or "" on failure. */
        @JavascriptInterface
        public String saveFile(String name, String content) {
            String fn = safeName(name);
            try {
                if (Build.VERSION.SDK_INT >= 29) {
                    ContentValues cv = new ContentValues();
                    cv.put(MediaStore.MediaColumns.DISPLAY_NAME, fn);
                    cv.put(MediaStore.MediaColumns.MIME_TYPE, "application/json");
                    cv.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ProStats");
                    Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
                    if (uri == null) return "";
                    OutputStream out = getContentResolver().openOutputStream(uri);
                    if (out == null) return "";
                    out.write(content.getBytes(StandardCharsets.UTF_8));
                    out.close();
                    return "Downloads/ProStats/" + fn;
                } else {
                    File dir = getExternalFilesDir(null);
                    if (dir == null) dir = getFilesDir();
                    File f = new File(dir, fn);
                    FileOutputStream out = new FileOutputStream(f);
                    out.write(content.getBytes(StandardCharsets.UTF_8));
                    out.close();
                    return f.getAbsolutePath();
                }
            } catch (Exception e) {
                return "";
            }
        }

        /** Opens the Android share sheet (WhatsApp, Drive, e-mail...) with the .json file. */
        @JavascriptInterface
        public void shareFile(final String name, final String content) {
            runOnUiThread(new Runnable() {
                @Override public void run() {
                    try {
                        String fn = safeName(name);
                        writeCache(fn, content);
                        Uri uri = Uri.parse("content://" + SaveProvider.AUTHORITY + "/" + Uri.encode(fn));
                        Intent send = new Intent(Intent.ACTION_SEND);
                        send.setType("application/json");
                        send.putExtra(Intent.EXTRA_STREAM, uri);
                        send.putExtra(Intent.EXTRA_SUBJECT, fn);
                        send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        startActivity(Intent.createChooser(send, "ProStats"));
                    } catch (Exception e) {
                        Toast.makeText(MainActivity.this, "Erro ao compartilhar: " + e.getMessage(), Toast.LENGTH_LONG).show();
                    }
                }
            });
        }

        @JavascriptInterface
        public String platform() { return "android"; }
    }
}
