# CATATAN: skrip generator ini sudah tidak sinkron dengan notebook.
# Notebook UTS_GSD_23031554018_MOCH_AKBAR_HANAFI.ipynb sudah diedit langsung
# (penambahan sel pemilihan user acak, pembentukan subgraph, dan impor Neo4j).
# Jangan jalankan ulang skrip ini kecuali ingin membangun notebook dari nol.

#!/usr/bin/env python3
"""
build_notebook.py
Script untuk membangun dan mengeksekusi Jupyter Notebook lengkap
UTS Graf Sains Data - Moch. Akbar Hanafi (23031554018)
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "codemirror_mode": {"name": "ipython", "version": 3},
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.12.15"
    }
}

cells = []

def add_md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip()))

def add_code(text):
    cells.append(nbf.v4.new_code_cell(text.strip()))

# --- Header & Identitas ---
add_md("""
# LAPORAN TUGAS UJIAN TENGAH SEMESTER (UTS) GRAF SAINS DATA
## Analisis Graf Bipartite, Vector Space Modelling (VSM), dan Sistem Rekomendasi Collaborative Filtering KNN pada Dataset E-Commerce RetailRocket Menggunakan Neo4J dan Python

---

### **Identitas Mahasiswa & Pembagian Data Periode (Fold)**

| Atribut | Informasi Mahasiswa |
| :--- | :--- |
| **Nama Lengkap** | **MOCH. AKBAR HANAFI** |
| **Nomor Induk Mahasiswa (NIM)** | **23031554018** |
| **Nomor Urut Presensi** | **3** |
| **Kelas** | **GSD 2023E** |
| **Program Studi** | S1 Sains Data |
| **Fakultas / Universitas** | Fakultas Matematika dan Ilmu Pengetahuan Alam — Universitas Negeri Surabaya |
| **Mata Kuliah** | Graf Sains Data (3 SKS) — Gasal 2026/2027 |
| **Fold Training (P1)** | `2015-05-03 00:00:00 UTC` s/d `2015-07-22 23:59:59 UTC` (`1430611200000` ms s/d `1437609599999` ms) |
| **Fold Testing (P2)** | `2015-07-23 00:00:00 UTC` s/d `2015-08-12 23:59:59 UTC` (`1437609600000` ms s/d `1439423999999` ms) |
""")

# --- Acceptance Criteria ---
add_md("""
---
## **Kriteria Keberterimaan (Acceptance Criteria)**

Laporan dan implementasi ini mengacu pada kriteria keberterimaan (Acceptance Criteria) berikut:

1. **AC 1: Lingkungan (Environment) & Setup Neo4j**
   - Virtual environment Python terisolasi (`myvenv`) aktif dan seluruh dependensi (`requirements.txt`) terpasang.
   - Neo4j Database Server berjalan aktif pada instance lokal / container Docker dan terhubung melalui Python Driver Neo4j (`bolt://localhost:7687`).
2. **AC 2: Checkpoint Tugas Pendahuluan**
   - Menjawab 3 pertanyaan konsep: (1) Nama database (`neo4j`), (2) Sintaks Cypher/API multi-database (`USE <db>`, `session(database=...)`), (3) Jenis graf pertemanan (directed graph / graf berarah).
   - Pengujian fungsi CRUD dasar graf (`add_friend`, `print_friends`) dan Cypher Total Reset (`MATCH (n) DETACH DELETE n;`).
   - Mekanisme batch import data dengan relasi bertipe interaksi (`VIEWED`, `ADDED_TO_CART`, `BOUGHT`).
3. **AC 3: Wrangling & Filter Timestamp Sesuai Identitas Mahasiswa**
   - Kolom `timestamp` pada `events.csv` disaring berdasarkan Epoch millisecond sesuai jadwal resmi:
     - Fold Training (P1): `1430611200000` s/d `1437609599999`
     - Fold Testing (P2): `1437609600000` s/d `1439423999999`
   - Data hasil penyaringan disimpan ke dalam berkas CSV mandiri (`events_p1_train.csv`, `events_p2_test.csv`, `events_subgraph.csv`).
4. **AC 4: Impor & Analisis Komposisi Subgraph (Soal 2.1.3)**
   - Subgraph interaksi berhasil diimpor ke Neo4j dengan constraints unik pada `visitorId` dan `itemId`.
   - Menghitung komposisi simpul (`Visitor`, `Item`) dan relasi (`VIEWED`, `ADDED_TO_CART`, `BOUGHT`) menggunakan Python API dan query Cypher beserta penjelasannya.
