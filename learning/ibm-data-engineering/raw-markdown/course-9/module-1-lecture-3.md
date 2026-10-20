# Module 1, lecture 3: selecting a data warehouse system

A warehouse choice affects data pipelines, BI tools, staffing, and budgets for years. Evaluate those costs and requirements before choosing a platform.

---

## 1. Evaluation criteria overview

Organizations assess data warehouse systems across five primary dimensions:

1. **Features and Capabilities**
2. **Compatibility and Implementation Considerations**
3. **Ease of Use and Skills**
4. **Support Considerations**
5. **Cost**

Weigh these trade-offs against the organization's operating requirements and plans.

---

## 2. Features and capabilities

### 2.1 Deployment location

Data warehouses can exist on-premises, on appliances, and across one or more cloud locations. The location decision is driven by a balance of competing demands:

- **Security-first organizations** may mandate an on-premises solution to retain full physical control over data.
- **Multi-location businesses** dealing with data privacy regulations such as **CCPA** or **GDPR** need either on-premises or geo-specific data warehouse placements.
- Each organization balances security and privacy requirements against the need for speed in delivering profit-producing business insights.

### 2.2 Architecture and structure

Key architectural questions an organization must resolve:

- Is the organization prepared to commit to a **vendor-specific architecture**?
- Does it require **multi-cloud installation**—multiple data warehouses across multiple locations?
- Does the solution **scale** to meet anticipated future growth?
- What **data types** does the organization ingest? Organizations analyzing **dark data** or planning to work with **semi-structured and unstructured data** need a system that supports these formats natively.
- Does the organization process **big data** requiring both **batch and streaming** ingestion?

### 2.3 Implementation capabilities

Implementation requirements include:

- **Data governance** frameworks
- **Data migration** tooling
- **Data transformation** capabilities
- The ability to **optimize and re-optimize** system performance as analytical needs evolve

### 2.4 Security and user management

Zero-trust security policies require user management and validation. Automated notifications and reports help teams detect errors and respond before they spread.

---

## 3. Ease of use and skills

The sophistication of a data warehouse platform is irrelevant if the team cannot operate it effectively. Key considerations:

- Does the organization's staff have the skills to implement the vendor's specific technology? If not, how quickly can they acquire them?
- For complex, large-scale deployments, the **implementation partner's expertise** is equally critical.
- Do the technology and engineering staff responsible for architecting, deploying, and administering front-end **querying, reporting, and visualization tools** have the proficiency to configure the new system rapidly?

---

## 4. Support considerations

Support planning is frequently underestimated and can become both frustrating and expensive if neglected:

- **Single-vendor accountability:** Using one vendor as a single, highly accountable source can save time, money, and frustration.
- **Service Level Agreements (SLAs):** Verify SLA coverage for uptime, security, scalability, and other system-critical concerns.
- **Support channels and hours:** Validate availability via phone, email, chat, and text.
- **Self-service and community:** Does the vendor offer self-service solutions and maintain an active user community?

---

## 5. Total cost of ownership (TCO)

Evaluating only the initial price tag is a common and costly mistake. The **Total Cost of Ownership (TCO)** across the system's operational lifetime includes:

| Cost Category                       | Description                                                                                          |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Infrastructure**                  | Compute and storage costs—whether on-premises hardware or cloud resource consumption.                |
| **Software Licensing**              | License fees for on-premises deployments, or subscription and usage-based costs for cloud offerings. |
| **Data Migration & Integration**    | Moving data into the warehouse, plus ongoing pruning and purging operations.                         |
| **Administration**                  | Personnel costs for managing the systems and ongoing training.                                       |
| **Recurring Support & Maintenance** | Fees paid to the warehousing vendor or implementation partner for continued operational support.     |

---

## 6. On-Premises vs. Public Cloud: the decision framework

The decision between on-premises and public cloud deployment reduces to a trade-off between **control** and **economics**:

- **On-premises** may be mandatory for organizations with strict data security and privacy requirements that preclude data leaving their physical infrastructure.
- **Public cloud** offers economies of scale—compute capacity, scalable storage, and flexible price-for-performance options—that are difficult to replicate in-house.

Some organizations combine these approaches in a hybrid configuration.

---
