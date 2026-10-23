#!/usr/bin/env python3
"""
vsm_similarity_analytics.py
Modul komputasi VSM, Proyeksi Graf NetworkX, Perhitungan Cosine Similarity,
Write-back Edge Similarity ke Neo4j, Rekomendasi Collaborative Filtering KNN,
dan Evaluasi Offline (Hit@5, NDCG@5) untuk UTS Graf Sains Data.
Mahasiswa: MOCH. AKBAR HANAFI (23031554018)
"""

import os
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from neo4j import GraphDatabase

# Konfigurasi Styling Plot
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password123")
TARGET_USER = 1293068
SEED = 17


def load_data():
    print("Memuat dataset training dan testing...")
    p1 = pd.read_csv("data/events_subgraph.csv")
    p2 = pd.read_csv("data/events_p2_test.csv")
    return p1, p2


def analyze_vsm(p1):
    print("\n=== Analisis Vector Space Modelling (VSM) ===")
    users = sorted(p1["visitorid"].unique())
    items = sorted(p1["itemid"].unique())

    n_users = len(users)
    n_items = len(items)

    user_map = {u: idx for idx, u in enumerate(users)}
    item_map = {it: idx for idx, it in enumerate(items)}

    row_ind = [user_map[u] for u in p1["visitorid"]]
    col_ind = [item_map[it] for it in p1["itemid"]]
    weights = p1["event"].map({"view": 1.0, "addtocart": 2.0, "transaction": 3.0}).values

    # Matriks VSM User-Item (User sebagai vektor, dimensi = Item)
    mat_user = csr_matrix((weights, (row_ind, col_ind)), shape=(n_users, n_items))

    # Matriks VSM Item-User (Item sebagai vektor, dimensi = User)
    mat_item = mat_user.T.tocsr()

    total_cells = n_users * n_items
    nnz = mat_user.nnz
    sparsity = (1.0 - (nnz / total_cells)) * 100

    print(f"Dimensi VSM User : ({n_users:,} User x {n_items:,} Item)")
    print(f"Dimensi VSM Item : ({n_items:,} Item x {n_users:,} User)")
    print(f"Total Elemen     : {total_cells:,}")
    print(f"Elemen Non-Zero  : {nnz:,}")
    print(f"Sparsity Matriks : {sparsity:.2f}%")

    return users, items, mat_user, mat_item, user_map, item_map


def compute_user_similarities(users, mat_user, target_user, user_map, k=5):
    print(f"\nMenghitung Cosine Similarity untuk Target User: {target_user}...")
    target_idx = user_map[target_user]
    target_vec = mat_user[target_idx]

    sims = cosine_similarity(target_vec, mat_user).flatten()
    sorted_indices = np.argsort(sims)[::-1]

    # Ambil tetangga terdekat selain dirinya sendiri
    neighbors = [idx for idx in sorted_indices if idx != target_idx][:k]

    neighbor_records = []
    for rank, n_idx in enumerate(neighbors, 1):
        neighbor_user = users[n_idx]
        score = float(sims[n_idx])
        neighbor_records.append({
            "rank": rank,
            "user": neighbor_user,
            "similarity": score
        })
        print(f"Rank {rank}: Visitor {neighbor_user} -> Similarity = {score:.4f}")

    return neighbor_records, sims


def update_neo4j_similarities(driver, target_user, neighbor_records):
    print("\nMenulis kembali relasi SIMILAR ke database Neo4j...")
    query = """
    UNWIND $batch AS rec
    MATCH (u1:Visitor {visitorId: rec.source})
    MATCH (u2:Visitor {visitorId: rec.target})
    MERGE (u1)-[r:SIMILAR {score: rec.score}]->(u2)
    RETURN count(r) AS updated
    """
    batch = [
        {"source": target_user, "target": rec["user"], "score": rec["similarity"]}
        for rec in neighbor_records
    ]

    with driver.session() as session:
        session.execute_write(lambda tx: tx.run(query, batch=batch))

        # Query verifikasi hasil penulisan
        verify_query = """
        MATCH (u1:Visitor {visitorId: $target})-[r:SIMILAR]->(u2:Visitor)
        RETURN u1.visitorId AS sourceUser, u2.visitorId AS targetUser, r.score AS similarity
        ORDER BY r.score DESC
        LIMIT 5
        """
        result = session.run(verify_query, target=target_user)
        print("\nHasil Query Cypher Verifikasi Relasi SIMILAR:")
        for rec in result:
            print(f"({rec['sourceUser']})-[:SIMILAR {{score: {rec['similarity']:.4f}}}]->({rec['targetUser']})")