5. **AC 5: Vector Space Modelling (VSM) User & Item (Soal 2.1.4 & 2.1.5)**
   - VSM User: Representasi User dalam ruang dimensi Item, menjabarkan bentuk matriks, shape, dimensi, sparsity, dan visualisasi graf proyeksi NetworkX.
   - VSM Item: Representasi Item dalam ruang dimensi User, menjabarkan bentuk matriks, shape, dimensi, sparsity, dan visualisasi graf proyeksi NetworkX.
6. **AC 6: Evaluasi Komparatif Proyeksi User vs Item (Soal 2.1.6)**
   - Analisis mendalam efektivitas vs efisiensi komputasi antara kedua proyeksi ($\mathcal{O}(|U|^2 \cdot |I|)$ vs $\mathcal{O}(|I|^2 \cdot |U|)$) dan relevansinya terhadap Collaborative Filtering.
7. **AC 7: Perhitungan Similarity & Update Graf (Soal 2.1.7 & 2.1.8)**
   - Perhitungan Cosine Similarity pada graf terproyeksi menggunakan Python.
   - Mengambil 5 tetangga dengan similarity tertinggi untuk satu simpul acuan.
   - Menyimpan kembali relasi `[:SIMILAR {score: ...}]` ke Neo4j dan memverifikasi dengan Cypher.
   - Menampilkan kondisi graf SEBELUM vs SESUDAH perhitungan similarity (Cypher dan visualisasi graf NetworkX).
8. **AC 8: Rekomendasi Collaborative Filtering KNN & Evaluasi Offline (Soal 2.2.1 & 2.2.2)**
   - Pemilihan user target secara acak yang dapat direproduksi (`np.random.seed(732)`).
   - Algoritma KNN ($k=5$) merekomendasikan Top-3 item preferensi tertinggi yang belum pernah diakses target user.
   - Evaluasi akurasi offline terhadap interaksi faktual user pada **Fold Testing (P2)** dengan metrik **Hit@5** dan **NDCG@5**.
""")

# --- 1. Tugas Pendahuluan ---
add_md("""
---
## **1. Tugas Pendahuluan**

### **1.1 Persiapan dan Perkenalan Lingkungan**
Virtual environment dibuat menggunakan `uv` atau `python -m venv` untuk memastikan isolasi dependensi. Seluruh library yang dibutuhkan dicatat dalam `requirements.txt`.
""")

add_code(r"""
# Memeriksa versi library yang terpasang dalam virtual environment
import sys
import neo4j
import pandas as pd
import numpy as np
import sklearn
import networkx as nx
import matplotlib

print(f"Python Interpreter : {sys.executable}")
print(f"Python Version     : {sys.version.split()[0]}")
print(f"Neo4j Driver       : {neo4j.__version__}")
print(f"Pandas Version     : {pd.__version__}")
print(f"NumPy Version      : {np.__version__}")
print(f"Scikit-Learn       : {sklearn.__version__}")
print(f"NetworkX Version   : {nx.__version__}")
print(f"Matplotlib Version : {matplotlib.__version__}")
""")

add_md("""
### **1.2 Mempelajari Penggunaan Driver Neo4J**

Berikut adalah implementasi fungsi koneksi driver Neo4j, pembuatan node `Person` beserta relasi `KNOWS`, dan pembacaan kembali menggunakan `RoutingControl.READ`.
""")

add_code(r"""
from neo4j import GraphDatabase, RoutingControl

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password123")

def add_friend(driver, name, friend_name):
    query = (
        "MERGE (a:Person {name: $name}) "
        "MERGE (friend:Person {name: $friend_name}) "
        "MERGE (a)-[:KNOWS]->(friend)"
    )
    driver.execute_query(
        query,
        name=name,
        friend_name=friend_name,
        database_="neo4j",
    )

def print_friends(driver, name):
    query = (
        "MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
        "RETURN friend.name ORDER BY friend.name"
    )
    records, _, _ = driver.execute_query(
        query,
        name=name,
        database_="neo4j",
        routing_=RoutingControl.READ,
    )
    friends = [record["friend.name"] for record in records]
    return friends

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    # Tambahkan relasi pertemanan Arthur
    add_friend(driver, "Arthur", "Guinevere")
    add_friend(driver, "Arthur", "Lancelot")
    add_friend(driver, "Arthur", "Merlin")
    
    friends_of_arthur = print_friends(driver, "Arthur")
    print("Daftar teman dari Arthur yang tercatat di Neo4j:")
    for f in friends_of_arthur:
        print(f" - {f}")
""")

add_md("""
#### **Jawaban Pertanyaan Pendahuluan (Checkpoint)**

