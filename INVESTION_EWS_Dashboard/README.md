# INVESTION — Volatility Intelligence Dashboard

Dashboard Streamlit satu halaman berbasis output notebook/model tim. Halaman langsung dimulai dengan KPI EWS, risk gauge, lintasan prediksi dan validasi, benchmark, snapshot EWS, pilar SHAP, penjelasan SHAP lokal, proyeksi, serta rekomendasi dan simulasi portofolio.

## Palet visual
- Background kuning hangat / gradasi: `#FFF2A7`
- Light azure: `#BEDEFF`
- Baseline naif: `#FFF2A7`
- Warning: `#FFA500`
- High risk / CatBoost line: `#930031`
- Teks utama: `#472F26`

## Struktur
- `dashboard.py`: aplikasi dashboard satu halaman; membaca keluaran analisis dari folder `data/`.
- `app.py`: versi dashboard sebelumnya.
- `analisis/coba 7 fix.ipynb`: notebook analisis CatBoost dan SHAP. Ekspor CSV diarahkan ke `data/` agar dashboard memakai hasil analisis terbaru.
- `requirements.txt`: dependensi dashboard.
- `data/`: CSV keluaran notebook untuk evaluasi model, SHAP, proyeksi, dan output EWS.
- `data/model_evaluation_metrics.csv`: perbandingan RMSE, MAE, dan MAPE dari evaluasi notebook; file ini diperbarui saat sel evaluasi dijalankan.
- `data/validation_predictions.csv`: pasangan aktual, prediksi CatBoost, dan baseline periode validasi yang diekspor notebook untuk grafik lintasan.
- Tabel data pada dashboard dibatasi maksimal 5 baris; tombol unduh tetap menyediakan data lengkap.
- Visualisasi yang tidak ditampilkan pada halaman utama: heatmap data mentah, heatmap SHAP, plot fitur 3D, dan grafik/tabel seluruh fitur SHAP. Ringkasan top-3 fitur serta SHAP lokal tetap ditampilkan.

## Menjalankan di Windows / VS Code
Buka terminal di folder yang berisi `app.py`, lalu:

```powershell
uv pip install -r requirements.txt
streamlit run dashboard.py
```

Jalankan notebook analisis terlebih dahulu untuk memperbarui CSV yang dipakai dashboard. Dashboard tidak melatih ulang CatBoost setiap kali halaman dibuka.
Tabel dashboard memakai teks kuning muda pada baris gelap agar tetap kontras dan mudah dibaca.

Agar sidebar langsung tertutup saat dibuka, aplikasi memakai `initial_sidebar_state="collapsed"`. Klik tombol panah di header untuk membukanya kembali.

## Format output opsional

### `data/validation_predictions.csv`
Notebook `analisis/coba 7 fix.ipynb` mengekspor seri yang sama dengan grafik evaluasi setelah sel visualisasi lintasan dijalankan. Jalankan notebook dari folder proyek atau `analisis`; file ditulis ke `data/validation_predictions.csv`. Dashboard menampilkannya pada grafik validasi terpisah dari grafik data uji dengan urutan seri, palet Set2, skala desimal, dan metrik yang sama dengan notebook. Kolomnya adalah `Date`, `Actual_Volatility`, `CatBoost_Pred_Vol`, dan `Baseline_Naif_Pred`. Jika file memiliki akhiran duplikat seperti ` (1)`, dashboard memilih salinan yang terakhir diperbarui.

## Catatan interpretasi
- File test yang dilampirkan memuat 359 baris prediksi EWS dan status risiko hingga 22 Mei 2026, bukan label aktual berpasangan. Dashboard tidak membuat nilai aktual test secara sintetis.
- CSV SHAP validasi memuat tanggal dan kontribusi SHAP, bukan prediksi/target aktual; lintasan validasi diekspor terpisah oleh sel grafik evaluasi notebook.
- Peningkatan RMSE 24,24%, RMSE baseline 0,004118, dan RMSE CatBoost 0,003120 diambil dari ringkasan pada notebook tim dan diberi label metrik validasi. Verifikasi angka tersebut pada hasil final tim sebelum presentasi.
- Grafik SHAP lokal menampilkan kontribusi bertanda bergaya waterfall karena base value/output value tidak tersedia pada CSV; tidak mengklaim sebagai waterfall lengkap dengan base value.
- VaR 99% merupakan perkiraan simulasi sederhana dengan asumsi Gaussian dan volatilitas 5-hari dari model; bukan nilai VaR resmi yang memperhitungkan seluruh karakteristik portofolio maupun biaya instrumen hedging.