def run_knn_recommendations(p1, p2, target_user, neighbor_records, k=5):
    print("\n=== Collaborative Filtering KNN (k=5) ===")
    user_p1_items = set(p1[p1["visitorid"] == target_user]["itemid"])
    print(f"Jumlah item unik yang telah diakses target user di P1: {len(user_p1_items)}")

    candidate_scores = {}
    event_weights = {"view": 1.0, "addtocart": 2.0, "transaction": 3.0}

    for rec in neighbor_records[:k]:
        n_user = rec["user"]
        n_sim = rec["similarity"]
        n_events = p1[p1["visitorid"] == n_user]

        for _, row in n_events.iterrows():
            it = int(row["itemid"])
            if it not in user_p1_items:
                w = event_weights.get(row["event"], 1.0)
                candidate_scores[it] = candidate_scores.get(it, 0.0) + (n_sim * w)

    sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)

    print("\n--- Top 3 Item yang Diiklankan / Direkomendasikan (No. 1b Analytics) ---")
    top_3 = sorted_candidates[:3]
    for rank, (it, score) in enumerate(top_3, 1):
        print(f"Rank {rank}: Item ID {it} | Skor Prediksi Preferensi: {score:.4f}")

    top_5 = sorted_candidates[:5]
    print("\n--- Top 5 Rekomendasi Item Lengkap ---")
    for rank, (it, score) in enumerate(top_5, 1):
        print(f"Rank {rank}: Item ID {it} | Skor: {score:.4f}")

    # Evaluasi terhadap Fold Testing (P2)
    p2_user = p2[p2["visitorid"] == target_user]
    p2_ground_truth = set(p2_user["itemid"].unique())
    print(f"\nGround Truth Fold Testing (P2) Target User ({len(p2_ground_truth)} item unik): {sorted(p2_ground_truth)}")

    rec_items = [it for it, _ in top_5]
    hits = [1 if it in p2_ground_truth else 0 for it in rec_items]
    print(f"Indikator Hit per Rank (1-5): {hits}")

    hit_at_5 = 1 if sum(hits) > 0 else 0

    # Perhitungan DCG@5 dan NDCG@5
    dcg = sum([h / np.log2(idx + 2) for idx, h in enumerate(hits)])

    # IDCG@5: skenario ideal jika seluruh item relevan berada di peringkat teratas
    ideal_hits = [1] * min(len(p2_ground_truth), 5)
    idcg = sum([1 / np.log2(idx + 2) for idx in range(len(ideal_hits))])
    ndcg_at_5 = dcg / idcg if idcg > 0 else 0.0

    print("\n=== Hasil Evaluasi Offline ===")
    print(f"Hit@5  : {hit_at_5} ({sum(hits)} dari 5 item rekomendasi diakses user pada periode testing)")
    print(f"DCG@5  : {dcg:.4f}")
    print(f"IDCG@5 : {idcg:.4f}")
    print(f"NDCG@5 : {ndcg_at_5:.4f}")

    return top_3, top_5, hits, hit_at_5, dcg, idcg, ndcg_at_5, p2_ground_truth