1. **Apa nama database yang digunakan pada tutorial ini?**
   - **Jawaban:** Database yang digunakan adalah **`neo4j`**, yang merupakan *default database* pada instalasi Neo4J Enterprise / Community Edition (dinyatakan secara eksplisit dalam argumen `database_="neo4j"` pada pemanggilan `execute_query`).

2. **Sebutkan akses lain (seperti sintaks DDL/DML CYPHER) yang dapat digunakan mengakses database lain dalam 1 instance!**
   - **Jawaban:**
     - **Klausul Cypher `USE <database_name>`:** Digunakan di awal kueri untuk mengarahkan eksekusi kueri ke database tertentu, contoh:
       ```cypher
       USE retaildb MATCH (v:Visitor) RETURN count(v);
       ```
     - **Manajemen Database Administratif via Database `system`:**
       ```cypher
       SHOW DATABASES;
       CREATE DATABASE salesdb;
       STOP DATABASE salesdb;
       ```
     - **Konfigurasi Python Driver Session:** Mengarahkan session atau transaksi ke database target secara dinamis via parameter:
       ```python
       with driver.session(database="salesdb") as session:
           session.run("MATCH (n) RETURN n LIMIT 10")
       ```

3. **Apa jenis graf pertemanan yang telah dibuat di sini?**
   - **Jawaban:** Graf yang dibuat adalah **Directed Graph (Graf Berarah)**, karena relasi didefinisikan secara asimetris dengan tanda panah spesifik: `(a:Person)-[:KNOWS]->(friend:Person)`. Artinya, `Arthur KNOWS Guinevere` tidak secara otomatis membuat `Guinevere KNOWS Arthur` kecuali relasi balasan dibuat secara eksplisit.
""")

add_md("""
#### **CYPHER Total Reset**
Melakukan pembersihan seluruh simpul dan relasi percobaan dari database sebelum mengimpor data utama.
""")

add_code(r"""
# Melakukan reset total database Neo4j
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.execute_query("MATCH (n) DETACH DELETE n;", database_="neo4j")
    records, _, _ = driver.execute_query("MATCH (n) RETURN count(n) AS total", database_="neo4j")
    print(f"Total node setelah reset: {records[0]['total']}")
""")

# --- 2. Soal UTS ---
add_md("""
---
## **2. Soal UTS**

### **2.1 Wrangling dan EDA**

#### **2.1.1 & 2.1.2 Penentuan Periode Filter Timestamp dan Penyimpanan CSV**
Sesuai rincian identitas mahasiswa **MOCH. AKBAR HANAFI (NIM: 23031554018)**:
- **Fold Training (P1):** `2015-05-03 00:00:00 UTC` s/d `2015-07-22 23:59:59 UTC` (Epoch ms: `1430611200000` s/d `1437609599999`)
- **Fold Testing (P2):** `2015-07-23 00:00:00 UTC` s/d `2015-08-12 23:59:59 UTC` (Epoch ms: `1437609600000` s/d `1439423999999`)
""")

add_code(r"""
# Membaca dataset RetailRocket dan memfilter data berdasarkan Fold Mahasiswa
p1_start, p1_end = 1430611200000, 1437609599999
p2_start, p2_end = 1437609600000, 1439423999999

df_raw = pd.read_csv("data/events.csv")
print(f"Total baris data mentah events.csv: {len(df_raw):,}")

# Filter Fold Training (P1)
df_p1 = df_raw[(df_raw["timestamp"] >= p1_start) & (df_raw["timestamp"] <= p1_end)].copy()
# Filter Fold Testing (P2)
df_p2 = df_raw[(df_raw["timestamp"] >= p2_start) & (df_raw["timestamp"] <= p2_end)].copy()

print(f"Fold Training (P1) : {len(df_p1):,} baris | {df_p1['visitorid'].nunique():,} unique visitors | {df_p1['itemid'].nunique():,} unique items")
print(f"Fold Testing (P2)  : {len(df_p2):,} baris | {df_p2['visitorid'].nunique():,} unique visitors | {df_p2['itemid'].nunique():,} unique items")

# Irisan pengunjung pada kedua fold
common_visitors = set(df_p1["visitorid"]).intersection(set(df_p2["visitorid"]))
print(f"Pengunjung yang aktif pada P1 dan P2 : {len(common_visitors):,} visitors")
""")

add_md("""
Berkas hasil filter disimpan ke dalam direktori `data/` sebagai berkas CSV mandiri:
- `data/events_p1_train.csv` : Data lengkap Fold Training P1 (1.681.206 baris)
- `data/events_p2_test.csv` : Data lengkap Fold Testing P2 (433.774 baris)
- `data/events_subgraph.csv` : Data komunitas subgraph aktif yang diimpor ke Neo4j (25.886 baris)
""")

add_code(r"""
# Memeriksa keberadaan file CSV yang tersimpan
import os
for fname in ["events_p1_train.csv", "events_p2_test.csv", "events_subgraph.csv"]:
    fpath = os.path.join("data", fname)
    fsize = os.path.getsize(fpath) / (1024 * 1024)
    print(f"File: {fpath:<25} | Ukuran: {fsize:.2f} MB")
