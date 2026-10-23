# Naskah Soal & Panduan Detail Ujian Tengah Semester (UTS) Graf Sains Data

## Identitas Mahasiswa & Pembagian Data Periode (Fold)

Berdasarkan berkas pembagian data kelas **GSD 2023E** (`UTS GSD 2023E.xlsx`), berikut adalah rincian identitas dan pembagian periode waktu interaksi (Fold Training & Fold Testing) untuk pengerjaan Soal UTS:

| Atribut | Detail Informasi |
| :--- | :--- |
| **No. Urut** | 3 |
| **NIM** | 23031554018 |
| **Nama Mahasiswa** | MOCH. AKBAR HANAFI |
| **Kelas** | GSD 2023E |
| **Fold Training (P1) — Awal** | `2015-05-03` (3 Mei 2015) |
| **Fold Training (P1) — Akhir** | `2015-07-22` (22 Juli 2015) |
| **Fold Testing (P2) — Awal** | `2015-07-23` (23 Juli 2015) |
| **Fold Testing (P2) — Akhir** | `2015-08-12` (12 Agustus 2015) |

> **Catatan Teknis Filter Timestamp (Dataset RetailRocket):**
> Kolom `timestamp` pada berkas `events.csv` RetailRocket menggunakan format **Unix Epoch dalam milidetik (milliseconds)**. Saat menerapkan filter pada Soal 2.1 nomor 1 dan 2:
> - **Fold Training (P1):** `2015-05-03 00:00:00 UTC` (`1430611200000` ms) s/d `2015-07-22 23:59:59 UTC` (`1437609599999` ms)
> - **Fold Testing (P2):** `2015-07-23 00:00:00 UTC` (`1437609600000` ms) s/d `2015-08-12 23:59:59 UTC` (`1439423999999` ms)

## Informasi Mata Kuliah & Naskah Soal

| Komponen | Keterangan |
| :--- | :--- |
| **Institusi** | Universitas Negeri Surabaya — Fakultas Matematika dan Ilmu Pengetahuan Alam |
| **Program Studi** | S1 Sains Data (Kampus 1 Unesa, Gedung E2 Ketintang, Surabaya 60231) |
| **Matakuliah** | Graf Sains Data |
| **SKS** | 3 |
| **Tanggal** | Minggu ke-8/9, Gasal 2026/2027 |
| **Dosen** | TIM |
| **Materi** | Python Driver untuk (Neo4J) dan Rekomendasi |
| **Sifat** | Individu |

### Petunjuk Umum

1. Ikuti langkah-langkah aktivitas individu sesuai dengan petunjuk.
2. Perhatikan poin-poin utama dalam tiap pertanyaan.

## 1. Tugas Pendahuluan

### 1.1 Persiapan dan Perkenalan Lingkungan

1. Buatlah sebuah environment baru menggunakan `venv` atau `uv` dan jalankan perintah seperti berikut:

   ```bash
   $ python -m venv myenv
   ```

   atau, untuk `uv` seperti:

   ```bash
   $ uv venv myvenv --python 3.10
   ```

   Pembuatan virtual environment ini sangat disarankan untuk proses isolasi *development environment* sehingga dapat meminimalisasi "disrupsi" paket-paket dependensi dari *local projects* di lingkungan kerja (laptop / PC) masing-masing.

2. Matikan paket virtual environment yang lain (jika ada):

   ```bash
   $ conda deactivate
   ```

   Aktifkan virtual environment baru `myvenv`:

   ```bash
   $ source myvenv/bin/activate
   ```

3. Install dependensi paket-paket seperti yang ada di dalam file `requirements.txt` seperti berikut:

   ```text
   neo4j>=4.0,<4.3
   imdbpy==2020.9.25
   nose==1.3.7
   cinemagoerng>=0.4
   imdbinfo>=0.5
   imdbpy>=2020.9.25
   neo4j==4.2.1
   ```

   dengan perintah kurang lebih sebagai berikut:

   ```bash
   uv pip install -r requirements.txt
   ```

### 1.2 Mempelajari Penggunaan Driver Neo4J

