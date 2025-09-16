# 📄 Product Requirement Document (PRD)

## 1. Problem Statement
Cloud spending data is large, complex, and fragmented. Finance and engineering teams often struggle to:
- Understand **where money is being spent**.
- Get **real-time insights** into cost trends.
- Translate raw data into **actionable recommendations** without deep BI/SQL expertise.

This project provides an **AI-native analytics copilot** that ingests spend data, surfaces KPIs, and allows natural-language Q&A for quick, actionable insights.

---

## 2. Target Users
- **FinOps / Finance Teams** → Need visibility into monthly cloud spend and saving opportunities.
- **Engineering Managers** → Track cost vs. usage across services, projects, and environments.
- **Executives / Business Stakeholders** → Require high-level summaries and explanations in plain English.

---

## 3. Top Use Cases
1. **KPI Dashboard** → View total spend, breakdown by service/resource group, and multi-month trends.
2. **Natural-Language Queries** → Ask questions like “Which service had the highest cost in August?” or “Why did my Azure spend increase in May?”
3. **Cost Optimization Suggestions** → Identify idle/underutilized resources and estimate potential savings.
4. **Historical Spend Exploration** → Compare monthly spend across regions, services, and accounts.
5. **Reporting** → Export summaries with charts/tables for stakeholder sharing.

---

## 4. Success Metrics
- **Time to Insight** → Reduce analysis time by at least **70%** compared to manual Excel/SQL analysis.
- **Accuracy** → ≥ **85% correct responses** to benchmarked test questions (evaluation set).
- **Adoption** → At least **3 user personas** (finance, engineering, business) find value in the tool.
- **Engagement** → Average user session length > **5 minutes**, with repeated Q&A and dashboard use.
- **Deployability** → Runs fully in Docker with setup time < **5 minutes**.

