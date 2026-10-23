#!/usr/bin/env python3
"""
import_neo4j.py
Script untuk mengimpor dataset RetailRocket ke database Neo4J dengan batch processing.
Sesuai Panduan UTS Graf Sains Data - Moch. Akbar Hanafi (23031554018)
"""

import os
import sys
import argparse
import time
import pandas as pd
from tqdm import tqdm
from neo4j import GraphDatabase


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Impor dataset RetailRocket ke database Neo4J menggunakan batching."
    )
    parser.add_argument(
        "-u", "--user", default="neo4j", help="Username Neo4j (default: neo4j)"
    )
    parser.add_argument(
        "-p", "--password", default="password123", help="Password Neo4j (default: password123)"
    )
    parser.add_argument(
        "-b", "--bolt", default="neo4j://localhost:7687", help="Neo4J URI / Bolt (default: neo4j://localhost:7687)"
    )
    parser.add_argument(
        "-s", "--source", default="data/events_subgraph.csv", help="File CSV sumber data (default: data/events_subgraph.csv)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=1000, help="Ukuran batch transaksi (default: 1000)"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Reset/bersihkan isi database sebelum impor"
    )
    return parser.parse_args()


def create_constraints(session):
    print("Membuat unique constraints untuk Visitor dan Item...")
    session.run(
        "CREATE CONSTRAINT unique_visitor_id IF NOT EXISTS "
        "FOR (v:Visitor) REQUIRE v.visitorId IS UNIQUE;"
    )
    session.run(
        "CREATE CONSTRAINT unique_item_id IF NOT EXISTS "
        "FOR (i:Item) REQUIRE i.itemId IS UNIQUE;"
    )
    print("Constraints berhasil dibuat/diverifikasi.")


def import_batch(tx, batch):
    cypher_query = """
    UNWIND $batch AS row
    MERGE (v:Visitor {visitorId: row.visitorid})
    MERGE (i:Item {itemId: row.itemid})
    WITH v, i, row
    CALL (v, i, row) {
        WITH v, i, row WHERE row.event = 'view'
        CREATE (v)-[:VIEWED {timestamp: row.timestamp}]->(i)
        RETURN count(*) AS cnt

        UNION ALL

        WITH v, i, row WHERE row.event = 'addtocart'
        CREATE (v)-[:ADDED_TO_CART {timestamp: row.timestamp}]->(i)
        RETURN count(*) AS cnt

        UNION ALL

        WITH v, i, row WHERE row.event = 'transaction'
        CREATE (v)-[:BOUGHT {timestamp: row.timestamp, transactionId: row.transactionid}]->(i)
        RETURN count(*) AS cnt
    }
    RETURN count(*) AS total
    """
    tx.run(cypher_query, batch=batch)


def main():
    args = parse_arguments()

    if not os.path.exists(args.source):
        print(f"Error: File '{args.source}' tidak ditemukan!")
        sys.exit(1)

    print(f"Menghubungkan ke Neo4j di {args.bolt}...")
    try:
        driver = GraphDatabase.driver(args.bolt, auth=(args.user, args.password))
        driver.verify_connectivity()
        print("Koneksi ke Neo4j berhasil terverifikasi.")
    except Exception as e:
        print(f"Gagal terhubung ke database: {e}")
        sys.exit(1)

    with driver.session() as session:
        if args.reset:
            print("Mereset isi database Neo4j (MATCH (n) DETACH DELETE n)...")
            session.run("MATCH (n) DETACH DELETE n;")
            print("Database berhasil di-reset.")

        create_constraints(session)

        print(f"Membaca file data dari: {args.source}")
        df = pd.read_csv(args.source)
        df["transactionid"] = df["transactionid"].fillna("").astype(str)

        total_rows = len(df)
        batch_size = args.batch_size
        total_chunks = (total_rows + batch_size - 1) // batch_size

        print(f"Total baris data: {total_rows:,} ({total_chunks} batch)")
        print("Memulai proses impor batch ke Neo4j...")

        start_time = time.time()
        for i in tqdm(range(0, total_rows, batch_size), total=total_chunks, desc="Mengimpor Batch Data"):
            batch = df.iloc[i : i + batch_size].to_dict(orient="records")
            session.execute_write(import_batch, batch)

        elapsed = time.time() - start_time
        print(f"Proses impor berhasil selesai dalam {elapsed:.2f} detik ({total_rows/elapsed:.1f} baris/detik).")

        # Ringkasan komposisi simpul dan relasi
        print("\n--- Ringkasan Subgraph di Neo4J ---")
        v_count = session.run("MATCH (v:Visitor) RETURN count(v) AS cnt").single()["cnt"]
        i_count = session.run("MATCH (i:Item) RETURN count(i) AS cnt").single()["cnt"]
        print(f"Total Node Visitor : {v_count:,}")
        print(f"Total Node Item    : {i_count:,}")

        rel_records = session.run("MATCH ()-[r]->() RETURN type(r) AS relType, count(r) AS cnt ORDER BY cnt DESC")
        for rec in rel_records:
            print(f"Relasi [:{rec['relType']}] : {rec['cnt']:,}")

    driver.close()
    print("Koneksi Neo4J ditutup.")


if __name__ == "__main__":
    main()