""")

add_md("""
#### **2.1.3 Komposisi Subgraph pada Neo4J dan Penjelasan Kueri Cypher**

Data komunitas interaksi diimpor ke database Neo4j dengan skrip batch import (`import_neo4j.py`). Berikut adalah query Python API untuk mengambil komposisi jenis simpul dan jenis relasi:
""")

add_code(r"""
# Query komposisi simpul dan relasi dari database Neo4j
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    # 1. Komposisi Node
    node_query = '''
    MATCH (n)
    RETURN labels(n)[0] AS nodeType, count(n) AS nodeCount
    ORDER BY nodeCount DESC
    '''
    node_records, _, _ = driver.execute_query(node_query, database_="neo4j")
    
    # 2. Komposisi Relasi
    rel_query = '''
    MATCH ()-[r]->()
    RETURN type(r) AS relType, count(r) AS relCount
    ORDER BY relCount DESC
    '''
    rel_records, _, _ = driver.execute_query(rel_query, database_="neo4j")

print("=== Komposisi Simpul (Nodes) Subgraph Neo4J ===")
for r in node_records:
    print(f" - Simpul [{r['nodeType']:<10}]: {r['nodeCount']:,} node")

print("\n=== Komposisi Hubungan (Relationships) Subgraph Neo4J ===")
for r in rel_records:
    print(f" - Relasi [:{r['relType']:<15}]: {r['relCount']:,} relasi")
""")

add_md("""
**Penjelasan Kueri CYPHER yang Digunakan:**
1. **Query Komposisi Simpul:**
   ```cypher
   MATCH (n)
   RETURN labels(n)[0] AS nodeType, count(n) AS nodeCount
   ORDER BY nodeCount DESC;
   ```
   *Penjelasan:* Pola `MATCH (n)` mencocokkan setiap simpul dalam graf. Fungsi `labels(n)[0]` mengekstrak label utama simpul (`Visitor` atau `Item`). Fungsi agregasi `count(n)` menghitung total instance per label, dan diurutkan secara menurun (`ORDER BY DESC`).

2. **Query Komposisi Relasi:**
   ```cypher
   MATCH ()-[r]->()
   RETURN type(r) AS relType, count(r) AS relCount
   ORDER BY relCount DESC;
   ```
   *Penjelasan:* Pola `()-[r]->()` mencocokkan seluruh relasi terarah tanpa membatasi label simpul asal maupun tujuan. Fungsi `type(r)` mengambil nama tipe relasi (`VIEWED`, `ADDED_TO_CART`, `BOUGHT`, atau `SIMILAR`), lalu `count(r)` menghitung total kemunculan setiap tipe relasi.
""")

# --- 2.1.4 VSM User ---
add_md("""
#### **2.1.4 Vector Space Modelling (VSM) Simpul User**

Pada representasi VSM Simpul User, setiap **User** dimodelkan sebagai vektor dalam ruang berdimensi item-item yang tersedia.
- **Baris:** User ($v_i \in U$)
- **Kolom:** Item ($item_j \in I$)
- **Nilai Elemen ($M_{u, i}$):** Bobot interaksi e-commerce ($w \in \{1: \text{view}, 2: \text{addtocart}, 3: \text{transaction}\}$).
""")

add_code(r"""
# Membangun Matriks VSM User-Item
from scipy.sparse import csr_matrix
sub_df = pd.read_csv("data/events_subgraph.csv")

users = sorted(sub_df["visitorid"].unique())
items = sorted(sub_df["itemid"].unique())

n_users = len(users)
n_items = len(items)

user_map = {u: i for i, u in enumerate(users)}
item_map = {it: i for i, it in enumerate(items)}

row_ind = [user_map[u] for u in sub_df["visitorid"]]
col_ind = [item_map[it] for it in sub_df["itemid"]]
weights = sub_df["event"].map({"view": 1.0, "addtocart": 2.0, "transaction": 3.0}).values

mat_user = csr_matrix((weights, (row_ind, col_ind)), shape=(n_users, n_items))

total_elements = n_users * n_items
nnz = mat_user.nnz
sparsity_user = (1.0 - (nnz / total_elements)) * 100

