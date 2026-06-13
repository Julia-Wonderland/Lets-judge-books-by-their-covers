# app.py

import argparse
import subprocess
from pyspark.sql import SparkSession
from pyspark.sql.functions import rand, col
from PIL import Image
import subprocess
from pyspark.sql.functions import udf
from pyspark.sql.types import BooleanType


spark = SparkSession.builder \
    .appName("BookCoverCLI") \
    .getOrCreate()

df = spark.read.parquet("hdfs://namenode:9000/project/raw/book_cover_analysis.parquet")


def show_image(book_id, split):
    hdfs_path = f"/project/images/raw/{book_id}.jpg"
    local_path = f"/workspace/images/{book_id}.jpg"

    """subprocess.run([
        "hdfs", "dfs", "-get", "-f",
        hdfs_path, local_path
    ])"""

    img = Image.open(local_path)
    img.show()
    img.save(f"/workspace/output/{book_id}.jpg")
    print("Saved image to /workspace/output/")


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

    row = pick_one(filtered)

    print_row(row)
    show_image(row["id"], row["split"])




def cmd_mistakes(args):
    genre = args.genre

    filtered = df.filter(
        (col(f"{genre}_true") == 1) &
        (col(f"{genre}_pred") == 0)
    )

    row = pick_one(filtered)

    print_row(row)
    print("❌ Model missed this one")

    show_image(row["id"], row["split"])



def cmd_confident(args):
    genre = args.genre

    filtered = df.filter(
        (col(f"{genre}_true") == 1) &
        (col(f"{genre}_pred") == 1)
    ).orderBy(col(f"{genre}_prob").desc())

    row = filtered.limit(1).collect()[0]

    print_row(row)
    print("🔥 Highly confident correct prediction")

    show_image(row["id"], row["split"])



parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")

# random
p1 = subparsers.add_parser("random")
p1.add_argument("--genre", required=True)
p1.set_defaults(func=cmd_random)

# mistakes
p2 = subparsers.add_parser("mistakes")
p2.add_argument("--genre", required=True)
p2.set_defaults(func=cmd_mistakes)

# confident
p3 = subparsers.add_parser("confident")
p3.add_argument("--genre", required=True)
p3.set_defaults(func=cmd_confident)


args = parser.parse_args()
args.func(args)