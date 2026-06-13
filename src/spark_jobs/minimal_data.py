from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import ArrayType, IntegerType

spark = SparkSession.builder \
    .appName("GoodreadsDLFeatureExport") \
    .getOrCreate()


df = spark.read.parquet(
    "hdfs://namenode:9000/project/processed/books_ml_ready"
)

def vector_to_list(v):
    if v is None:
        return None
    return [int(x) for x in v.toArray()]

vector_to_list_udf = udf(vector_to_list, ArrayType(IntegerType()))

df_dl = df.select(
    col("id"),
    vector_to_list_udf(col("genre_vector")).alias("genre_vector")
)


df_dl = df_dl.dropna()

df_dl.write.mode("overwrite").parquet(
    "hdfs://namenode:9000/project/processed/ml_features_dl"
)

spark.stop()