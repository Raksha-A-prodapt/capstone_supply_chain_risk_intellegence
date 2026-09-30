"""
Synthetic Supply Chain Dataset Generator
Generates realistic, reproducible supply chain records (100,000 - 300,000 rows)
incorporating realistic supplier tiers, logistics delays, customs holds,
seasonal demand, inventory depletion, and controlled anomalies.
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set deterministic random seed
SEED = 42
np.random.seed(SEED)

def generate_dataset(num_records: int = 120_000, output_path: str = "data/dataset.csv") -> pd.DataFrame:
    print(f"Generating {num_records:,} synthetic supply chain records with seed {SEED}...")

    # 1. Define Suppliers with explicit risk profiles
    suppliers = [
        # (supplier_id, supplier_name, base_late_prob, base_lead_mean, base_lead_std, risk_tier)
        ("SUP-001", "Apex Precision Components", 0.05, 12, 1.5, "LOW"),
        ("SUP-002", "Nova Tech Microelectronics", 0.06, 14, 1.8, "LOW"),
        ("SUP-003", "AeroDynamics Materials", 0.08, 10, 1.2, "LOW"),
        ("SUP-004", "Vanguard Industrial Foundry", 0.07, 15, 2.0, "LOW"),
        ("SUP-005", "Summit Sensor Systems", 0.09, 11, 1.4, "LOW"),
        ("SUP-006", "Optima Polymers & Resins", 0.06, 8, 1.0, "LOW"),
        ("SUP-007", "Quantum Battery Solutions", 0.08, 16, 2.1, "LOW"),
        ("SUP-008", "Precision Gearworks LLC", 0.07, 13, 1.6, "LOW"),
        
        ("SUP-009", "Pinnacle Circuit Fabrication", 0.16, 18, 3.2, "MEDIUM"),
        ("SUP-010", "Matrix Fluid Power", 0.18, 14, 2.8, "MEDIUM"),
        ("SUP-011", "Titanium & Alloys Global", 0.19, 21, 3.5, "MEDIUM"),
        ("SUP-012", "Delta Wire & Cable", 0.15, 12, 2.4, "MEDIUM"),
        ("SUP-013", "Orion Optical Sensors", 0.20, 15, 3.0, "MEDIUM"),
        ("SUP-014", "Cascade Rubber & Seals", 0.17, 10, 2.2, "MEDIUM"),
        ("SUP-015", "Silverline Connectors", 0.18, 13, 2.6, "MEDIUM"),
        ("SUP-016", "Benchmark Motors & Drives", 0.21, 20, 3.8, "MEDIUM"),
        ("SUP-017", "Global Fastener Network", 0.16, 9, 2.0, "MEDIUM"),
        ("SUP-018", "Solstice Solar Cells", 0.22, 22, 4.0, "MEDIUM"),

        # High risk suppliers with chronic delays and anomalies
        ("SUP-019", "Pacific Rim Foundry Corp", 0.42, 26, 6.5, "HIGH"),
        ("SUP-020", "Continental Freight & Stamping", 0.45, 24, 5.8, "HIGH"),
        ("SUP-021", "Harborview Semis & Chips", 0.49, 30, 7.2, "CRITICAL"),
        ("SUP-022", "Atlas Rare Earth Metals", 0.40, 28, 6.0, "HIGH"),
        ("SUP-023", "RedStar Cargo & Microchips", 0.53, 32, 8.5, "CRITICAL"),
        ("SUP-024", "Starlight Chem & Solvents", 0.38, 19, 5.0, "HIGH"),
        ("SUP-025", "Borealis Extreme Composites", 0.46, 27, 6.8, "CRITICAL"),
    ]

    # 2. Define Products
    products = [
        ("PROD-001", "Microcontroller Unit MCU-32", 45.0, 0.2, "Fragile Sensitive"),
        ("PROD-002", "Lithium-Ion Battery Pack 48V", 210.0, 12.5, "Hazardous HazMat"),
        ("PROD-003", "Titanium Hex Bolt Set M8", 14.5, 3.2, "Ambient"),
        ("PROD-004", "Optical CMOS Image Sensor", 65.0, 0.15, "Fragile Sensitive"),
        ("PROD-005", "Brushless DC Motor 750W", 140.0, 5.4, "Ambient"),
        ("PROD-006", "Thermal Heat Pipe Assembly", 32.0, 0.8, "Ambient"),
        ("PROD-007", "Refrigerated Sealant Compound", 58.0, 2.0, "Cold Chain Refrigerated"),
        ("PROD-008", "Multilayer Ceramic Capacitor Reel", 18.0, 0.5, "Fragile Sensitive"),
        ("PROD-009", "Industrial Hydraulic Valve 350Bar", 320.0, 18.0, "Ambient"),
        ("PROD-010", "Polymer Electrolyte Membrane", 95.0, 0.4, "Cold Chain Refrigerated"),
        ("PROD-011", "Fiber Optic Transceiver 100G", 85.0, 0.3, "Fragile Sensitive"),
        ("PROD-012", "Alloy Drive Shaft 1200mm", 175.0, 22.0, "Ambient"),
        ("PROD-013", "Precision Pressure Sensor", 52.0, 0.35, "Fragile Sensitive"),
        ("PROD-014", "Silicone Thermal Conductive Paste", 24.0, 1.2, "Cold Chain Refrigerated"),
        ("PROD-015", "High-Torque Planetary Gearbox", 260.0, 14.0, "Ambient"),
        ("PROD-016", "Insulated Copper Busbar 400A", 42.0, 4.5, "Ambient"),
        ("PROD-017", "Power MOSFET Discrete Module", 38.0, 0.25, "Fragile Sensitive"),
        ("PROD-018", "Carbon Fiber Structural Strut", 130.0, 3.8, "Ambient"),
        ("PROD-019", "Automotive Radar Transceiver IC", 74.0, 0.2, "Fragile Sensitive"),
        ("PROD-020", "Industrial Grade Coolant Fluid", 48.0, 25.0, "Hazardous HazMat"),
        ("PROD-021", "Ceramic Insulator Bushing", 28.0, 2.8, "Fragile Sensitive"),
        ("PROD-022", "Stepper Motor Driver IC", 33.0, 0.1, "Fragile Sensitive"),
        ("PROD-023", "Neodymium Permanent Magnet Ring", 62.0, 1.5, "Ambient"),
        ("PROD-024", "Heavy-Duty Solenoid Actuator", 88.0, 6.2, "Ambient"),
        ("PROD-025", "Precision Linear Encoder", 190.0, 1.8, "Fragile Sensitive"),
        ("PROD-026", "Tungsten Carbide Milling Bit", 72.0, 1.1, "Ambient"),
        ("PROD-027", "Electrolytic Battery Electrolyte", 55.0, 20.0, "Hazardous HazMat"),
        ("PROD-028", "FPGA Accelerator Board", 420.0, 0.9, "Fragile Sensitive"),
        ("PROD-029", "Stainless Steel Flange DN50", 45.0, 8.5, "Ambient"),
        ("PROD-030", "Solid State Relay 100A", 64.0, 0.7, "Ambient"),
    ]

    # 3. Logistics routes & Hubs
    cities = [
        ("Shanghai", "Los Angeles", 10400),
        ("Shenzhen", "Chicago", 12300),
        ("Tokyo", "Hamburg", 9000),
        ("Busan", "Rotterdam", 10800),
        ("Taipei", "Dallas", 11900),
        ("Singapore", "Antwerp", 10500),
        ("Frankfurt", "Atlanta", 7400),
        ("Seoul", "Newark", 11000),
        ("Yokohama", "Seattle", 7800),
        ("Munich", "Toronto", 6500),
    ]

    carriers = ["DHL Global", "FedEx SupplyChain", "Maersk Logistics", "Kuehne+Nagel", "DB Schenker"]
    hubs = ["Hub-North", "Hub-South", "Hub-East", "Hub-West", "Hub-Central"]
    customs_procedures = ["Standard Clearance", "FastTrack Priority", "Inspection Hold", "Bonded Transit"]
    customs_weights = [0.70, 0.18, 0.07, 0.05]

    # Generate dates across 365 days (2024)
    start_date = datetime(2024, 1, 1)
    
    # Pre-select indices
    sup_indices = np.random.choice(len(suppliers), size=num_records)
    prod_indices = np.random.choice(len(products), size=num_records)
    city_indices = np.random.choice(len(cities), size=num_records)
    carrier_indices = np.random.choice(len(carriers), size=num_records)
    hub_indices = np.random.choice(len(hubs), size=num_records)
    customs_indices = np.random.choice(len(customs_procedures), size=num_records, p=customs_weights)

    day_offsets = np.random.randint(0, 365, size=num_records)
    order_dates = [start_date + timedelta(days=int(d)) for d in day_offsets]

    # Quantities ordered
    units_ordered = np.random.exponential(scale=180, size=num_records).astype(int) + 20
    units_ordered = np.clip(units_ordered, 20, 2500)

    # Product attributes
    prod_ids = [products[i][0] for i in prod_indices]
    prod_names = [products[i][1] for i in prod_indices]
    unit_costs = [products[i][2] for i in prod_indices]
    unit_weights = [products[i][3] for i in prod_indices]
    material_handlings = [products[i][4] for i in prod_indices]
    total_weights = np.round(units_ordered * np.array(unit_weights), 2)

    # Supplier attributes
    sup_ids = [suppliers[i][0] for i in sup_indices]
    sup_names = [suppliers[i][1] for i in sup_indices]
    base_late_probs = np.array([suppliers[i][2] for i in sup_indices])
    base_lead_means = np.array([suppliers[i][3] for i in sup_indices])
    base_lead_stds = np.array([suppliers[i][4] for i in sup_indices])

    # Logistics routes
    origin_cities = [cities[i][0] for i in city_indices]
    dest_cities = [cities[i][1] for i in city_indices]
    distances = np.array([cities[i][2] for i in city_indices])
    carrier_names = [carriers[i] for i in carrier_indices]
    hub_names = [hubs[i] for i in hub_indices]
    customs_procs = [customs_procedures[i] for i in customs_indices]

    # Calculate Expected Lead Time based on supplier base lead time and distance
    distance_factor = (distances / 10000.0) * 2.0
    expected_lead_times = np.round(base_lead_means + distance_factor).astype(int)
    expected_lead_times = np.clip(expected_lead_times, 5, 45)

    # Compute actual lead time and delay probability modifiers
    # Customs Inspection Hold adds 4-10 days delay and high late probability
    customs_delay_mult = np.where(np.array(customs_procs) == "Inspection Hold", 1.8, 1.0)
    # Cold chain / hazardous handling adds slight variability
    handling_delay_mult = np.where(np.array(material_handlings) == "Cold Chain Refrigerated", 1.25, 1.0)
    handling_delay_mult = np.where(np.array(material_handlings) == "Hazardous HazMat", 1.30, handling_delay_mult)

    # Distance modifier
    dist_mult = 1.0 + (distances - 6500) / 25000.0

    # Adjusted late probability
    effective_late_probs = np.clip(base_late_probs * customs_delay_mult * handling_delay_mult * dist_mult, 0.02, 0.92)

    # Determine late_order binary flag
    random_draws = np.random.uniform(0.0, 1.0, size=num_records)
    late_order = (random_draws < effective_late_probs).astype(int)

    # Calculate actual delay days
    delay_days = np.zeros(num_records, dtype=int)
    late_mask = (late_order == 1)
    
    # Delay days follow gamma/exponential distribution
    raw_delays = np.random.exponential(scale=4.5, size=num_records) + 1.0
    # Additional delay if Inspection Hold
    raw_delays += np.where(np.array(customs_procs) == "Inspection Hold", np.random.uniform(4.0, 9.0, size=num_records), 0.0)
    # Extra delay for critical suppliers
    is_critical_sup = np.isin(sup_ids, ["SUP-021", "SUP-023", "SUP-025"])
    raw_delays += np.where(is_critical_sup, np.random.uniform(2.0, 6.0, size=num_records), 0.0)

    delay_days[late_mask] = np.round(raw_delays[late_mask]).astype(int)
    delay_days = np.clip(delay_days, 0, 45)

    # Controlled Lead-time Anomalies injection:
    # Inject extreme lead time spikes for SUP-023 in July/August (Port disruption scenario)
    # Inject volume spike anomalies for PROD-005
    for idx in range(num_records):
        odt = order_dates[idx]
        if sup_ids[idx] == "SUP-023" and 7 <= odt.month <= 8 and np.random.rand() < 0.35:
            late_order[idx] = 1
            delay_days[idx] = np.random.randint(18, 35)  # Severe lead time anomaly
        if prod_ids[idx] == "PROD-005" and odt.month in [10, 11] and np.random.rand() < 0.15:
            units_ordered[idx] = int(units_ordered[idx] * np.random.uniform(3.5, 6.0))  # Demand surge anomaly

    actual_lead_times = expected_lead_times + delay_days

    # Units received (some orders have partial shipments if delayed or damaged)
    units_received = units_ordered.copy()
    partial_mask = late_mask & (np.random.rand(num_records) < 0.22)
    units_received[partial_mask] = np.round(units_ordered[partial_mask] * np.random.uniform(0.60, 0.95, size=np.sum(partial_mask))).astype(int)

    # Compute dates
    expected_delivery_dates = [order_dates[i] + timedelta(days=int(expected_lead_times[i])) for i in range(num_records)]
    actual_delivery_dates = [order_dates[i] + timedelta(days=int(actual_lead_times[i])) for i in range(num_records)]

    # Product demand dynamics:
    # Baseline product demand + seasonal variation (monthly sine wave) + noise
    month_array = np.array([d.month for d in order_dates])
    seasonal_factors = 1.0 + 0.35 * np.sin((month_array - 3) * (2 * np.pi / 12)) + (month_array >= 10) * 0.25
    base_demands = np.random.poisson(lam=120, size=num_records)
    demands = np.round(base_demands * seasonal_factors).astype(int)
    demands = np.clip(demands, 15, 600)

    # Realistic Inventory levels and Reorder Points
    # Reorder point = (Avg daily demand * avg lead time) + Safety stock
    avg_daily_demand = demands / 30.0
    safety_stocks = np.round(1.65 * np.sqrt(expected_lead_times) * 15.0).astype(int)
    reorder_points = np.round(avg_daily_demand * expected_lead_times + safety_stocks).astype(int)
    reorder_points = np.clip(reorder_points, 50, 1500)

    # Inventory levels: depleted by demand, replenished by received units
    # Problematic suppliers result in inventory levels dipping below reorder points!
    inventory_levels = np.round(reorder_points * np.random.uniform(0.3, 1.8, size=num_records)).astype(int)
    # If severe delay, inventory is heavily depleted
    inventory_levels = np.where(delay_days > 7, np.maximum(5, inventory_levels - delay_days * 18), inventory_levels)
    inventory_levels = np.clip(inventory_levels, 0, 3000)

    # Format Order IDs
    order_ids = [f"ORD-{i+1:06d}" for i in range(num_records)]

    # Build DataFrame
    df = pd.DataFrame({
        "order_id": order_ids,
        "supplier_id": sup_ids,
        "supplier_name": sup_names,
        "product_id": prod_ids,
        "product_name": prod_names,
        "order_date": [d.strftime("%Y-%m-%d") for d in order_dates],
        "expected_delivery_date": [d.strftime("%Y-%m-%d") for d in expected_delivery_dates],
        "actual_delivery_date": [d.strftime("%Y-%m-%d") for d in actual_delivery_dates],
        "units_ordered": units_ordered,
        "units_received": units_received,
        "unit_cost": np.round(unit_costs, 2),
        "inventory_level": inventory_levels,
        "reorder_point": reorder_points,
        "demand": demands,
        "origin_city": origin_cities,
        "destination_city": dest_cities,
        "distance_km": distances,
        "carrier_3pl": carrier_names,
        "logistics_hub": hub_names,
        "customs_procedure": customs_procs,
        "material_handling": material_handlings,
        "weight": total_weights,
        "lead_time_days": actual_lead_times,
        "late_order": late_order,
        "delay_days": delay_days
    })

    # Sort deterministically by order_date and order_id
    df = df.sort_values(by=["order_date", "order_id"]).reset_index(drop=True)

    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset successfully generated and saved to {output_path}!")
    print(f"Shape: {df.shape}")
    print(f"Late order rate: {df['late_order'].mean():.2%}")
    print(f"Average delay days when late: {df[df['late_order'] == 1]['delay_days'].mean():.1f} days")
    print(f"Top late rate suppliers:\n{df.groupby('supplier_id')['late_order'].mean().sort_values(ascending=False).head(5)}")

    return df

if __name__ == "__main__":
    count = 120_000
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    generate_dataset(count)
