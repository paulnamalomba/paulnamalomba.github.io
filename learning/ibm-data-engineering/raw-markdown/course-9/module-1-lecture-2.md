# Module 1, lecture 2: popular data warehouse systems

Choosing a data warehouse platform involves trade-offs in control, scalability, and operating costs. Appliances, cloud services, and hybrid deployments place different responsibilities on the team.

---

## 1. Deployment platform categories

Most data warehouse systems are delivered through one or more of three deployment models:

- **Appliances:** Pre-integrated bundles of hardware and software engineered for high-performance analytical workloads with minimal administration overhead.
- **Cloud-Only:** Fully managed services with cloud scaling and pay-per-use pricing—no infrastructure provisioning required.
- **On-Premises / Hybrid:** Traditionally installed within private data centers, though most vendors in this category now also offer cloud deployment options and hybrid configurations.

---

## 2. Appliance-Based systems

### 2.1 Oracle Exadata

Oracle Exadata can be deployed on-premises or via Oracle Public Cloud. It features built-in optimization algorithms and supports all major workload types: OLTP, data warehouse analytics, in-memory analytics, and mixed workloads.

### 2.2 IBM Netezza

IBM Netezza is deployable across IBM Cloud, AWS, Microsoft Azure, and private clouds via the IBM Cloud Pak for Data System. Netezza is widely recognized for its strong data science and machine learning enablement, making it a natural fit for organizations whose analytical workflows extend beyond traditional BI into predictive modelling.

---

## 3. Cloud-Native systems

### 3.1 Amazon Redshift

Amazon Redshift uses AWS-specific hardware and proprietary software to deliver accelerated data compression, encryption, machine learning, and graph-optimization algorithms that automatically organize and store data. It is tightly integrated into the broader AWS ecosystem.

### 3.2 Snowflake

Snowflake provides a multi-cloud analytics solution with strong data privacy compliance (GDPR, CCPA) and FedRAMP Moderate authorization. It advertises always-on encryption of data both in transit and at rest.

### 3.3 Google BigQuery

Google BigQuery markets itself as a "flexible, multi-cloud data warehouse solution" delivering:

- **99.99% uptime**
- **Sub-second query response** from any BI tool
- **Petabyte-scale speed** with high concurrency for real-time analytics

---

## 4. Hybrid On-Premises and Cloud systems

### 4.1 Microsoft Azure Synapse Analytics

Azure Synapse Analytics offers code-free visual ETL/ELT processes with over 95 native connectors for data ingestion. It supports both data lake and data warehouse use cases and enables development in T-SQL, Python, Scala, Spark SQL, and .NET across serverless and dedicated resource pools.

### 4.2 Teradata Vantage

Teradata Vantage takes a unified approach, advertising a multi-cloud data platform that brings together data lakes, data warehouses, analytics, and new data sources under a single umbrella. Key differentiators include:

- Combination of open-source and commercial technologies
- High query concurrency via workload management and adaptive optimization
- A single point of contact for operational support—monitoring, change requests, performance tuning, security management, and reporting

### 4.3 IBM Db2 Warehouse

IBM Db2 Warehouse is a **containerized, scale-out** data warehousing solution recognized for:

- **Massively parallel processing (MPP)** capabilities
- **Petaflop-level speeds**
- **99.99% service uptime**
- Workload portability across public cloud, private cloud, and on-premises environments with minimal or no code changes

### 4.4 Vertica

Vertica offers multi-cloud support across AWS, Google Cloud, Microsoft Azure, and on-premises Linux hardware. It reports fast multi-GB data transfer rates, elastic compute and storage scalability, and notable system fault tolerance when operating in Eon mode.

### 4.5 Oracle autonomous data warehouse

Oracle Autonomous Data Warehouse runs in **Oracle Public Cloud** and on-premises, supporting multi-model data and multiple workloads. Oracle describes the system as built to eliminate manual data management, with extensive automated security features:

- Autonomous data encryption at rest and in motion
- Protection of regulated data
- Automated security patch application
- Threat detection

---

## 5. Vendor landscape summary

| Category                     | Vendors                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------- |
| **Appliance**                | Oracle Exadata, IBM Netezza                                                                 |
| **Cloud-Native**             | Amazon Redshift, Snowflake, Google BigQuery                                                 |
| **Hybrid (On-Prem + Cloud)** | Microsoft Azure Synapse, Teradata Vantage, IBM Db2 Warehouse, Vertica, Oracle Autonomous DW |

---
