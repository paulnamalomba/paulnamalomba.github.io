# Module 1, lecture 1: data warehouse overview

Data warehouses bring together inconsistent data from operational systems so it can be analyzed in one place. They provide a common structure for data that would otherwise remain scattered across those systems.

---

## 1. Defining the data warehouse

A **data warehouse** is a system that aggregates data from one or more sources into a single, central, consistent data store to support various data analytics requirements.

Transactional databases are optimized for write-heavy operational workloads. Data warehouses support analytical reads across millions of historical transactions.

### 1.1 Core analytics capabilities

A data warehouse supports several analytical workloads:

- **OLAP (Online Analytical Processing):** Provides fast, flexible, multidimensional data analysis for business intelligence and decision support applications. Analysts can slice and dice metrics across time, geography, product line, and customer segment simultaneously.
- **ETL-Accelerated Reporting:** Data transformation during the Extract, Transform, Load process speeds front-end reporting delivery. Critical business metrics reach dashboards faster because the heavy computation has already been done at ingestion time.
- **AI and Machine Learning:** Data warehouses expose the historical depth and breadth of organizational data to machine learning pipelines—enabling predictive modelling, anomaly detection, and recommendation engines.
- **Data Mining:** Statistical and pattern-discovery workloads run against the warehouse to surface non-obvious correlations that would be invisible in any single operational system.

---

## 2. The evolution of data warehouse infrastructure

Data warehouse infrastructure has changed substantially across three distinct eras, each driven by the scale of data being generated.

### 2.1 On-Premises era

Traditionally, organizations hosted data warehouses in their own data centers, first on mainframes and later on Unix, Windows, and Linux servers. They owned the hardware and managed the software stack in-house.

### 2.2 The appliance era

As data volumes surged in the 2000s, **data warehouse appliances** emerged. These were pre-integrated bundles of specialized hardware and optimized warehousing software, shipped as a single unit. The appliance model reduced the management overhead of large-scale data warehousing by collapsing hardware provisioning and software tuning into a single vendor-managed layer.

### 2.3 Cloud data warehouses (CDWs)

Cloud data warehouses (CDWs) have become a common deployment model as cloud-generated data has grown. Organizations access scalable, pay-as-you-go services instead of buying hardware and installing warehouse software, reducing the initial capital investment.

---

## 3. Industry use cases

Data warehouses are pervasive across virtually every sector of the economy. The common thread is the need to analyze large volumes of historical data to support decisions that would otherwise be based on intuition alone.

| Industry                           | Primary Analytical Application                                                                                               |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Retail & E-Commerce**            | Sales performance analysis; ML-assisted product recommendation engines that drive cross-sell and upsell revenue.             |
| **Healthcare**                     | AI-driven patient data analysis to enable more accurate diagnosis and treatment decisions at the point of care.              |
| **Transportation & Logistics**     | Route optimization, travel time modelling, equipment utilization forecasting, and staffing requirement projections.          |
| **Financial Technology & Banking** | Risk evaluation, real-time fraud detection, and cross-sell analytics applied to transaction histories.                       |
| **Social Media**                   | High-velocity sentiment analysis measuring ever-changing customer opinion and projecting downstream impact on product sales. |
| **Government**                     | Business intelligence applied to citizen-facing programs, enabling evidence-based policy evaluation and change decisions.    |

---

## 4. The business case: benefits of a data warehouse

A data warehouse supports these operational and analytical needs:

### 4.1 Centralization and data quality

Data warehouses consolidate transactional systems, operational databases, and flat files in one location. Integration removes bad records and duplicates and standardizes schemas, giving analytical consumers a shared source of data.

### 4.2 Performance and accessibility

Separating operational writes from analytical reads generally improves both workloads. Operational databases avoid the load of analytical queries, while analysts gain faster, more predictable access to historical data.

### 4.3 Advanced intelligence capabilities

With a clean, centralized, and performant data store in place, large-scale BI functions become viable: data mining, AI model training, and machine learning inference pipelines can all operate against the same authoritative dataset. These capabilities build on each other, supporting more complex analytical work.

### 4.4 Competitive advantage

Better data quality and faster analysis help organizations identify opportunities and act on them. The commercial value depends on how the resulting information informs decisions.

---
