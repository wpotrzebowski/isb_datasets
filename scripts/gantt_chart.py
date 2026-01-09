import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib.colors as mcolors

# -------------------------------------------------------------------
# Define tasks and their time windows (approximate quarters of 2026)
# -------------------------------------------------------------------
tasks = [
    # Q1 – Prototype → MVP foundation
    {
        "name": "Tidy prototype",
        "start": datetime(2026, 1, 1),
        "end":   datetime(2026, 3, 31),
    },
    {
        "name": "Define scope & metadata",
        "start": datetime(2026, 1, 15),
        "end":   datetime(2026, 3, 31),
    },
    {
        "name": "Create/improve system template",
        "start": datetime(2026, 2, 1),
        "end":   datetime(2026, 3, 31),
    },

    # Q2 – MVP catalogue + hosting
    {
        "name": "Populate with additional 5–10 systems",
        "start": datetime(2026, 4, 1),
        "end":   datetime(2026, 6, 30),
    },
    {
        "name": "Short-/long-term hosting decision",
        "start": datetime(2026, 5, 1),
        "end":   datetime(2026, 6, 15),
    },

    # Q3 – Internal review, annotations, data model
    {
        "name": "Internal ISB review",
        "start": datetime(2026, 7, 1),
        "end":   datetime(2026, 9, 30),
    },
    {
        "name": "Core manual annotations",
        "start": datetime(2026, 7, 15),
        "end":   datetime(2026, 9, 30),
    },
    {
        "name": "Data model draft",
        "start": datetime(2026, 8, 1),
        "end":   datetime(2026, 9, 30),
    },
    {
        "name": "mmCIF w/o model exploration",
        "start": datetime(2026, 8, 1),
        "end":   datetime(2026, 9, 30),
    },
    {
        "name": "Pilot workflows (1–2 systems)",
        "start": datetime(2026, 9, 1),
        "end":   datetime(2026, 10, 31),
    },
    {
        "name": "Repo structure & basic CI",
        "start": datetime(2026, 9, 1),
        "end":   datetime(2026, 9, 30),
    },

    # Q4 – Integration & sustainability
    {
        "name": "OpenBIS/log mapping (conceptual + links)",
        "start": datetime(2026, 10, 1),
        "end":   datetime(2026, 11, 15),
    },
    {
        "name": "Governance & contribution model",
        "start": datetime(2026, 10, 15),
        "end":   datetime(2026, 11, 30),
    },
    {
        "name": "Portal integration & docs",
        "start": datetime(2026, 11, 1),
        "end":   datetime(2026, 12, 31),
    },
    {
        "name": "Buffer / stretch goals",
        "start": datetime(2026, 12, 1),
        "end":   datetime(2026, 12, 31),
    },
]

# -------------------------------------------------------------------
# Generate variants of the SciLifeLab teal #045C64
# by blending with white (lighter tints)
# -------------------------------------------------------------------
base_color = "#045C64"

def blend_with_white(color, factor):
    """
    factor = 1.0 -> original color
    factor = 0.0 -> white
    """
    r, g, b = mcolors.to_rgb(color)
    r = 1 - (1 - r) * factor
    g = 1 - (1 - g) * factor
    b = 1 - (1 - b) * factor
    return (r, g, b)

# A few tints, all variants of #045C64
factors = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
color_variants = [blend_with_white(base_color, f) for f in factors]

# -------------------------------------------------------------------
# Build Gantt chart
# -------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 7))

for i, task in enumerate(tasks):
    start_num = mdates.date2num(task["start"])
    end_num = mdates.date2num(task["end"])
    duration = end_num - start_num

    color = color_variants[i % len(color_variants)]

    ax.barh(
        y=i,
        width=duration,
        left=start_num,
        align="center",
        color=color,
        edgecolor="black",
        linewidth=0.5,
    )

# Y-axis: task labels
ax.set_yticks(range(len(tasks)))
ax.set_yticklabels([t["name"] for t in tasks])
ax.invert_yaxis()  # First task at top

# X-axis: time over 2026
ax.xaxis_date()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  # Jan, Feb, ...
ax.set_xlim([datetime(2026, 1, 1), datetime(2026, 12, 31)])

ax.set_xlabel("2026")
ax.set_title("ISB Multimodal Datasets – 2026 Roadmap (20% FTE)")

plt.tight_layout()
plt.savefig("isb_gantt_2026.png", dpi=300)
plt.show()

print("Saved Gantt chart as isb_gantt_2026.png")

