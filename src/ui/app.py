import argparse
import subprocess
from pyspark.sql import SparkSession
from pyspark.sql.functions import rand, col
from PIL import Image
import subprocess
from pyspark.sql.functions import udf, lit
from pyspark.sql.types import BooleanType
import logging
import os
import numpy as np
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType

logging.getLogger("py4j").setLevel(logging.ERROR)
logging.getLogger("pyspark").setLevel(logging.ERROR)

spark = SparkSession.builder \
    .appName("BookCoverCLI") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

df = spark.read.parquet("hdfs://namenode:9000/project/raw/book_cover_analysis.parquet")


def show_image(book_id, split):
    #book_id="10031.The_Wall"
    hdfs_path = f"/project/images/raw/{book_id}.jpg"
    local_path = f"/workspace/images/{book_id}.jpg"
    temp_path = f"/tmp/{book_id}.jpg"
    output_path = f"/workspace/output/{book_id}.jpg"

    try:
        print("Checking HDFS:", hdfs_path)

        jvm = spark.sparkContext._jvm
        conf = spark.sparkContext._jsc.hadoopConfiguration()

        uri = jvm.java.net.URI("hdfs://namenode:9000")
        hdfs = jvm.org.apache.hadoop.fs.FileSystem.get(uri, conf)

        path = jvm.org.apache.hadoop.fs.Path(hdfs_path)

        if hdfs.exists(path):
            print("Image found in HDFS")

            hdfs.copyToLocalFile(
                False,
                path,
                jvm.org.apache.hadoop.fs.Path(temp_path)
            )

            img = Image.open(temp_path)

        else:
            print("Image not found in HDFS, using local copy")
            img = Image.open(local_path)

    except Exception as e:
        print(f"HDFS access failed ({e}), using local copy")
        img = Image.open(local_path)

    os.makedirs("/workspace/output", exist_ok=True)

    img.save(output_path)

    print(f"Saved image to {output_path}")

def print_row(row):
    print("\n" + "=" * 60)
    print("ID:", row["id"])
    print("Split:", row["split"])
    print("True:", row["true_labels"])
    print("Pred:", row["pred_labels"])
    print("Probs (first 5):", row["pred_probs"][:5])
    print("=" * 60 + "\n")


def pick_one(filtered_df):
    row = filtered_df.orderBy(rand()).limit(1).collect()[0]
    return row



def cmd_random(args):
    genre = args.genre

    filtered = df.filter(col(f"{genre}_true") == 1)

    if args.split:
        filtered = filtered.filter(col("split") == args.split)

    row = pick_one(filtered)

    print_row(row)
    show_image(row["id"], row["split"])




def cmd_mistakes(args):
    genre = args.genre

    filtered = df.filter(
        (col(f"{genre}_true") == 1) &
        (col(f"{genre}_pred") == 0)
    )

    if args.split:
        filtered = filtered.filter(col("split") == args.split)

    row = pick_one(filtered)

    print_row(row)
    print(" Model missed this one")

    show_image(row["id"], row["split"])



def cmd_confident(args):
    genre = args.genre

    filtered = df.filter(
        (col(f"{genre}_true") == 1) &
        (col(f"{genre}_pred") == 1)
    ).orderBy(col(f"{genre}_prob").desc())

    if args.split:
        filtered = filtered.filter(col("split") == args.split)

    row = filtered.limit(1).collect()[0]

    print_row(row)
    print(" Highly confident correct prediction")

    show_image(row["id"], row["split"])


def cosine_similarity(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)

    denom = np.linalg.norm(v1) * np.linalg.norm(v2)

    if denom == 0:
        return 0.0

    return float(np.dot(v1, v2) / denom)


cosine_udf = udf(cosine_similarity, DoubleType())


def cmd_recommend(args):

    book_id = args.book_id
    quantity=int(args.quantity)

    target = (
        df.filter(col("id") == book_id)
          .select("embedding")
          .collect()
    )

    if not target:
        print(f"Book {book_id} not found")
        return

    target_embedding = target[0]["embedding"]

    recommendations = (
        df
        .withColumn(
            "similarity",
            cosine_udf(
                col("embedding"),
                lit(target_embedding)
            )
        )
        .filter(col("id") != book_id)
        .orderBy(col("similarity").desc())
        .limit(quantity)
        .collect()
    )

    print("Query book:")
    show_image(book_id, None)

    print("\nTop recommendations:\n")

    for i, row in enumerate(recommendations, start=1):
        print(
            f"{i}. {row['id']} "
            f"(similarity={row['similarity']:.4f})"
        )
        show_image(row['id'],None)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")

# random
p1 = subparsers.add_parser("random")
p1.add_argument("--genre", required=True)
p1.add_argument(
    "--split",
    choices=["train", "val", "test"],
    default=None
)
p1.set_defaults(func=cmd_random)

# mistakes
p2 = subparsers.add_parser("mistakes")
p2.add_argument("--genre", required=True)
p2.add_argument(
    "--split",
    choices=["train", "val", "test"],
    default=None
)
p2.set_defaults(func=cmd_mistakes)

# confident
p3 = subparsers.add_parser("confident")
p3.add_argument("--genre", required=True)
p3.add_argument(
    "--split",
    choices=["train", "val", "test"],
    default=None
)
p3.set_defaults(func=cmd_confident)

#recommender
p4 = subparsers.add_parser("recommend")
p4.add_argument("--book-id", required=True)
p4.add_argument("--quantity", required=True)
p4.set_defaults(func=cmd_recommend)


args = parser.parse_args()
args.func(args)