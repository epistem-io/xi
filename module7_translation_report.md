
# Module 7 Translation Report
Generated: 2025-11-06 13:43:37

## Summary
- **Total strings found**: 43
- **Translated**: 38 (88.4%)
- **Needs review**: 5 (11.6%)

## Translation Status by Type
Status              Needs Review  Translated
Type                                        
f-string                       4           9
help_text                      0           2
page_title                     0           1
st.button                      0           2
st.download_button             0           2
st.error                       0           2
st.file_uploader               0           1
st.info                        0           3
st.markdown                    0           1
st.metric                      1           2
st.number_input                0           1
st.selectbox                   0           1
st.slider                      0           1
st.subheader                   0           5
st.success                     0           2
st.title                       0           1
st.warning                     0           2

## Strings Needing Review

- **st.metric**: Koefisien Kappa
- **f-string**: ❌ {results['error']}
- **f-string**: {results['overall_accuracy']*100:.2f}%
- **f-string**: {results['kappa']:.3f}
- **f-string**: {results['n_total']} titik


## All Translated Strings

- **st.title**: Penilaian Akurasi Tematik
- **st.subheader**: Langkah 1: Unggah Data Referensi Lapangan
- **st.subheader**: Langkah 2: Konfigurasi dan Jalankan Penilaian
- **st.subheader**: Hasil Penilaian Akurasi
- **st.subheader**: Kinerja per Kelas
- **st.subheader**: 🔄 Matriks Konfusi
- **st.error**: ❌ Tidak ditemukan hasil klasifikasi dari Modul 6.
- **st.error**: Data validasi tidak berhasil dimuat dengan benar.
- **st.warning**: Selesaikan Modul 6 terlebih dahulu untuk menghasilkan peta klasifikasi tutupan lahan.
- **st.warning**: ⚠️ Harap unggah data validasi Anda terlebih dahulu.
- **st.success**: ✅ Peta klasifikasi dimuat dari Modul 6
- **st.success**: ✅ Penilaian akurasi tematik selesai!
- **st.info**: 📁 Unggah **shapefile .zip** yang berisi sampel validasi independen Anda dengan ID kelas.
- **st.info**: 💡 Pastikan shapefile Anda menyertakan semua file yang diperlukan (.shp, .shx, .dbf, .prj)
- **st.info**: 💡 Kembali ke Modul 6 untuk meningkatkan model klasifikasi Anda jika diperlukan
- **st.button**: 🎯 Evaluasi Akurasi Peta
- **st.button**: ⬅️ Kembali ke Modul 6
- **st.selectbox**: Kolom ID Kelas:
- **st.number_input**: Ukuran Piksel (meter):
- **st.slider**: Tingkat Kepercayaan untuk Interval Akurasi:
- **st.file_uploader**: Pilih shapefile terkompresi (.zip)
- **st.metric**: Akurasi Keseluruhan
- **st.metric**: Ukuran Sampel
- **st.download_button**: 📥 Unduh Ringkasan Hasil
- **st.download_button**: 📥 Unduh Metrik Kelas
- **help_text**: Kolom yang berisi pengenal kelas numerik (mis. 1, 2, 3, 4)
- **help_text**: Resolusi spasial untuk pengambilan sampel pada peta terklasifikasi
- **page_title**: Penilaian Akurasi Tematik
- **st.markdown**: **📍 Sebaran Titik Validasi:**
- **f-string**: <style>{f.read()}</style>
- **f-string**: Kesalahan memproses shapefile: {str(e)}
- **f-string**: ✅ {message}
- **f-string**: ❌ {message}
- **f-string**: ❌ Penilaian gagal: {results.get('error', 'Kesalahan tidak diketahui')}
- **f-string**: Interval Kepercayaan {confidence_pct}%
- **f-string**: {ci[0]*100:.1f}% - {ci[1]*100:.1f}%
- **f-string**: Prediksi {i}
- **f-string**: Aktual {i}
