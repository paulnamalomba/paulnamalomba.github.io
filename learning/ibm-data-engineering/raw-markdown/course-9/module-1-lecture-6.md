# Module 1, lecture 6: data lakes overview

A data warehouse enforces a predefined schema when data is written. This suits BI workloads, but it can delay ingestion of heterogeneous data whose analytical uses are not yet known. A data lake stores data in its native format and applies structure when it is read for a particular use.

---

## 1. Defining the data lake

A data lake is a storage repository that can hold large amounts of structured, semi-structured, and unstructured data in their native format, classified and tagged with metadata. Each data element is assigned a unique identifier and tagged with metatags for downstream use.

Key distinctions from a data warehouse:

- **Schema-on-read** — you do not need to define the structure and schema of data before loading it into the data lake
- **Use-case agnostic** — you do not need to know all the analytical use cases at ingestion time
- **Raw data preservation** — data exists in its original form, straight from the source, and is transformed only when needed for a specific analytical task

A data lake is also a **reference architecture** that is independent of any specific technology. It can be deployed on:

- **Cloud object storage** — e.g., Amazon S3
- **Distributed systems** — e.g., Apache Hadoop for Big Data processing
- **Relational database management systems**
- **NoSQL data repositories** capable of storing very large data volumes

> A data lake is not a data dump. Governance, metadata management, and cataloguing are essential to prevent it from degrading into an unusable data swamp.

---

## 2. Benefits of a data lake

### 2.1 Universal data type support

Data lakes can store all data types without format conversion:

- **Unstructured data** — documents, emails, images, audio
- **Semi-structured data** — JSON, XML, CSV, log files
- **Structured data** — rows and columns from relational databases

### 2.2 Scalable storage capacity

Data lakes scale from terabytes to petabytes, accommodating the exponential growth of organizational data without capacity-related redesign.

### 2.3 Time savings

By retaining data in its original format, data lakes eliminate the upfront time investment required to define structures, create schemas, and transform data before loading—an overhead that is mandatory in traditional data warehousing.

### 2.4 Flexible data reuse

The ability to access data in its original format enables fast, flexible reuse across a wide range of **current and future use cases**—from exploratory analysis to machine learning feature engineering.

---

## 3. Data lake vendor landscape

Technologies, platforms, and reference architectures for data lakes are offered by:

| Vendor      | Vendor            |
| ----------- | ----------------- |
| Amazon      | Microsoft         |
| Cloudera    | Oracle            |
| Google      | SAS               |
| IBM         | Snowflake         |
| Informatica | Teradata / Zaloni |

---

## 4. Data lakes vs. Data warehouses

Data lakes were designed in response to the limitations of data warehouses. Most organizations require **both**, as they serve different needs.

| Dimension         | Data Lake                                                                               | Data Warehouse                                               |
| ----------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| **Data Format**   | Raw, unstructured, integrated in native form                                            | Processed, conformed to standards prior to loading           |
| **Schema**        | Schema-on-read — no schema required before loading                                      | Schema-on-write — strict conformance required before loading |
| **Data Quality**  | May contain uncurated, raw data; does not necessarily comply with governance guidelines | Curated, governed, and quality-controlled                    |
| **Primary Users** | Data scientists, data developers, ML engineers                                          | Business analysts, data analysts                             |
| **Staging Role**  | Often used as a staging area before loading into warehouses or data marts               | Final analytical destination for BI workloads                |

---

## 5. The data lake as a staging layer

Data lakes are frequently used as a **self-serve staging area** for a variety of downstream use cases:

- Machine learning model development and training
- Advanced analytics and exploratory data science
- Data transformation pipelines feeding enterprise data warehouses and data marts

A data lake can complement a data warehouse in the same architecture.

---
