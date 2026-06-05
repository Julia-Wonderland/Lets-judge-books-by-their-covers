from pyspark.sql import SparkSession
from pyspark.sql.functions import rand

# 1. Spark session
spark = SparkSession.builder \
    .appName("GoodreadsTrainValTestSplit") \
    .getOrCreate()


# 2. Load processed dataset from HDFS
df = spark.read.parquet(
    "hdfs://namenode:9000/project/processed/clean_books"
)


# 3. (Optional but recommended) make split reproducible
# random column used for deterministic splitting
df = df.withColumn("rand", rand(seed=42))


# 4. Define splits
train_df = df.filter(col("rand") <= 0.8)
val_df   = df.filter((col("rand") > 0.8) & (col("rand") <= 0.9))
test_df  = df.filter(col("rand") > 0.9)


# 5. Drop helper column
train_df = train_df.drop("rand")
val_df   = val_df.drop("rand")
test_df  = test_df.drop("rand")


# 6. Write to HDFS
train_df.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/project/datasets/train"
)

val_df.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/project/datasets/val"
)

test_df.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/project/datasets/test"
)


spark.stop()