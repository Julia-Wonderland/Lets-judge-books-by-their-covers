# Let's Judge Books by Their Covers

## Abstract

Can a book's genre be inferred from its cover alone?

This project investigates the relationship between visual design and literary genre through large-scale image classification. Using a dataset derived from Goodreads book metadata and cover images, a deep convolutional neural network was trained to perform multi-label genre prediction from book covers. Beyond classification performance, the project explores model interpretability through Grad-CAM visualizations and provides tools for qualitative inspection of predictions and learned visual representations.

The project combines distributed data processing with Apache Spark, deep learning using EfficientNet, explainability techniques, and a lightweight exploration interface built on top of the resulting dataset.

The title is inspired by the paper *"Judging a Book By its Cover"* by Iwana et al. (2016), which demonstrated that deep neural networks can learn meaningful genre-related visual patterns from book cover designs.

---

## Motivation

Book covers serve both artistic and commercial purposes. Designers intentionally employ visual conventions—such as typography, color palettes, imagery, and composition—to communicate genre and target audience.

While humans routinely make assumptions about books based on their covers, this project investigates whether those same signals can be learned automatically by modern computer vision models.

The project was designed around three questions:

1. Can a CNN accurately predict genres from cover images alone?
2. What visual features drive those predictions?
3. Do learned image embeddings capture meaningful similarities between books?

---

## Dataset Construction

The project uses a Goodreads-derived collection of book metadata and cover images.

### Data Acquisition

The original dataset contains:

* Book metadata
* Goodreads genre information
* Cover image URLs
* Additional descriptive attributes

### Data Processing

The raw data required substantial preprocessing before model training.

Apache Spark was used to perform large-scale processing tasks, including:

* Cleaning and filtering records
* Genre normalization
* Multi-label target construction
* Removal of incomplete entries
* Image validation
* Dataset splitting
* Feature aggregation

The resulting dataset contains cover images paired with multi-label genre annotations.

### Genre Space

The final label set consists of 29 genres:

* Fiction
* Audiobook
* Romance
* Fantasy
* Adult
* Contemporary
* Mystery
* Young Adult
* Thriller
* Historical Fiction
* Novels
* Adventure
* Nonfiction
* Classics
* Mystery Thriller
* Crime
* Historical
* Suspense
* Paranormal
* Science Fiction
* Humor
* Contemporary Romance
* Chick Lit
* Literature
* Childrens
* Adult Fiction
* Magic
* Science Fiction Fantasy
* Urban Fantasy

Because books frequently belong to multiple genres simultaneously, the task is formulated as a multi-label classification problem.

---

## Model Architecture

The classification model is based on EfficientNet.

### Why EfficientNet?

EfficientNet provides a strong balance between:

* Accuracy
* Computational efficiency
* Transfer learning performance

Pretrained ImageNet weights were used as initialization, allowing the model to leverage previously learned visual representations.

### Multi-Label Classification

Unlike standard single-label classification, each book may belong to multiple genres.

The model therefore predicts a probability for each genre independently using sigmoid activations and binary cross-entropy style objectives.

The output for each book is a vector of genre probabilities rather than a single predicted class.

---

## Explainability

To better understand model behavior, Grad-CAM was used to generate visual explanations of predictions.

Grad-CAM highlights image regions that contribute most strongly to a model's decision, allowing qualitative analysis of:

* Genre-specific design patterns
* Typography usage
* Color schemes
* Illustrations and artwork
* Potential dataset biases

These visualizations provide insight into whether the model is focusing on meaningful cover elements or exploiting spurious correlations.

---

## Embedding Analysis

In addition to genre predictions, image embeddings were extracted from the trained model.

These embeddings capture high-level visual characteristics of book covers and enable similarity search.

Applications include:

* Book recommendation
* Nearest-neighbor retrieval
* Visual clustering
* Exploration of learned feature spaces

Cosine similarity between embeddings is used to identify visually related books.

---

## Distributed Data Platform

The project was designed around a distributed data workflow.

### Technologies

* Apache Spark
* Hadoop HDFS
* Docker
* PySpark

HDFS serves as the central storage layer for:

* Processed datasets
* Cover images
* Model outputs
* Analysis artifacts

Spark jobs are used throughout the preprocessing and aggregation pipeline, enabling scalable handling of large image and metadata collections.

---

## Result Dataset

Model outputs are written back into Hadoop as a consolidated analysis dataset.

For each book, the dataset stores:

* Book identifier
* Dataset split
* Ground-truth labels
* Predicted labels
* Genre probabilities
* Learned embeddings

This final dataset acts as the primary source for downstream analysis and exploration.

---

## Interactive Exploration

A lightweight Spark-based interface is included for qualitative inspection of results.

The interface supports:

* Random sample exploration
* Error analysis
* High-confidence prediction inspection
* Embedding-based recommendations
* Cover image retrieval from HDFS

Detailed usage instructions can be found in:

```
src/ui/instructions.md
```

---

## Repository Structure

```
data/
    Raw and intermediate datasets

src/
    Data processing and model code

src/ui/
    Exploration interface

models/
    models saved with .pth extention

```

---

## Future Work

Potential extensions include:

* CLIP-based multimodal models
* Joint image-text genre prediction
* Transformer-based vision architectures
* Interactive Grad-CAM visualization
* Approximate nearest-neighbor search for large-scale recommendations
* Human evaluation of recommendation quality

---

## Reference

Iwana, B. K., Rizvi, S. T. R., Ahmed, S., Dengel, A., & Uchida, S. (2016).

*Judging a Book By its Cover.*

https://arxiv.org/abs/1610.09204