1. Ikuti tutorial penggunaan driver Neo4J untuk melakukan pembuatan objek dan akses objek berikut.
2. Baris berikut mendefinisikan string koneksi ke database Neo4J:

   ```python
   from neo4j import GraphDatabase, RoutingControl

   URI = "neo4j://localhost:7687"
   AUTH = ("neo4j", "password")
   ```

   Ganti informasi *credential* sesuai dengan kebutuhan.

3. Baris perintah berikut melakukan pembuatan sebuah Node berikut dengan *relationship*-nya:

   ```python
   def add_friend(driver, name, friend_name):
       driver.execute_query(
           "MERGE (a:Person {name: $name}) "
           "MERGE (friend:Person {name: $friend_name}) "
           "MERGE (a)-[:KNOWS]->(friend)",
           name=name, friend_name=friend_name, database_="neo4j",
       )
   ```

   Perhatikan perintah `execute_query`.

4. Untuk mencetak dan menjalankan keseluruhan:

   ```python
   def print_friends(driver, name):
       records, _, _ = driver.execute_query(
           "MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
           "RETURN friend.name ORDER BY friend.name",
           name=name, database_="neo4j", routing_=RoutingControl.READ,
       )
       for record in records:
           print(record["friend.name"])

   with GraphDatabase.driver(URI, auth=AUTH, ) as driver:
       add_friend(driver, "Arthur", "Guinevere")
       add_friend(driver, "Arthur", "Lancelot")
       add_friend(driver, "Arthur", "Merlin")
       print_friends(driver, "Arthur")
   ```

#### Pertanyaan Pendahuluan (*Checkpoint*)

1. Apa nama database yang digunakan pada tutorial ini?
2. Sebutkan akses lain (seperti sintaks DDL/DML CYPHER) yang dapat digunakan mengakses database lain dalam 1 instance!
3. Apa jenis graf pertemanan yang telah dibuat di sini?

#### CYPHER Total Reset

Jalankan perintah berikut untuk melakukan *truncate* pada konten database:

```cypher
MATCH (n) DETACH DELETE n;
```

> \*Hati-hati dalam menggunakan perintah ini pada *shared database*.

### 1.3 Melakukan Proses Impor Data dari RetailRocket ke Database Neo4J

**Sumber data:** Roman Zykov

