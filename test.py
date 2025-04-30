import plotly.express as px
import pandas as pd

# --- 1) Create some dummy state‐level data ---
data = pd.DataFrame({
    "state_code": ["CA", "TX", "FL", "NY", "IL", "PA", "OH", "GA", "NC", "MI"],
    "active_cases": [1_200_000, 900_000, 750_000, 650_000, 500_000, 450_000, 400_000, 380_000, 360_000, 340_000]
})

# --- 2) Build a simple choropleth for the USA ---
fig = px.choropleth(
    data,
    locations="state_code",                 # 2‐letter state codes
    locationmode="USA-states",              # tells Plotly these are US states
    color="active_cases",                   # column to map to color
    color_continuous_scale="Reds",         # simple red color scale
    range_color=(300_000, 1_200_000),       # fix your color range
    scope="usa",
    title="Sample Active Cases by State"
)

# --- 3) Tidy up margins and layout ---
fig.update_layout(
    margin={"l":0, "r":0, "t":40, "b":0},
    coloraxis_colorbar=dict(
        title="Cases",
        ticksuffix="",
        showticksuffix="all"
    )
)

# To display in a notebook or script:
fig.show()

# (Optional) To export as a static image, uncomment below—
# you'll need kaleido installed (`pip install kaleido`):
# fig.write_image("us_active_cases_map.png", scale=2)
