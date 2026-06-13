from pyspark.sql import SparkSession
from pyspark.sql.functions import rand

spark = SparkSession.builder \
    .appName("GoodreadsTrainValTestSplit") \
    .getOrCreate()


df = spark.read.parquet(
    "hdfs://namenode:9000/project/processed/clean_books"
)



df = df.withColumn("rand", rand(seed=42))


train_df = df.filter(col("rand") <= 0.8)
val_df   = df.filter((col("rand") > 0.8) & (col("rand") <= 0.9))
test_df  = df.filter(col("rand") > 0.9)



train_df = train_df.drop("rand")
val_df   = val_df.drop("rand")
test_df  = test_df.drop("rand")


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