print("=== Karakteristik VSM Simpul User ===")
print(f"Dimensi Matriks (Shape) : ({n_users:,} User, {n_items:,} Item)")
print(f"Jumlah Fitur Dimensi    : {n_items:,} dimensi Item")
print(f"Total Sel Matriks       : {total_elements:,}")
print(f"Elemen Non-Zero (nnz)   : {nnz:,}")
print(f"Sparsity (Tingkat Kerapian): {sparsity_user:.2f}%")
print(f"Rata-rata interaksi per User: {nnz / n_users:.1f} item")
""")

add_md("""
**Visualisasi Plot NetworkX Proyeksi VSM Simpul User:**
Menampilkan graf proyeksi simpul User di mana edge merepresentasikan keterkaitan kemiripan preferensi (Cosine Similarity) antar-pengunjung.
""")

add_code(r"""
# Menampilkan visualisasi plot NetworkX VSM User Projection
from IPython.display import Image, display
display(Image(filename="plots/vsm_user_projection.png", width=650))
""")

# --- 2.1.5 VSM Item ---
add_md("""
#### **2.1.5 Vector Space Modelling (VSM) Simpul Item**

Pada representasi VSM Simpul Item, setiap **Item** dimodelkan sebagai vektor dalam ruang berdimensi pengguna (User) yang berinteraksi dengannya.
- **Baris:** Item ($item_j \in I$)
- **Kolom:** User ($v_i \in U$)
- **Nilai Elemen ($M_{i, u}$):** Bobot interaksi ($M_{Item} = M_{User}^T$).
""")

add_code(r"""
# Membangun Matriks VSM Item-User (Transpose dari VSM User)
mat_item = mat_user.T.tocsr()

print("=== Karakteristik VSM Simpul Item ===")
print(f"Dimensi Matriks (Shape) : ({n_items:,} Item, {n_users:,} User)")
print(f"Jumlah Fitur Dimensi    : {n_users:,} dimensi User")
print(f"Total Sel Matriks       : {total_elements:,}")
print(f"Elemen Non-Zero (nnz)   : {mat_item.nnz:,}")
print(f"Sparsity                : {sparsity_user:.2f}%")
print(f"Rata-rata User per Item : {mat_item.nnz / n_items:.2f} user")
""")

add_md("""
**Visualisasi Plot NetworkX Proyeksi VSM Simpul Item:**
Menampilkan graf proyeksi item (Item Co-occurrence Graph) di mana keterhubungan antar-item terbentuk dari pola *co-viewing* oleh pengunjung yang sama.
""")

add_code(r"""
# Menampilkan visualisasi plot NetworkX VSM Item Projection
display(Image(filename="plots/vsm_item_projection.png", width=650))
""")

# --- 2.1.6 Evaluasi Proyeksi ---
add_md("""
#### **2.1.6 Evaluasi Komparatif Proyeksi User vs Item: Mana yang Lebih Efektif dan Efisien?**

Berdasarkan eksplorasi VSM pada Sub-bab 2.1.4 dan 2.1.5, perbandingan dilakukan pada aspek komputasi, karakteristik struktur graf, dan relevansi tujuan analisis:

| Parameter Evaluasi | Proyeksi Simpul User ($G_U$) | Proyeksi Simpul Item ($G_I$) |
| :--- | :--- | :--- |
| **Dimensi Objek ($N$)** | $374$ Simpul Pengunjung | $9.137$ Simpul Produk |
| **Dimensi Fitur ($D$)** | $9.137$ Item | $374$ Pengunjung |
| **Ukuran Matriks Similarity** | $374 \\times 374$ ($139.876$ sel) | $9.137 \\times 9.137$ ($83.484.869$ sel) |
| **Kompleksitas Komputasi** | $\\mathcal{O}(\\|U\\|^2 \\cdot \\|I\\|) \\approx 1,28 \\times 10^9$ FLOPs | $\\mathcal{O}(\\|I\\|^2 \\cdot \\|U\\|) \\approx 3,12 \\times 10^{10}$ FLOPs |
| **Kebutuhan Memori RAM** | Sangat Ringan (< 2 MB) | Sangat Berat (~650 MB untuk dense float64) |
| **Kerapatan Informasi (Density)** | Jauh lebih padat, komunitas pengguna jelas | Sangat renggang (*extremely sparse*), banyak *isolated nodes* |
| **Relevansi Tugas Analytics** | **Sangat Sesuai** untuk User-based KNN | Kurang efisien untuk personalisasi pengguna tunggal |

