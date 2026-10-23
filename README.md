# UTS Graf Sains Data

Analisis graf bipartite, Vector Space Modelling (VSM), dan sistem rekomendasi collaborative filtering KNN pada dataset e-commerce RetailRocket menggunakan Neo4j dan Python.

## Identitas

| | |
| :--- | :--- |
| **Nama** | MOCH. AKBAR HANAFI |
| **NIM** | 23031554018 |
| **No. Urut Presensi** | 3 |
| **Kelas** | GSD 2023E |
| **Program Studi** | S1 Sains Data, FMIPA Universitas Negeri Surabaya |
| **Mata Kuliah** | Graf Sains Data (3 SKS) |
| **Fold Training (P1)** | 2015-05-03 00:00:00 UTC s/d 2015-07-22 23:59:59 UTC (epoch ms: 1430611200000 – 1437609599999) |
| **Fold Testing (P2)** | 2015-07-23 00:00:00 UTC s/d 2015-08-12 23:59:59 UTC (epoch ms: 1437609600000 – 1439423999999) |

## Isi Repositori

```text
UTS GRAF/
├── UTS_GSD_23031554018_MOCH_AKBAR_HANAFI.ipynb  # Notebook utama berisi seluruh alur pengerjaan dan output
├── requirements.txt                             # Daftar dependensi Python
├── README.md                                    # Dokumentasi proyek
├── data/
│   └── events_subgraph.csv                      # Data subgraph interaksi di sekitar user target (25.886 baris)
└── plots/
    ├── vsm_user_projection.png                  # Plot proyeksi simpul User
    ├── vsm_item_projection.png                  # Plot proyeksi simpul Item (co-occurrence)
    ├── graph_before_similarity.png              # Kondisi graf sebelum perhitungan similarity
    ├── graph_after_similarity.png               # Kondisi graf sesudah perhitungan similarity
    └── knn_recommendations.png                  # Visualisasi peringkat rekomendasi KNN
```

## Cara Menjalankan

1. **Siapkan virtual environment dan instal dependensi:**
   ```bash
   uv venv myvenv --python 3.12
   source myvenv/bin/activate
   uv pip install -r requirements.txt
   ```

2. **Pastikan database Neo4j aktif di port 7687:**
   ```bash
   docker start neo4j
   # Jika container belum dibuat sebelumnya:
   # docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password123 neo4j:latest
   ```

3. **Buka dan jalankan notebook:**
   ```bash
   jupyter notebook UTS_GSD_23031554018_MOCH_AKBAR_HANAFI.ipynb
   ```
   Pilih menu **Kernel -> Restart & Run All**. Seluruh alur (filter data, penentuan user target, pembentukan subgraph, impor batch ke Neo4j, VSM, kalkulasi similarity, sampai evaluasi rekomendasi) sudah berjalan mandiri di dalam notebook.

## Alur Pengerjaan

1. **Filter Data:** Menyaring `events.csv` berdasarkan rentang timestamp (epoch ms) periode Fold Training P1 dan Fold Testing P2 untuk saya (NIM: 23031554018).
2. **Pemilihan User Target:** Dipilih acak dengan `np.random.seed(732)` dari user yang aktif di P1 maupun P2 dengan minimal 15 interaksi di P1. Terpilih Visitor `1293068`.
3. **Pembentukan Subgraph:** Dibangun lingkungan dua langkah di sekitar user target (semua item yang pernah disentuh user target, lalu semua user lain yang menyentuh item yang sama, beserta seluruh interaksinya di P1). Hasilnya mencakup 374 user, 9.137 item, dan 25.886 interaksi.
4. **Impor ke Neo4j:** Dilakukan per batch 1.000 baris dengan unique constraint pada `visitorId` dan `itemId`.
5. **VSM & Proyeksi Graf:** Membentuk matriks User ($374 \times 9.137$) dan Item ($9.137 \times 374$) dengan sparsity 99,57%. Proyeksi User dipilih karena lebih hemat komputasi (~24 kali lebih cepat) dan langsung memodelkan ketetanggaan preferensi.
6. **Perhitungan Similarity:** Menghitung Cosine Similarity antar-user terhadap user target, lalu lima nilai tertinggi dituliskan kembali ke Neo4j sebagai relasi `[:SIMILAR {score: ...}]`.
7. **Rekomendasi KNN & Evaluasi:** Collaborative Filtering dengan $k = 5$ menghasilkan Top-3 item baru, dan dievaluasi terhadap aktivitas nyata user target di periode testing (P2).

## Ringkasan Hasil

**Komposisi Subgraph di Neo4j**

| Simpul | Jumlah | Relasi | Jumlah |
| :--- | ---: | :--- | ---: |
| Item | 9.137 | VIEWED | 23.349 |
| Visitor | 374 | ADDED_TO_CART | 1.482 |
| | | BOUGHT | 1.055 |
| **Total Node** | **9.511** | **Total Relasi Interaksi** | **25.886** |

**Lima Similarity Tertinggi terhadap Visitor 1293068**

| Peringkat | Visitor ID | Cosine Similarity |
| ---: | ---: | ---: |
| 1 | 42561 | 0,9107 |
| 2 | 1319005 | 0,9064 |
| 3 | 895969 | 0,8867 |
| 4 | 708420 | 0,8825 |
| 5 | 660351 | 0,8825 |

**Tiga Item Rekomendasi Teratas ($k = 5$)**

| Peringkat | Item ID | Skor Prediksi | Keterangan |
| ---: | ---: | ---: | :--- |
| 1 | 38965 | 3,5862 | Tidak diakses di P2 |
| 2 | 241555 | 3,5709 | **HIT!** Diakses user pada Fold Testing P2 |
| 3 | 265571 | 2,6602 | Tidak diakses di P2 |

**Hasil Evaluasi Periode Testing**
- **Hit@5 = 1** (Terdapat 2 item hit dari 5 rekomendasi: Item `241555` di peringkat 2 dan Item `239006` di peringkat 4).
- **Precision@5 = 0,4** (Proporsi 2 dari 5 item relevan).
- **DCG@5 = 1,0616**, **IDCG@5 = 2,9485**, **NDCG@5 = 0,3601**.

## Visualisasi

| Berkas Gambar | Keterangan |
| :--- | :--- |
| `plots/vsm_user_projection.png` | Proyeksi User: user target dan 5 tetangga terdekatnya beserta bobot similarity |
| `plots/vsm_item_projection.png` | Proyeksi Item: keterhubungan produk berdasarkan pola co-viewing pengguna |
| `plots/graph_before_similarity.png` | Kondisi graf SEBELUM similarity (bipartite interaksi Visitor -> Item) |
| `plots/graph_after_similarity.png` | Kondisi graf SESUDAH similarity (graf homogen terproyeksi dengan relasi `SIMILAR`) |
| `plots/knn_recommendations.png` | Diagram batang 5 item rekomendasi dan penandaan item yang hit di periode testing |

## Pengumpulan

Seluruh pengerjaan terekam di dalam notebook [UTS_GSD_23031554018_MOCH_AKBAR_HANAFI.ipynb](file:///Users/macairm12020/college/UTS%20GRAF/UTS_GSD_23031554018_MOCH_AKBAR_HANAFI.ipynb). Tautan repositori GitHub dikumpulkan melalui LMS SiDia.
