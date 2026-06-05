from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import CountVectorizer

spark = SparkSession.builder \
    .appName("GoodreadsFeatureEngineering") \
    .getOrCreate()

# -------------------------
# 1. LOAD DATA
# -------------------------
df = spark.read.parquet(
    "hdfs://namenode:9000/project/raw/26_29_dataset.parquet"
)

df.coalesce(1).write.mode("overwrite").parquet(
    "hdfs://namenode:9000/project/processed/zero_stage_clean"
)

# -------------------------
# 2. BASIC CLEANING
# -------------------------
df_clean = df \
    .filter(F.col("genres").isNotNull()) \
    #.filter(F.col("genres") != "[]") \
    #.filter(F.col("num_ratings").isNotNull()) \
    #.filter(F.col("num_reviews").isNotNull()) \
    #.filter(F.col("num_ratings") > 7500)

df_clean.coalesce(1).write.mode("overwrite").parquet(
    "hdfs://namenode:9000/project/processed/first_stage_clean"
)

# -------------------------
# 3. STRING -> ARRAY CLEANING
# -------------------------
df_clean = df_clean.withColumn(
    "genres_array",
    F.split(
        F.regexp_replace(F.col("genres"), r'[\[\]"]', ""),
        ","
    )
)

df_clean = df_clean.withColumn(
    "genres_array",
    F.expr("transform(genres_array, x -> trim(x))")
)

# -------------------------
# 4. FILTER RARE GENRES (Spark-native, no collect hacks)
# -------------------------
genre_counts = df_clean \
    .select(F.explode("genres_array").alias("genre")) \
    .groupBy("genre") \
    .count()

MIN_COUNT = 2000

common_genres_df = genre_counts \
    .filter(F.col("count") >= MIN_COUNT) \
    .select("genre")

# Convert to broadcast set (safe + scalable)
common_genres_list = [r["genre"] for r in common_genres_df.collect()]
common_genres_broadcast = spark.sparkContext.broadcast(set(common_genres_list))

# -------------------------
# 5. FILTER GENRES USING PYTHON UDF-FREE EXPRESSION
# -------------------------
df_clean = df_clean.withColumn(
    "genres_filtered",
    F.expr("""
        filter(
            genres_array,
            x -> array_contains(array({}), x)
        )
    """
    .format(
        ",".join([f"'{g}'" for g in common_genres_list])
    ))
)

# -------------------------
# 6. MULTI-HOT ENCODING (EXPLICIT COLUMNS)
# -------------------------
for genre in common_genres_list:
    col_name = "genre_" + genre.replace(" ", "_").replace("-", "_")

    df_clean = df_clean.withColumn(
        col_name,
        F.when(F.array_contains("genres_filtered", genre), 1).otherwise(0)
    )

# -------------------------
# 7. VECTOR ENCODING (BEST FOR DL / ML MODELS)
# -------------------------
cv = CountVectorizer(
    inputCol="genres_filtered",
    outputCol="genre_vector",
    binary=True,
    vocabSize=5000
)

cv_model = cv.fit(df_clean)
df_final = cv_model.transform(df_clean)

# -------------------------
# 8. SAVE OUTPUT
# -------------------------
df_final.coalesce(1).write.mode("overwrite").parquet(
    "hdfs://namenode:9000/project/processed/books_ml_ready"
)

spark.createDataFrame(
    [(g,) for g in common_genres_list],
    ["genre"]
).coalesce(1).write.mode("overwrite").parquet(
    "hdfs://namenode:9000/project/processed/genre_vocab"
)

spark.stop()