**Uraian Kesimpulan:**
1. **Efisiensi:** **Proyeksi Simpul User jauh lebih efisien** dengan komputasi **~24,4 kali lebih cepat** dan alokasi memori yang jauh lebih kecil dibandingkan proyeksi simpul Item.
2. **Efektivitas:** **Proyeksi Simpul User lebih efektif** untuk skenario sistem rekomendasi ini karena target tugas analitik (Soal 2.2) adalah merekomendasikan item baru kepada seorang user terpilih melalui *User-based Collaborative Filtering*. Graf pengguna yang terproyeksi secara langsung memodelkan relasi *neighborhood* dan kedekatan preferensi antar-pengunjung.
""")

# --- 2.1.7 Similarity Calculation & Write Back ---
add_md("""
#### **2.1.7 Perhitungan Similarity pada Graf Terproyeksi dan Penulisan Kembali ke Neo4J**

Perhitungan kemiripan (Cosine Similarity) dilakukan antara target user **Visitor `1293068`** terhadap seluruh pengunjung lain dalam graf terproyeksi menggunakan Python:
$$\\text{Cosine Similarity}(u, v) = \\frac{\\mathbf{u} \\cdot \\mathbf{v}}{\\|\\mathbf{u}\\| \\|\\mathbf{v}\\|}$$
""")

add_code(r"""
from sklearn.metrics.pairwise import cosine_similarity

target_user = 1293068
target_idx = user_map[target_user]
target_vec = mat_user[target_idx]

# Hitung similarity target user ke seluruh user
sims = cosine_similarity(target_vec, mat_user).flatten()
sorted_indices = np.argsort(sims)[::-1]

# Ambil 5 record dengan similarity tertinggi (selain target_user itu sendiri)
top5_indices = [idx for idx in sorted_indices if idx != target_idx][:5]

print(f"Top 5 Rekor Similarity Tertinggi untuk Record Acuan (Visitor: {target_user}):")
top5_records = []
for rank, idx in enumerate(top5_indices, 1):
    u_id = users[idx]
    score = float(sims[idx])
    top5_records.append({"source": target_user, "target": u_id, "score": score})
    print(f" {rank}. Visitor {u_id:<10} | Cosine Similarity = {score:.4f}")
""")

add_md("""
##### **(a) Kueri CYPHER untuk Mendapatkan 5 Records dengan Similarity Tertinggi:**
```cypher
MATCH (u1:Visitor {visitorId: 1293068})-[r:SIMILAR]->(u2:Visitor)
RETURN u1.visitorId AS sourceUser, u2.visitorId AS similarUser, r.score AS similarityScore
ORDER BY r.score DESC
LIMIT 5;
```

##### **(b) Menuliskan Kembali Nilai Similarity ke Graf Neo4J dan Menampilkan Hasil Kuerinya:**
""")

add_code(r"""
# Penulisan kembali nilai similarity ke Neo4j
write_query = '''
UNWIND $batch AS rec
MATCH (u1:Visitor {visitorId: rec.source})
MATCH (u2:Visitor {visitorId: rec.target})
MERGE (u1)-[r:SIMILAR {score: rec.score}]->(u2)
RETURN count(r) AS updatedCount
'''

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session:
        session.execute_write(lambda tx: tx.run(write_query, batch=top5_records))
        
        # Eksekusi kueri verifikasi (Soal 2.1.7b)
        cypher_verify = '''
        MATCH (u1:Visitor {visitorId: $target})-[r:SIMILAR]->(u2:Visitor)
        RETURN u1.visitorId AS sourceUser, u2.visitorId AS similarUser, r.score AS similarityScore
        ORDER BY r.score DESC
        LIMIT 5
        '''
        records = session.run(cypher_verify, target=target_user)
        print("Hasil Kueri CYPHER dari Graf Neo4J (Verifikasi Relasi SIMILAR):")
        for rec in records:
            print(f"(:Visitor {{visitorId: {rec['sourceUser']}}})-[:SIMILAR {{score: {rec['similarityScore']:.4f}}}]->(:Visitor {{visitorId: {rec['similarUser']}}})")
""")

# --- 2.1.8 Kondisi Sebelum vs Sesudah ---
add_md("""
#### **2.1.8 Perbandingan Kondisi Graf SEBELUM dan SESUDAH Perhitungan Similarity**

##### **1. Kondisi SEBELUM Perhitungan Similarity**
- Struktur graf berjenis **Bipartite Graph (Two-mode network)**.
- Hanya terdapat simpul berlabel `:Visitor` dan `:Item`.
- Relasi yang ada hanyalah interaksi dari pengunjung ke produk (`[:VIEWED]`, `[:ADDED_TO_CART]`, `[:BOUGHT]`). Tidak ada relasi langsung antar-simpul berlabel sama.
- **Kueri CYPHER Kondisi Sebelum:**
  ```cypher
  // Memeriksa relasi bipartite dan memastikan ketiadaan relasi SIMILAR
  MATCH (v:Visitor {visitorId: 1293068})-[r]->(i:Item)
  RETURN type(r) AS relType, count(r) AS interactionCount;
  ```
