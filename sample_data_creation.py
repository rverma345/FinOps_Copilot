# generate_sample_data.py
import pandas as pd
import numpy as np
import random
import json
from datetime import datetime

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

# Parameters
months = pd.date_range("2025-01-01", periods=6, freq="MS").strftime("%Y-%m").tolist()
services = ["Virtual Machines", "Storage", "SQL Database", "App Service", "Kubernetes", "Networking"]
regions = ["eastus", "westus", "centralus", "northeurope", "southeastasia"]
owners = ["Alice", "Bob", "Charlie", "Diana", "Eve", None]  # some missing tags
envs = ["dev", "test", "prod"]

# Billing data
billing_rows = []
resources_rows = []
resource_counter = 1

for month in months:
    for _ in range(200):  # ~200 resources/month → ~1200 rows
        account_id = f"acc-{random.randint(1000, 9999)}"
        subscription = f"sub-{random.randint(1,5)}"
        service = random.choice(services)
        resource_group = f"rg-{random.randint(1,10)}"
        resource_id = f"res-{resource_counter}"
        resource_counter += 1
        region = random.choice(regions)
        usage_qty = round(np.random.exponential(scale=50), 2)
        unit_cost = round(random.uniform(0.1, 2.0), 2)
        cost = round(usage_qty * unit_cost, 2)

        billing_rows.append([
            month, account_id, subscription, service, resource_group,
            resource_id, region, usage_qty, unit_cost, cost
        ])

        # Add resource metadata (some with missing owner)
        resources_rows.append([
            resource_id,
            random.choice(owners),
            random.choice(envs),
            json.dumps({"project": f"proj-{random.randint(1,5)}"})
        ])

# Create DataFrames
billing_df = pd.DataFrame(billing_rows, columns=[
    "invoice_month", "account_id", "subscription", "service", "resource_group",
    "resource_id", "region", "usage_qty", "unit_cost", "cost"
])

resources_df = pd.DataFrame(resources_rows, columns=[
    "resource_id", "owner", "env", "tags_json"
])

# Save to CSV
billing_df.to_csv("data/billing.csv", index=False)
resources_df.to_csv("data/resource_metadata.csv", index=False)

print("✅ Sample datasets generated: data/billing.csv & data/resources.csv")
