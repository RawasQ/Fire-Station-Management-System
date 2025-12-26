import gradio as gr
import pandas as pd
import random
import matplotlib.pyplot as plt
from PIL import Image
import time
import folium
from folium.plugins import AntPath
from io import BytesIO

# -------------------------------
# Sample Data
# -------------------------------
vehicles = {
    "🚒 Fire Engine 1": ["Officer A", "Officer B", "Officer C"],
    "🚒 Fire Engine 2": ["Officer D", "Officer E"],
    "🚑 Rescue Van 1": ["Officer F", "Officer G"]
}

equipment_list = ["🧯 Fire Extinguisher", "💧 Water Hose", "🫁 Oxygen Cylinder", "✂ Hydraulic Cutter", "🧤 Protective Gear"]

incident_log = []

# -------------------------------
# AI Route Selection
# -------------------------------
def ai_route(severity):
    if severity=="High":
        return "🛣 Emergency Green Corridor", 12
    elif severity=="Medium":
        return "🛣 Traffic-Aware City Route", 18
    return "🛣 Normal Shortest Route", 25

# -------------------------------
# Generate Equipment Chart as PIL Image
# -------------------------------
def generate_equipment_chart(equipment_counts):
    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(equipment_counts.keys(), equipment_counts.values(), color="tomato")
    ax.set_title("🧰 Equipment Usage")
    ax.set_ylabel("Units Used")
    plt.xticks(rotation=15)
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img = Image.open(buf)
    plt.close(fig)
    return img

# -------------------------------
# Generate Water Consumption Chart
# -------------------------------
def generate_water_chart(log):
    df = pd.DataFrame(log)
    if df.empty:
        fig, ax = plt.subplots(figsize=(5,3))
        ax.text(0.5,0.5,"No Incidents Yet", ha="center", va="center")
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)
        return img
    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(df.index, df['Water Used (L)'], color="blue")
    ax.set_title("💧 Water Usage per Incident")
    ax.set_ylabel("Liters")
    ax.set_xlabel("Incident #")
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img = Image.open(buf)
    plt.close(fig)
    return img

# -------------------------------
# Generate Folium Map of Vehicle Movement
# -------------------------------
def generate_map(lat, lon):
    lat = float(lat)
    lon = float(lon)
    # Fire station is fixed location
    station_lat, station_lon = 12.9716, 77.5946
    m = folium.Map(location=[station_lat, station_lon], zoom_start=13)
    # Vehicle movement line
    AntPath(locations=[[station_lat, station_lon],[lat, lon]], color="red", weight=5).add_to(m)
    folium.Marker([station_lat, station_lon], tooltip="Fire Station", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([lat, lon], tooltip="Incident Location", icon=folium.Icon(color="red")).add_to(m)
    # Save map as html
    map_path = "/tmp/map.html"
    m.save(map_path)
    return map_path

# -------------------------------
# Dispatch Logic with Timeline
# -------------------------------
def dispatch_incident(incident_type, severity, latitude, longitude, equipment, water_used_liters):
    # Stage 1: Dispatched
    stage_msg = "🚨 Dispatched: Vehicle is on the way..."
    time.sleep(1)

    vehicle = random.choice(list(vehicles.keys()))
    officers = ", ".join(vehicles[vehicle])
    route, eta = ai_route(severity)

    equipment_count = {eq: random.randint(1,3) for eq in equipment}

    # Stage 2: On Scene
    stage_msg += "\n🟡 On Scene: Firefighters reached incident site..."
    time.sleep(1)

    # Save history
    record = {
        "Incident": incident_type,
        "Location": f"{latitude}, {longitude}",
        "Severity": severity,
        "Vehicle": vehicle,
        "Officers": officers,
        "Route": route,
        "ETA (min)": eta,
        "Equipment Used": ", ".join(equipment),
        "Water Used (L)": water_used_liters
    }
    incident_log.append(record)
    df = pd.DataFrame(incident_log)

    # Stage 3: Resolved
    stage_msg += "\n🟢 Resolved: Incident cleared successfully!"
    time.sleep(1)

    # Charts
    eq_chart = generate_equipment_chart(equipment_count)
    water_chart = generate_water_chart(incident_log)

    # Dispatch Report
    report = f"""
━━━━━━━━ 🚨 INCIDENT RESPONSE REPORT ━━━━━━━━

🔥 Incident Type : {incident_type}
📍 Location      : {latitude}, {longitude}
⚠ Severity      : {severity}

🚒 Vehicle       : {vehicle}
👨‍🚒 Officers    : {officers}

🛣 AI Route      : {route}
⏱ ETA           : {eta} minutes

🧰 Equipment Used:
{', '.join(equipment)}
💧 Water Used: {water_used_liters} Liters

🕒 Timeline:
{stage_msg}

✅ Status: INCIDENT SUCCESSFULLY RESOLVED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    map_path = generate_map(latitude, longitude)
    return report, df, eq_chart, water_chart, map_path

# -------------------------------
# UI/UX DESIGN
# -------------------------------
with gr.Blocks(title="🔥 Fire Station Command Center") as app:
    gr.Markdown("# 🚨 FIRE STATION COMMAND CENTER")
    gr.Markdown("### AI-Powered Emergency Dispatch & Visualization")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 📍 Incident Details")
            incident_type = gr.Textbox(label="Incident Type", placeholder="Building Fire / Road Accident")
            severity = gr.Radio(["Low","Medium","High"], label="Severity Level", value="Medium")
            latitude = gr.Textbox(label="Latitude", placeholder="12.9756")
            longitude = gr.Textbox(label="Longitude", placeholder="77.5950")
            water_used = gr.Number(label="Water Used (Liters)", value=500)
        with gr.Column(scale=1):
            gr.Markdown("## 🧰 Equipment Allocation")
            equipment = gr.CheckboxGroup(equipment_list, label="Select Equipment Used")

    dispatch_btn = gr.Button("🚨 DISPATCH RESPONSE UNIT", variant="primary")
    gr.Markdown("---")

    with gr.Row():
        report_box = gr.Textbox(label="📄 Dispatch Report", lines=14)
        history_table = gr.Dataframe(label="📊 Incident & Dispatch History", interactive=False)

    with gr.Row():
        eq_chart_img = gr.Image(label="📈 Equipment Usage Chart")
        water_chart_img = gr.Image(label="💧 Water Usage Trends")
        map_html = gr.HTML(label="🗺️ Vehicle Movement Map")

    dispatch_btn.click(
        dispatch_incident,
        inputs=[incident_type, severity, latitude, longitude, equipment, water_used],
        outputs=[report_box, history_table, eq_chart_img, water_chart_img, map_html]
    )

app.launch(share=True)