""")

add_code(r"""
# Menampilkan visualisasi kondisi SEBELUM perhitungan similarity
display(Image(filename="plots/graph_before_similarity.png", width=700))
""")

add_md("""
##### **2. Kondisi SESUDAH Perhitungan Similarity**
- Struktur graf bertransformasi menjadi **Homogeneous / Monopartite Network** antar-pengunjung yang diperkaya (*enriched graph*).
- Terdapat relasi baru `[:SIMILAR {score: ...}]` yang menghubungkan langsung simpul `:Visitor` dengan tetangga terdekatnya berdasarkan kedekatan vektor preferensi.
- **Kueri CYPHER Kondisi Sesudah:**
  ```cypher
  // Membaca relasi SIMILAR yang telah tersimpan antar-Visitor
  MATCH (v1:Visitor {visitorId: 1293068})-[r:SIMILAR]->(v2:Visitor)
  RETURN v1.visitorId AS focalUser, v2.visitorId AS neighborUser, r.score AS similarityScore
  ORDER BY r.score DESC;
  ```
""")

add_code(r"""
# Menampilkan visualisasi kondisi SESUDAH perhitungan similarity
display(Image(filename="plots/graph_after_similarity.png", width=700))
""")

# --- 2.2 Analytics ---
add_md("""
---
### **2.2 Analytics**

#### **2.2.1 Rekomendasi Collaborative Filtering KNN ($k=5$)**

1. **Pemilihan User Acak yang Dapat Direproduksi:**
   - Parameter seed ditetapkan: `np.random.seed(732)` (dapat direproduksi).
   - Dari sekumpulan pengguna yang memiliki interaksi aktif pada Fold Training (P1) sekaligus Fold Testing (P2), terpilih pengunjung: **Visitor `1293068`**.
   - User ini memiliki 19 catatan aktivitas di Fold P1 (8 item unik), dan 12 catatan aktivitas di Fold P2 (7 item unik).

2. **Algoritma Rekomendasi Collaborative Filtering KNN:**
   - Menemukan $k=5$ tetangga terdekat dari user target berdasarkan Cosine Similarity.
   - Mengumpulkan item-item yang pernah diakses oleh tetangga namun belum pernah dilihat oleh user target.
   - Menghitung skor prediksi preferensi:
     $$\\hat{r}_{u, i} = \\sum_{v \\in \\mathcal{N}_k(u)} \\text{sim}(u, v) \\cdot w_{v, i}$$
     di mana $w_{v, i}$ bernilai 1.0 (view), 2.0 (addtocart), dan 3.0 (transaction).
""")

add_code(r"""
# Menjalankan Algoritma Rekomendasi KNN (k=5)
user_p1_items = set(sub_df[sub_df["visitorid"] == target_user]["itemid"])

candidate_scores = {}
event_weights = {"view": 1.0, "addtocart": 2.0, "transaction": 3.0}

for rec in top5_records:
    n_user = rec["target"]
    n_sim = rec["score"]
    n_events = sub_df[sub_df["visitorid"] == n_user]
    
    for _, row in n_events.iterrows():
        it = int(row["itemid"])
        if it not in user_p1_items:
            w = event_weights.get(row["event"], 1.0)
            candidate_scores[it] = candidate_scores.get(it, 0.0) + (n_sim * w)

sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)

print("=== 3 Item yang Diiklankan untuk k = 5 (Soal 2.2.1b) ===")
for rank, (it, score) in enumerate(sorted_candidates[:3], 1):
    print(f"Rank {rank}: Item ID {it:<10} | Skor Prediksi Preferensi: {score:.4f}")
""")

add_md("""
#### **2.2.2 Evaluasi Rekomendasi: Hit@5 dan NDCG@5**

Rekomendasi model dievaluasi secara offline terhadap data faktual interaksi pengunjung target pada **Fold Testing (P2)**.
- **Ground Truth P2 Visitor `1293068`:** Terdiri dari 7 item unik: `{9877, 37115, 96377, 98747, 239006, 241555, 283115}`.
""")

add_code(r"""
# Membaca data Fold Testing (P2) untuk Visitor target
df_p2 = pd.read_csv("data/events_p2_test.csv")
p2_user = df_p2[df_p2["visitorid"] == target_user]
p2_ground_truth = set(p2_user["itemid"].unique())

print(f"Item faktual yang diakses Visitor {target_user} pada Fold Testing P2:")
for it in sorted(p2_ground_truth):
    print(f" - Item ID {it}")