1. Unduh data dari Kaggle dengan perintah berikut:

   - **(a) Windows PowerShell:**

     ```powershell
     curl.exe -L -o ecommerce-dataset.zip `
       https://www.kaggle.com/api/v1/datasets/download/retailrocket/ecommerce-dataset
     ```

   - **(b) Unix-based (Linux / MacOS):**

     ```bash
     curl -L -o ecommerce-dataset.zip \
       https://www.kaggle.com/api/v1/datasets/download/retailrocket/ecommerce-dataset
     ```

2. Perhatikan fitur yang telah diunduh dengan rincian sebagai berikut:
   - **(a) timestamp:** Waktu dalam format unix epoch.
   - **(b) visitorid:** ID unik pengunjung.
   - **(c) event:** Jenis interaksi *default*: *view*, *addtocart*, *transaction*.
   - **(d) itemid:** ID unik produk.
   - **(e) transactionid:** ID transaksi, hanya terisi saat event berjenis '*transaction*'.

3. Buatlah mekanisme pembuatan session Neo4J baru dengan perintah kurang lebih seperti berikut (sumber: Neo4J Driver 6.4):

   ```python
   from neo4j import GraphDatabase

   driver = GraphDatabase.driver(uri, auth=(user, password))
   session = driver.session(database="system")
   ```

   atau, modifikasi dengan `argparse`, contohnya:

   ```python
   def parse_arguments():
       parser = argparse.ArgumentParser(
           description="Impor dataset RetailRocket (events.csv) ke database Neo4J."
       )
       parser.add_argument(
           "-u", "--user", default="neo4j", help="Username Neo4j (default: neo4j)"
       )
       parser.add_argument(
           "-p",
           "--password",
           default="neo4j",
           help="Password Neo4j (default: neo4j)",
       )
       parser.add_argument(
           "-b",
           "--bolt",
           default="neo4j://127.0.0.1:7687",
           help="Neo4J URI / Bolt (default: neo4j://127.0.0.1:7687)",
       )
       parser.add_argument(
           "-s",
           "--source",
           default="data",
           help="Direktori/folder sumber data (default: data)",
       )
       return parser.parse_args()
   ```

   Diawali oleh pemeriksaan keberadaan berkas `events.csv`:

   ```python
   csv_file_path = os.path.join(args.source, "events.csv")

   if not os.path.exists(csv_file_path):
       print(f"Error: File '{csv_file_path}' tidak ditemukan!")
       sys.exit(1)
   ```

   Dilanjutkan dengan pembuatan koneksi:

   ```python
   try:
       driver = GraphDatabase.driver(
           args.bolt, auth=(args.user, args.password)
       )
       driver.verify_connectivity()
   except Exception as e:
       print(f"Gagal terhubung ke database: {e}")
       sys.exit(1)
   ```

   Sesuaikan dengan kebutuhan Anda.

4. Anda lanjutkan dengan proses impor dengan mekanisme *batch*, kurang lebih sebagai berikut:

   ```python
   batch_size = 

   with driver.session() as session:
       create_constraints(session)

       print(f"Membaca file data dari: {csv_file_path}")
       chunks = pd.read_csv(csv_file_path, chunksize=batch_size)

       total_rows = 
       total_chunks = (total_rows // batch_size) + 1

       print("Memulai proses impor data ke Neo4j...")
       for chunk in tqdm(
           chunks, total=total_chunks, desc="Mengimpor Batch Data"
       ):
           # Membersihkan data null/NaN pada transactionid
           chunk["transactionid"] = (
               chunk["transactionid"].fillna("").astype(str)
           )

           records = chunk.to_dict(orient="records")
           session.execute_write(import_batch, records)

   driver.close()
   print("Proses impor berhasil.")
   ```

5. Selanjutnya, Anda membutuhkan baris perintah untuk mengimpor data dalam CYPHER, contohnya:

   ```python
   def import_batch(tx, batch):
       cypher_query = """
       UNWIND $batch AS row
       MERGE (v:Visitor {visitorId: row.visitorid})
       MERGE (i:Item {itemId: row.itemid})

       WITH v, i, row
       CALL {
           WITH v, i, row
           WITH v, i, row WHERE row.event = 'view'
           CREATE (v)-[:VIEWED {timestamp: row.timestamp}]->(i)

           UNION ALL

           WITH v, i, row
           WITH v, i, row WHERE row.event = 'addtocart'
           CREATE (v)-[:ADDED_TO_CART {timestamp: row.timestamp}]->(i)

           UNION ALL

           WITH v, i, row
           WITH v, i, row WHERE row.event = 'transaction'
           CREATE (v)-[:BOUGHT {timestamp: row.timestamp, transactionId: row.transactionid}]->(i)
       }
       """
       tx.run(cypher_query, batch=batch)
   ```

## 2. Soal UTS

### Petunjuk Khusus

1. **Deadline:** Sesuai LMS SiDia.
2. Modifikasi kode sumber sesuai dengan kebutuhan Anda.
3. Unggah pekerjaan Anda (dokumentasi notebook `.ipynb` dan penjelasan, serta dataset) pada akun Github Anda, dan tuliskan URL github Anda pada LMS SiDia.
4. Sesi kelas pada jadwal masing-masing akan ada pertanyaan secara acak.

### 2.1 Wrangling dan EDA (Maks. skor: 45)

1. Tentukan 2 periode waktu sebagai filter dari data interaksi. Kombinasi periode yang dipilih tiap mahasiswa **tidak boleh sama! (akan ditentukan)**
   - *Contoh di soal:* Fold training (P1) $\rightarrow$ `01/2023 - 03/2023`; Fold testing (P2) `01/2024 - 06/2024`.
   - **Ketentuan Khusus Anda (MOCH. AKBAR HANAFI - 23031554018):**
     - **Fold training (P1):** `2015-05-03` sampai dengan `2015-07-22`
     - **Fold testing (P2):** `2015-07-23` sampai dengan `2015-08-12`
2. Terapkan proses filter ini pada `timestamp` pada proses persiapan data, lalu simpan pada sebuah file `.csv`!
3. Lakukan query untuk mendapatkan komposisi dari *subgraph* yang dibuat. Uraikan jenis simpul dan jumlah masing-masing simpul dengan Python API! Jelaskan CYPHER SQL yang digunakan!
4. Lakukan Vector Space Modelling (VSM) terhadap simpul yang diasumsikan sebagai **User**. Uraikan bagaimana karakteristiknya (dimensi, shape, plot networkx, dst.)!
5. Lakukan VSM terhadap simpul yang diasumsikan sebagai **Item**. Uraikan bagaimana karakteristiknya (dimensi, shape, plot networkx, dst.)!
6. Berdasarkan eksplorasi no. 4 dan 5, uraikan proyeksi manakah yang lebih baik (efektif/efisien)!
7. Berdasarkan analisis no. 6, lakukan perhitungan *similarity* pada hasil graf yang terproyeksi dengan menggunakan Python:
   - **(a)** Tuliskan CYPHER SQL untuk mendapatkan 5 records dengan *similarity* tertinggi (Anda tentukan sendiri record acuannya)!
   - **(b)** Tuliskan kembali nilai *similarity-similarity* tersebut pada graf yang telah ada! Perlihatkan hasil query-nya!
8. Tuliskan CYPHER SQL dan tunjukkan hasil graf-nya untuk memperlihatkan kondisi: sebelum dan sesudah perhitungan *similarity*!

### 2.2 Analytics (Maks. skor: 55)

1. Pilih seorang *user* secara acak (tentukan proses acak-nya, dan harus bisa di-reproduksi), lalu:
   - **(a)** tuliskan skrip Python dalam merekomendasikan KNN-nya!
   - **(b)** berikan 3 item yang diiklankan untuk $k = 5$ pada penentuan KNN-nya!
2. Berdasarkan hasil rekomendasi Anda no. 1b Analytics, hitunglah:
   - **(a)** Hit@5
   - **(b)** NDCG@5

## Daftar Periksa (Checklist) Pengerjaan UTS untuk MOCH. AKBAR HANAFI

| No | Tahapan Tugas | Target / Parameter Spesifik Anda | Status |
| :--- | :--- | :--- | :--- |
| 1 | **Setup Environment & Neo4J** | Virtual environment (`myenv`/`myvenv`), install `requirements.txt`, pastikan koneksi Bolt Neo4J aktif | [ ] |
| 2 | **Checkpoint Tugas Pendahuluan** | Jawab 3 pertanyaan *checkpoint* (nama database `neo4j`, sintaks akses multi-database, jenis graf berarah `Person-[:KNOWS]->Person`) | [ ] |
| 3 | **Filter Data Interaksi (`events.csv`)** | Filter **Fold Training (P1):** `2015-05-03` s/d `2015-07-22` dan **Fold Testing (P2):** `2015-07-23` s/d `2015-08-12`, simpan ke `.csv` | [ ] |
| 4 | **Impor Subgraph ke Neo4J** | Impor data hasil filter ke Neo4J (`Visitor`, `Item`, relasi `VIEWED`, `ADDED_TO_CART`, `BOUGHT`) | [ ] |
| 5 | **Komposisi Subgraph (No. 2.1.3)** | Query jenis simpul & jumlah masing-masing simpul via Python API + penjelasan Cypher | [ ] |
| 6 | **VSM Simpul User (No. 2.1.4)** | Representasi VSM User, uraikan dimensi, shape, dan visualisasi plot `networkx` | [ ] |
| 7 | **VSM Simpul Item (No. 2.1.5)** | Representasi VSM Item, uraikan dimensi, shape, dan visualisasi plot `networkx` | [ ] |
| 8 | **Evaluasi Proyeksi (No. 2.1.6)** | Bandingkan efektivitas & efisiensi proyeksi User vs Item | [ ] |
| 9 | **Perhitungan Similarity & Update Graf (No. 2.1.7 & 2.1.8)** | Hitung similarity via Python, tampilkan 5 similarity tertinggi dari 1 record acuan via Cypher, simpan balik ke graf, dan tampilkan kondisi graf sebelum & sesudah | [ ] |
| 10 | **Rekomendasi KNN & Evaluasi (No. 2.2.1 & 2.2.2)** | Pilih 1 user acak (dengan `random.seed` / `np.random.seed`), rekomendasikan 3 item dengan $k=5$, lalu hitung **Hit@5** dan **NDCG@5** terhadap Fold Testing | [ ] |
| 11 | **Unggah ke GitHub & Submit LMS SiDia** | Unggah notebook `.ipynb`, penjelasan, serta dataset ke repositori GitHub dan kumpulkan link di LMS SiDia | [ ] |
