# Book Cover Analysis CLI

## Overview

This project provides a Spark-based command line interface for exploring a dataset of book covers, labels, predictions, embeddings, and recommendation results.

The application is located at:

```
/workspace/src/ui/app.py
```

Images are loaded from HDFS when available and automatically fall back to local storage when necessary.

---

## Starting the Environment

Start all services:

```
docker compose up -d
```

Verify that the containers are running:

```
docker ps
```

Enter the Spark master container:

```
docker exec -it spark-master bash
```

All commands below should be executed from inside the Spark master container.

---

## Running the Application

General syntax:

```
/opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    /workspace/src/ui/app.py <command> [arguments]
```

---

## Command: random

Returns a random book belonging to a selected genre.

Arguments:

```
--genre    Required genre name
--split    Optional dataset split
```

Available splits:

```
train
val
test
```

Example:

```
/opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    /workspace/src/ui/app.py \
    random \
    --genre Fantasy
```

Example with split filter:

```
/opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    /workspace/src/ui/app.py \
    random \
    --genre Fantasy \
    --split test
```

Output:

* Book information
* Ground truth labels
* Predicted labels
* Prediction probabilities
* Saved cover image

---

## Command: mistakes

Returns a random example where the model failed to predict a genre that is actually present.

Arguments:

```
--genre    Required genre name
--split    Optional dataset split
```

Example:

```
/opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    /workspace/src/ui/app.py \
    mistakes \
    --genre Romance
```

Example with split filter:

```
/opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    /workspace/src/ui/app.py \
    mistakes \
    --genre Romance \
    --split test
```

Output:

* Book information
* Ground truth labels
* Predicted labels
* Saved cover image
* Indication that the model missed the genre

---

## Command: confident

Returns the most confident correct prediction for a selected genre.

Arguments:

```
--genre    Required genre name
--split    Optional dataset split
```

Example:

```
/opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    /workspace/src/ui/app.py \
    confident \
    --genre Fantasy
```

Output:

* Book information
* Prediction probabilities
* Saved cover image
* Highest-confidence correctly classified example

---
## Available Genres

The following genres are supported by the:

```
random
mistakes
confident
```

Available genres:

```
Fiction
Audiobook
Romance
Fantasy
Adult
Contemporary
Mystery
Young Adult
Thriller
Historical Fiction
Novels
Adventure
Nonfiction
Classics
Mystery Thriller
Crime
Historical
Suspense
Paranormal
Science Fiction
Humor
Contemporary Romance
Chick Lit
Literature
Childrens
Adult Fiction
Magic
Science Fiction Fantasy
Urban Fantasy
```

When a genre name contains spaces, wrap it in quotes:

```
--genre "Historical Fiction"
--genre "Contemporary Romance"
--genre "Mystery Thriller"
--genre "Science Fiction Fantasy"
--genre "Young Adult"
```



## Command: recommend

Returns books with embeddings most similar to a selected book.

Similarity is computed using cosine similarity between embedding vectors.

Arguments:

```
--book-id     Required book identifier
--quantity    Number of recommendations to return
```

Example:

```
/opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    /workspace/src/ui/app.py \
    recommend \
    --book-id 10031.The_Wall \
    --quantity 5
```

Output:

* Query book image
* Top N recommended books
* Similarity score for each recommendation
* Saved images for all recommendations

---

## Image Output

Whenever an image is retrieved, it is saved to:

```
/workspace/output/
```

Examples:

```
/workspace/output/10031.The_Wall.jpg

/workspace/output/10897866-the-soulkeepers.jpg
```

The application first attempts to load images from HDFS:

```
hdfs://namenode:9000/project/images/raw/
```

If an image is unavailable in HDFS, a local copy is used from:

```
/workspace/images/
```

---

## Example Workflow

1. Start services:

   docker compose up -d

2. Enter Spark master:

   docker exec -it spark-master bash

3. Explore random fantasy books:

   /opt/spark/bin/spark-submit 
   --master spark://spark-master:7077 
   /workspace/src/ui/app.py 
   random 
   --genre Fantasy

4. Investigate model mistakes:

   /opt/spark/bin/spark-submit 
   --master spark://spark-master:7077 
   /workspace/src/ui/app.py 
   mistakes 
   --genre Fantasy

5. Find similar books:

   /opt/spark/bin/spark-submit 
   --master spark://spark-master:7077 
   /workspace/src/ui/app.py 
   recommend 
   --book-id 10031.The_Wall 
   --quantity 5
