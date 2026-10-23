# UTS Graf Sains Data

Analisis graf bipartite, Vector Space Modelling, dan sistem rekomendasi collaborative filtering KNN pada dataset e-commerce RetailRocket memakai Neo4j dan Python.

## Identitas

| | |
| :--- | :--- |
| Nama | MOCH. AKBAR HANAFI |
| NIM | 23031554018 |
| No. urut presensi | 3 |
| Kelas | GSD 2023E |
| Program Studi | S1 Sains Data, FMIPA Universitas Negeri Surabaya |
| Mata Kuliah | Graf Sains Data (3 SKS) |
| Fold Training (P1) | 2015-05-03 00:00:00 UTC s/d 2015-07-22 23:59:59 UTC (epoch ms 1430611200000 – 1437609599999) |
| Fold Testing (P2) | 2015-07-23 00:00:00 UTC s/d 2015-08-12 23:59:59 UTC (epoch ms 1437609600000 – 1439423999999) |

## Isi repositori

```text
UTS GRAF/
├── UTS_GSD_23031554018_MOCH_AKBAR_HANAFI.ipynb  # notebook utama, berisi seluruh pengerjaan dan outputnya
├── import_neo4j.py                              # skrip impor batch ke Neo4j (pakai argparse)
├── vsm_similarity_analytics.py                  # pipeline VSM, similarity, KNN, dan visualisasi
├── build_notebook.py                            # generator notebook versi awal (sudah tidak sinkron)
├── requirements.txt
├── data/
│   ├── events.csv                               # data mentah RetailRocket (2.756.101 baris)
│   ├── events_p1_train.csv                      # hasil filter periode P1 (1.681.206 baris)
│   ├── events_p2_test.csv                       # hasil filter periode P2 (433.774 baris)
│   └── events_subgraph.csv                      # subgraph di sekitar user target (25.886 baris)
└── plots/                                       # lima gambar hasil visualisasi
```

## Cara menjalankan

1. Siapkan virtual environment dan dependensinya.

   ```bash
   uv venv myvenv --python 3.12
   source myvenv/bin/activate
   uv pip install -r requirements.txt
   ```

2. Pastikan Neo4j sudah jalan sebelum notebook dieksekusi.

   ```bash
   docker start neo4j
   # kalau containernya belum ada:
   # docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password123 neo4j:latest
   ```

3. Jalankan notebook dari atas sampai bawah.

   ```bash
   jupyter notebook UTS_GSD_23031554018_MOCH_AKBAR_HANAFI.ipynb
   ```

   Notebook sudah berdiri sendiri: penyaringan data, pemilihan user target, pembentukan subgraph, impor ke Neo4j, sampai evaluasi semuanya dikerjakan di dalam notebook. Dua skrip `.py` di luar notebook dipakai kalau ingin menjalankan tahapannya terpisah:

   ```bash
   python import_neo4j.py --reset --source data/events_subgraph.csv
   python vsm_similarity_analytics.py
   ```

## Alur pengerjaan

1. **Penyaringan data.** `events.csv` disaring berdasarkan kolom `timestamp` (Unix epoch milidetik) sesuai dua periode yang ditentukan, lalu disimpan ke file CSV terpisah.
2. **Pemilihan user target.** Dipilih acak dengan `np.random.seed(732)` dari daftar kandidat terurut berisi user yang aktif di P1 maupun P2 dengan minimal 15 interaksi di P1. Hasilnya Visitor `1293068`. Seed-nya ditetapkan supaya hasilnya sama setiap kali dijalankan ulang.
3. **Pembentukan subgraph.** Diambil lingkungan dua langkah di sekitar user target: semua item yang pernah ia sentuh, semua user lain yang menyentuh item yang sama, lalu seluruh interaksi user-user tersebut di P1. Hasilnya 374 user, 9.137 item, dan 25.886 baris interaksi.
4. **Impor ke Neo4j.** Subgraph diimpor per batch 1.000 baris dengan unique constraint pada `visitorId` dan `itemId`. Node dibuat dengan `MERGE` supaya tidak dobel, relasi dibuat dengan `CREATE` supaya setiap interaksi tetap tercatat terpisah beserta `timestamp`-nya.
5. **VSM dan proyeksi.** Matriks User berukuran 374 x 9.137 dan matriks Item adalah transpose-nya. Keduanya punya 14.568 elemen non-nol dan sparsity 99,57%.
6. **Similarity.** Cosine similarity dihitung dari vektor user target terhadap seluruh user, lalu lima nilai tertinggi ditulis balik ke graf sebagai relasi `[:SIMILAR {score: ...}]`.
7. **Rekomendasi dan evaluasi.** KNN dengan k = 5, hasilnya diuji terhadap interaksi nyata user target di periode testing.

## Ringkasan hasil

**Komposisi subgraph di Neo4j**

| Simpul | Jumlah | Relasi | Jumlah |
| :--- | ---: | :--- | ---: |
| Item | 9.137 | VIEWED | 23.349 |
| Visitor | 374 | ADDED_TO_CART | 1.482 |
| | | BOUGHT | 1.055 |
| **Total** | **9.511** | **Total** | **25.886** |

**Lima similarity tertinggi terhadap Visitor 1293068**

| Peringkat | Visitor | Cosine similarity |
| ---: | ---: | ---: |
| 1 | 42561 | 0,9107 |
| 2 | 1319005 | 0,9064 |
| 3 | 895969 | 0,8867 |
| 4 | 708420 | 0,8825 |
| 5 | 660351 | 0,8825 |

**Tiga item yang direkomendasikan (k = 5)**

| Peringkat | Item ID | Skor prediksi | Keterangan |
| ---: | ---: | ---: | :--- |
| 1 | 38965 | 3,5862 | tidak diakses di P2 |
| 2 | 241555 | 3,5709 | kena, diakses user di P2 |
| 3 | 265571 | 2,6602 | tidak diakses di P2 |

**Evaluasi terhadap periode testing**

- Hit@5 = 1 (dua item kena dari lima rekomendasi, yaitu Item 241555 di peringkat 2 dan Item 239006 di peringkat 4)
- DCG@5 = 1,0616; IDCG@5 = 2,9485; NDCG@5 = 0,3601

## Visualisasi

| Gambar | Isi |
| :--- | :--- |
| `plots/vsm_user_projection.png` | Proyeksi sisi User: user target dan lima tetangga terdekatnya beserta bobot similarity |
| `plots/vsm_item_projection.png` | Proyeksi sisi Item: keterhubungan antar-produk berdasarkan pola co-viewing |
| `plots/graph_before_similarity.png` | Kondisi graf sebelum similarity dihitung, masih bipartite murni |
| `plots/graph_after_similarity.png` | Kondisi graf sesudahnya, sudah ada relasi langsung antar-Visitor |
| `plots/knn_recommendations.png` | Peringkat lima rekomendasi beserta penandaan item yang kena di periode testing |

## Pengumpulan

Repositori ini berisi kode, notebook beserta outputnya, visualisasi, dan dataset hasil penyaringan. Tautan repositori dikumpulkan lewat LMS SiDia.