def generate_visualizations(p1, target_user, neighbor_records, top_5_recs, hits, p2_ground_truth):
    print("\nMenghasilkan visualisasi grafik NetworkX dan Matplotlib...")
    os.makedirs("plots", exist_ok=True)

    # 1. Plot VSM User Projection
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    G_user = nx.Graph()
    G_user.add_node(f"User {target_user}", type="target")
    for rec in neighbor_records:
        nu = f"User {rec['user']}"
        G_user.add_node(nu, type="neighbor")
        G_user.add_edge(f"User {target_user}", nu, weight=rec["similarity"])

    pos = nx.spring_layout(G_user, seed=42, k=1.2)
    node_colors = ["#e11d48" if G_user.nodes[n]["type"] == "target" else "#2563eb" for n in G_user.nodes]
    nx.draw_networkx_nodes(G_user, pos, node_color=node_colors, node_size=1800, alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G_user, pos, width=2.5, edge_color="#64748b", alpha=0.7, ax=ax)
    nx.draw_networkx_labels(G_user, pos, font_size=9, font_weight="bold", font_color="#ffffff", ax=ax)

    edge_labels = {(u, v): f"{d['weight']:.3f}" for u, v, d in G_user.edges(data=True)}
    nx.draw_networkx_edge_labels(G_user, pos, edge_labels=edge_labels, font_size=8, font_color="#0f172a", ax=ax)

    ax.set_title(f"Proyeksi VSM Simpul User & Cosine Similarity (Target: {target_user})", fontsize=12, fontweight="bold", pad=15)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("plots/vsm_user_projection.png")
    plt.close()
    print("-> Tersimpan: plots/vsm_user_projection.png")

    # 2. Plot VSM Item Projection (Item Co-occurrence)
    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    G_item = nx.Graph()
    target_items = list(p1[p1["visitorid"] == target_user]["itemid"].unique())[:8]

    # Ambil interaksi item-item tersebut pada subset user
    sub_events = p1[p1["itemid"].isin(target_items)]
    for it in target_items:
        G_item.add_node(f"Item {it}")

    # Tambahkan edge jika ada co-view oleh user yang sama
    for i in range(len(target_items)):
        for j in range(i + 1, len(target_items)):
            it1, it2 = target_items[i], target_items[j]
            u1 = set(sub_events[sub_events["itemid"] == it1]["visitorid"])
            u2 = set(sub_events[sub_events["itemid"] == it2]["visitorid"])
            shared = len(u1.intersection(u2))
            if shared > 0:
                G_item.add_edge(f"Item {it1}", f"Item {it2}", weight=shared)

    pos_item = nx.circular_layout(G_item)
    nx.draw_networkx_nodes(G_item, pos_item, node_color="#0d9488", node_size=1500, alpha=0.9, ax=ax)
    edge_weights = [d["weight"] * 0.8 for _, _, d in G_item.edges(data=True)]
    nx.draw_networkx_edges(G_item, pos_item, width=edge_weights, edge_color="#0284c7", alpha=0.6, ax=ax)
    nx.draw_networkx_labels(G_item, pos_item, font_size=8, font_weight="bold", font_color="#ffffff", ax=ax)

    ax.set_title(f"Proyeksi VSM Simpul Item: Co-occurrence Interaksi (Target Catalog)", fontsize=12, fontweight="bold", pad=15)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("plots/vsm_item_projection.png")
    plt.close()
    print("-> Tersimpan: plots/vsm_item_projection.png")

    # 3. Plot Kondisi SEBELUM Perhitungan Similarity (Graf Bipartite)
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    G_before = nx.DiGraph()
    G_before.add_node(f"User {target_user}", layer=0, type="target_user")

    top_neighbors = [rec["user"] for rec in neighbor_records[:3]]
    for nu in top_neighbors:
        G_before.add_node(f"User {nu}", layer=0, type="neighbor_user")

    # Tambahkan item-item yang menghubungkan target user dan tetangganya
    u_items = list(p1[p1["visitorid"] == target_user]["itemid"].unique())[:5]
    for it in u_items:
        G_before.add_node(f"Item {it}", layer=1, type="item")
        G_before.add_edge(f"User {target_user}", f"Item {it}", rel="VIEWED")

    for nu in top_neighbors:
        nu_items = set(p1[p1["visitorid"] == nu]["itemid"]).intersection(set(u_items))
        for it in nu_items:
            G_before.add_edge(f"User {nu}", f"Item {it}", rel="VIEWED")

    pos_bipartite = nx.bipartite_layout(G_before, [n for n in G_before.nodes if "User" in n])
    colors_before = [
        "#e11d48" if "target_user" in G_before.nodes[n]["type"]
        else "#2563eb" if "neighbor_user" in G_before.nodes[n]["type"]
        else "#10b981"
        for n in G_before.nodes
    ]
    nx.draw_networkx_nodes(G_before, pos_bipartite, node_color=colors_before, node_size=1600, alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G_before, pos_bipartite, edge_color="#94a3b8", arrows=True, arrowsize=15, width=1.8, ax=ax)
    nx.draw_networkx_labels(G_before, pos_bipartite, font_size=8, font_weight="bold", font_color="#ffffff", ax=ax)

    ax.set_title("Kondisi SEBELUM Perhitungan Similarity (Graf Bipartite Visitor -> Item)", fontsize=12, fontweight="bold", pad=15)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("plots/graph_before_similarity.png")
    plt.close()
    print("-> Tersimpan: plots/graph_before_similarity.png")

    # 4. Plot Kondisi SESUDAH Perhitungan Similarity (Graf Homogen dengan Edge SIMILAR)
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    G_after = nx.DiGraph()
    G_after.add_node(f"Visitor\n{target_user}", type="target")

    for rec in neighbor_records:
        nu_label = f"Visitor\n{rec['user']}"
        G_after.add_node(nu_label, type="neighbor")
        G_after.add_edge(f"Visitor\n{target_user}", nu_label, weight=rec["similarity"])

    pos_after = nx.spring_layout(G_after, seed=42, k=1.5)
    colors_after = ["#e11d48" if G_after.nodes[n]["type"] == "target" else "#2563eb" for n in G_after.nodes]
    nx.draw_networkx_nodes(G_after, pos_after, node_color=colors_after, node_size=2200, alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G_after, pos_after, edge_color="#e11d48", arrows=True, arrowsize=20, width=2.5, ax=ax)
    nx.draw_networkx_labels(G_after, pos_after, font_size=8, font_weight="bold", font_color="#ffffff", ax=ax)

    edge_labels_after = {(u, v): f"SIMILAR\nscore: {d['weight']:.4f}" for u, v, d in G_after.edges(data=True)}
    nx.draw_networkx_edge_labels(G_after, pos_after, edge_labels=edge_labels_after, font_size=8, font_color="#0f172a", ax=ax)

    ax.set_title("Kondisi SESUDAH Perhitungan Similarity (Relasi [:SIMILAR] Antar-Visitor)", fontsize=12, fontweight="bold", pad=15)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("plots/graph_after_similarity.png")
    plt.close()
    print("-> Tersimpan: plots/graph_after_similarity.png")

    # 5. Plot Rekomendasi & Evaluasi Hit/Miss
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    item_labels = [f"Item {it}" for it, _ in top_5_recs]
    scores = [score for _, score in top_5_recs]
    bar_colors = ["#10b981" if h == 1 else "#6366f1" for h in hits]

    bars = ax.bar(item_labels, scores, color=bar_colors, width=0.55, edgecolor="#ffffff", linewidth=1.5)
    for bar, h, sc in zip(bars, hits, scores):
        status_text = "HIT! (ada di P2)" if h == 1 else "Not in P2"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f"{sc:.2f}\n[{status_text}]",
                ha="center", va="bottom", fontsize=8, fontweight="bold",
                color="#065f46" if h == 1 else "#3730a3")

    ax.set_ylim(0, max(scores) * 1.35)
    ax.set_ylabel("Skor Rekomendasi Collaborative Filtering", fontsize=10, fontweight="bold")
    ax.set_title(f"Rekomendasi Top-5 Item untuk Visitor {target_user} (Evaluasi P2 Testing)", fontsize=12, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig("plots/knn_recommendations.png")
    plt.close()
    print("-> Tersimpan: plots/knn_recommendations.png")


def main():
    p1, p2 = load_data()
    users, items, mat_user, mat_item, user_map, item_map = analyze_vsm(p1)

    neighbor_records, sims = compute_user_similarities(users, mat_user, TARGET_USER, user_map, k=5)

    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
        update_neo4j_similarities(driver, TARGET_USER, neighbor_records)
        driver.close()
    except Exception as e:
        print(f"Peringatan: Gagal terhubung ke Neo4j untuk penulisan SIMILAR: {e}")

    top_3, top_5, hits, hit_at_5, dcg, idcg, ndcg_at_5, p2_ground_truth = run_knn_recommendations(
        p1, p2, TARGET_USER, neighbor_records, k=5
    )

    generate_visualizations(p1, TARGET_USER, neighbor_records, top_5, hits, p2_ground_truth)
    print("\nSeluruh tahapan analitik dan visualisasi berhasil diselesaikan.")


if __name__ == "__main__":
    main()