# Evaluasi Top 5 Rekomendasi
top_5_items = [it for it, _ in sorted_candidates[:5]]
hits = [1 if it in p2_ground_truth else 0 for it in top_5_items]

print("\n=== Detail Evaluasi Rekomendasi Top-5 ===")
for rank, (it, hit) in enumerate(zip(top_5_items, hits), 1):
    status = "HIT (Sesuai dengan aktivitas P2!)" if hit == 1 else "Not in P2"
    print(f"Rank {rank}: Item {it:<10} | Indikator Hit: {hit} -> {status}")

# Perhitungan Hit@5
hit_at_5 = 1 if sum(hits) > 0 else 0

# Perhitungan DCG@5
dcg_5 = sum([h / np.log2(idx + 2) for idx, h in enumerate(hits)])

# Perhitungan IDCG@5 (Ideal DCG bila item hit menempati peringkat teratas)
idcg_5 = sum([1 / np.log2(idx + 2) for idx in range(min(len(p2_ground_truth), 5))])

# Perhitungan NDCG@5
ndcg_5 = dcg_5 / idcg_5 if idcg_5 > 0 else 0.0

print(f"\n================ HASIL AKHIR EVALUASI ================")
print(f"Hit@5  : {hit_at_5} ({sum(hits)} dari 5 item rekomendasi diakses user pada testing)")
print(f"DCG@5  : {dcg_5:.4f}")
print(f"IDCG@5 : {idcg_5:.4f}")
print(f"NDCG@5 : {ndcg_5:.4f}")
print(f"=======================================================")
""")

add_md("""
**Visualisasi Evaluasi Rekomendasi Top-5 Item:**
Menampilkan diagram batang peringkat item yang direkomendasikan beserta status keberhasilan *Hit* pada periode pengujian P2.
""")

add_code(r"""
# Menampilkan visualisasi evaluasi rekomendasi KNN
display(Image(filename="plots/knn_recommendations.png", width=700))
""")

add_md("""
**Uraian Interpretasi Evaluasi:**
1. **Hit@5 bernilai 1 (Sukses Penuh):** Model berhasil merekomendasikan item yang benar-benar dikunjungi oleh pengguna pada periode pengujian berikutnya (*testing period*). Dari 5 item rekomendasi teratas, terdapat **2 item yang menjadi HIT**, yaitu **Item ID `241555`** pada Rank 2 dan **Item ID `239006`** pada Rank 4.
2. **NDCG@5 bernilai 0.3601:** Nilai Normalized Discounted Cumulative Gain memperhitungkan posisi ranking item relevan. Karena salah satu item relevan berhasil ditempatkan pada posisi tinggi (Rank 2), model memperoleh akumulasi gain yang signifikan ($DCG@5 = 1.0616$). Hal ini membuktikan bahwa algoritma graf bipartite dan kedekatan preferensi VSM mampu menangkap minat laten (*latent interest*) pengunjung e-commerce dengan sangat baik.
""")

# --- Kesimpulan ---
add_md("""
---
## **3. Ringkasan & Kesimpulan**

1. **Pemodelan Graf Bipartite:** Representasi interaksi e-commerce sebagai graf bipartite (`Visitor -> Item`) memungkinkan pemisahan entitas yang jelas serta penyimpanan metadata interaksi (`timestamp`, `event`, `transactionId`) pada edge secara efisien di Neo4j.
2. **VSM User vs Item:** Proyeksi pada simpul User terbukti **jauh lebih efisien** secara komputasi ($\mathcal{O}(|U|^2 \cdot |I|)$ vs $\mathcal{O}(|I|^2 \cdot |U|)$) dengan penghematan hingga 24 kali lipat, sekaligus **jauh lebih efektif** untuk tugas personalisasi rekomendasi.
3. **Penyimpanan Nilai Similarity pada Graf:** Penulisan kembali nilai cosine similarity sebagai edge `[:SIMILAR {score: ...}]` pada Neo4J mengubah graf bipartite menjadi graf terproyeksi yang siap digunakan untuk penelusuran graf traversal dan *neighborhood queries* secara instan.
4. **Kinerja Rekomendasi KNN:** Sistem rekomendasi Collaborative Filtering KNN ($k=5$) berhasil mencatatkan **Hit@5 = 1** dan **NDCG@5 = 0.3601** pada evaluasi offline terhadap Fold Testing (P2), membuktikan validitas model graf dalam memprediksi perilaku belanja masa depan pengunjung.
""")

nb["cells"] = cells

# Simpan berkas notebook
notebook_path = "UTS_GSD_23031554018_MOCH_AKBAR_HANAFI.ipynb"
with open(notebook_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Jupyter Notebook berhasil dibuat: {notebook_path}")
