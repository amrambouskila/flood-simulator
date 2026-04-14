#!/usr/bin/env python3
"""
Flood-Adjusted Radiometric Dating Simulator
Interactive Streamlit app demonstrating how a global catastrophic flood
would affect ALL radiometric dating methods — from C-14 (thousands of years)
to U-Pb (billions of years).

Run with: streamlit run app.py
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

from models import (
    FloodAdjustedModel, StandardModel, CARBON_14_HALF_LIFE, LAMBDA,
    CURRENT_YEAR, FLOOD_YEAR, YEARS_SINCE_FLOOD,
    LongAgeRadiometricSuite, ISOTOPE_SYSTEMS, format_age,
)

st.set_page_config(
    page_title="Flood-Adjusted Radiometric Dating Simulator",
    page_icon="",
    layout="wide",
)

# ── Header ──────────────────────────────────────────────────────────────────

st.title("Flood-Adjusted Radiometric Dating Simulator")
st.markdown(
    "Radiometric dating assumes decay rates have **always** been constant and "
    "initial conditions are **fully known**. Adjust the sliders to model how "
    "a catastrophic global flood -- as described in the Torah -- shifts the "
    "numbers from 5,787 years to 4.5 billion."
)

# ══════════════════════════════════════════════════════════════════════════════
#                              SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

# ── Long-Age Radiometric Dating (top of sidebar — this is the headline) ────

st.sidebar.header("Long-Age Radiometric Dating")
st.sidebar.caption(
    "These isotope systems have half-lives of billions of years. "
    "Accelerated decay during Creation and/or the Flood produces the "
    "daughter isotopes that scientists measure today."
)

st.sidebar.subheader("Decay Acceleration")
creation_accel_log = st.sidebar.slider(
    "Creation Week Acceleration (log\u2081\u2080)",
    min_value=0.0, max_value=12.0, value=11.0, step=0.5,
    help="10^11 = decay ran 100 billion times faster during the 6 days of Creation. "
         "This is the primary mechanism that produces billions of years of daughter products.",
)
flood_accel_log = st.sidebar.slider(
    "Flood Year Acceleration (log\u2081\u2080)",
    min_value=0.0, max_value=10.0, value=0.0, step=0.5,
    help="Additional acceleration during the Flood year. Default 0 = normal rate (1x).",
)

st.sidebar.subheader("Initial Daughter Isotopes")
st.sidebar.caption(
    "Rocks may have been created with daughter products already present — "
    "mature creation."
)
initial_upb = st.sidebar.slider(
    "U-Pb Initial D/P Ratio",
    min_value=0.0, max_value=2.0, value=0.55, step=0.05,
    help="Initial Pb-206/U-238 at Creation. 0.55 + 10^11 acceleration \u2192 ~4.5 Gyr apparent age.",
)
initial_kar = st.sidebar.slider(
    "K-Ar Initial D/P Ratio",
    min_value=0.0, max_value=5.0, value=0.30, step=0.05,
    help="Initial Ar-40/K-40 at Creation.",
)
initial_rbsr = st.sidebar.slider(
    "Rb-Sr Initial D/P Ratio",
    min_value=0.0, max_value=2.0, value=0.10, step=0.05,
    help="Initial Sr-87/Rb-87 at Creation.",
)

# ── Carbon-14 Parameters ──────────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.header("Carbon-14 Dating")

st.sidebar.subheader("Pre-Flood Atmosphere")
st.sidebar.caption(
    "Before the flood, a water-vapor canopy and stronger magnetic field "
    "shielded the earth from cosmic rays, producing far less C-14."
)
pre_flood_c14 = st.sidebar.slider(
    "Pre-Flood C-14 Ratio (fraction of today's)",
    min_value=0.05, max_value=1.0, value=0.30, step=0.05,
    help="How much C-14 was in the atmosphere before the flood, relative to today. "
         "Lower = more age overestimation by standard dating.",
)
vapor_canopy = st.sidebar.slider(
    "Water Vapor Canopy Shielding",
    min_value=0.0, max_value=0.95, value=0.70, step=0.05,
    help="Fraction of cosmic rays blocked by the pre-flood water vapor canopy.",
)
magnetic_field = st.sidebar.slider(
    "Pre-Flood Magnetic Field Strength (x today's)",
    min_value=1.0, max_value=10.0, value=2.0, step=0.5,
    help="Stronger magnetic field deflects more cosmic rays, reducing C-14 production.",
)

st.sidebar.subheader("The Flood Event")
st.sidebar.caption(
    "Boiling rain, worldwide submersion, extreme pressure — conditions that "
    "cause rapid carbon exchange and isotopic disruption."
)
flood_temp = st.sidebar.slider(
    "Flood Water Temperature (\u00b0C)",
    min_value=20, max_value=300, value=100, step=10,
    help="Temperature of flood waters. Boiling+ causes rapid carbon exchange.",
)
water_depth = st.sidebar.slider(
    "Maximum Water Depth (feet)",
    min_value=1000, max_value=120000, value=90000, step=1000,
    help="Maximum depth of floodwaters. 90,000 ft covers the highest mountains.",
)

st.sidebar.subheader("Post-Flood Recovery")
st.sidebar.caption(
    "After the flood, C-14 had to rebuild from near zero. During this period, "
    "everything appears older than it is."
)
equilibrium_years = st.sidebar.slider(
    "Years to Reach C-14 Equilibrium",
    min_value=500, max_value=5000, value=2000, step=100,
    help="How long it took atmospheric C-14 to rebuild to today's level after the flood.",
)
volcanic_factor = st.sidebar.slider(
    "Post-Flood Volcanic Activity (x normal)",
    min_value=1.0, max_value=5.0, value=1.5, step=0.25,
    help="Post-flood volcanism released massive dead carbon (no C-14), diluting the ratio.",
)
ocean_reservoir = st.sidebar.slider(
    "Ocean Reservoir Factor",
    min_value=0.20, max_value=1.0, value=0.60, step=0.05,
    help="Massive post-flood oceans absorbed atmospheric C-14, keeping levels low.",
)

st.sidebar.subheader("Sample Conditions")
burial_depth = st.sidebar.slider(
    "Burial Depth (meters)",
    min_value=0, max_value=500, value=0, step=10,
    help="Deeper burial = more carbon exchange with surrounding rock.",
)

# ══════════════════════════════════════════════════════════════════════════════
#                           BUILD MODELS
# ══════════════════════════════════════════════════════════════════════════════

# C-14 model
c14_model = FloodAdjustedModel()
c14_model.pre_flood_c14_ratio = pre_flood_c14
c14_model.water_vapor_canopy = vapor_canopy
c14_model.magnetic_field_factor = magnetic_field
c14_model.flood_temperature_c = float(flood_temp)
c14_model.water_depth_feet = float(water_depth)
c14_model.post_flood_equilibrium_years = equilibrium_years
c14_model.volcanic_activity_factor = volcanic_factor
c14_model.ocean_reservoir_factor = ocean_reservoir
c14_model.burial_depth_m = float(burial_depth)

c14_data = c14_model.generate_comparison_data(max_true_age=CURRENT_YEAR, steps=300)

# Long-age radiometric suite
suite = LongAgeRadiometricSuite(
    creation_accel_log10=creation_accel_log,
    flood_accel_log10=flood_accel_log,
    initial_daughters={
        'U-Pb': initial_upb,
        'K-Ar': initial_kar,
        'Rb-Sr': initial_rbsr,
    },
)
long_ages = suite.apparent_ages()

# ══════════════════════════════════════════════════════════════════════════════
#                         HEADLINE METRICS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")

# Row 1: The big picture
h1, h2, h3 = st.columns(3)
with h1:
    st.metric(
        label="True Age of Earth (Torah)",
        value=f"{CURRENT_YEAR:,} years",
    )
with h2:
    upb_age = long_ages['U-Pb']
    st.metric(
        label="U-Pb Apparent Age",
        value=format_age(upb_age),
        delta=f"{upb_age / CURRENT_YEAR:,.0f}x overestimate",
        delta_color="inverse",
    )
with h3:
    c14_flood_date = c14_model.standard_date_for_true_age(YEARS_SINCE_FLOOD)
    st.metric(
        label="C-14 Date for Flood-Era Sample",
        value=f"{c14_flood_date:,.0f} years",
        delta=f"+{c14_flood_date - YEARS_SINCE_FLOOD:,.0f} yrs overestimate",
        delta_color="inverse",
    )

# Row 2: All three long-age systems
m1, m2, m3 = st.columns(3)
for col, key in zip([m1, m2, m3], ['U-Pb', 'K-Ar', 'Rb-Sr']):
    with col:
        age = long_ages[key]
        info = ISOTOPE_SYSTEMS[key]
        st.metric(
            label=f"{info['parent']} \u2192 {info['daughter']}",
            value=format_age(age),
            delta=f"half-life: {info['half_life']:.3g} yrs",
            delta_color="off",
        )

# ══════════════════════════════════════════════════════════════════════════════
#                              TABS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")

tab_big, tab_longiso, tab_age, tab_c14ratio, tab_initial, tab_math = st.tabs([
    "Big Picture",
    "Long-Age Isotopes",
    "C-14: Age Comparison",
    "C-14: Ratio Over Time",
    "C-14: Initial C-14 at Death",
    "The Math",
])

# ── Tab 1: Big Picture ─────────────────────────────────────────────────────

with tab_big:
    st.subheader("All Dating Methods: True Age vs. Apparent Age")
    st.markdown(
        "Every radiometric method -- from Carbon-14 (thousands) to Uranium-Lead "
        "(billions) -- can be explained by a 5,787-year-old Earth when you account "
        "for different initial conditions and decay rates during Creation and the Flood."
    )

    # Bar chart: all methods on log scale
    c14_max_date = c14_model.standard_date_for_true_age(YEARS_SINCE_FLOOD)
    system_names = ['C-14\n(max range)', 'U-238 \u2192 Pb-206', 'K-40 \u2192 Ar-40', 'Rb-87 \u2192 Sr-87']
    apparent_values = [c14_max_date, long_ages['U-Pb'], long_ages['K-Ar'], long_ages['Rb-Sr']]
    bar_colors = ['#FF6B35', '#2196F3', '#4CAF50', '#9C27B0']

    fig_big = go.Figure()
    fig_big.add_trace(go.Bar(
        x=system_names,
        y=apparent_values,
        marker_color=bar_colors,
        text=[format_age(a) for a in apparent_values],
        textposition='outside',
        textfont=dict(size=14),
    ))
    fig_big.add_hline(
        y=CURRENT_YEAR, line_dash="dash", line_color="red", line_width=2,
        annotation_text=f"True age: {CURRENT_YEAR:,} years",
        annotation_position="top left",
        annotation_font_size=14,
    )
    fig_big.update_layout(
        yaxis_title='Apparent Age (years, log scale)',
        yaxis_type='log',
        yaxis_range=[3, 11],  # 1,000 to 100 billion
        height=550,
        showlegend=False,
    )
    st.plotly_chart(fig_big, use_container_width=True)

    # Summary table
    st.subheader("Summary")
    st.table(suite.summary_table())

    st.markdown("""
**How 5,787 years becomes 4.5 billion:**

1. **Mature creation** -- rocks were created during Creation week with initial daughter
   isotopes already present, just as Adam was created as an adult, not an infant.
2. **Accelerated nuclear decay** -- during the 6 days of Creation, radioactive decay
   operated at ~10^11 times its current rate, packing billions of years of daughter
   product accumulation into days.
3. **The single assumption** -- standard radiometric dating assumes decay has ALWAYS
   been constant and initial daughter products were ALWAYS zero. Those two assumptions
   alone account for the entire discrepancy between 5,787 and 4,500,000,000.
4. **Carbon-14 is separate** -- C-14 only reaches ~50,000 years because of its short
   half-life. Its overestimation comes from a different mechanism: lower pre-flood
   atmospheric C-14 due to the water vapor canopy and stronger magnetic field.
    """)

# ── Tab 2: Long-Age Isotopes Detail ───────────────────────────────────────

with tab_longiso:
    st.subheader("Long-Age Isotope Systems: Epoch-by-Epoch Breakdown")
    st.markdown(
        "Select an isotope system to see exactly how parent and daughter isotopes "
        "evolve through each epoch of biblical history."
    )

    selected_system = st.selectbox(
        "Select isotope system",
        options=list(ISOTOPE_SYSTEMS.keys()),
        format_func=lambda k: (
            f"{ISOTOPE_SYSTEMS[k]['parent']} \u2192 {ISOTOPE_SYSTEMS[k]['daughter']} "
            f"({ISOTOPE_SYSTEMS[k]['description']})"
        ),
    )

    sys = suite.systems[selected_system]
    epochs = sys.get_epoch_breakdown()

    # Epoch table
    st.table([{
        'Epoch': e['name'],
        'Duration': e['duration'],
        'Acceleration': e['acceleration'],
        'Parent (P)': f"{e['P_after']:.6f}",
        'Daughter (D)': f"{e['D_after']:.6f}",
        'P Consumed': f"{e['consumed']:.6f}",
    } for e in epochs])

    # Chart: P and D through epochs
    epoch_labels = ['Creation\n(start)'] + [e['name'].split('(')[0].strip() for e in epochs]
    p_vals = [1.0] + [e['P_after'] for e in epochs]
    d_vals = [sys.initial_daughter_ratio] + [e['D_after'] for e in epochs]

    fig_epochs = go.Figure()
    fig_epochs.add_trace(go.Scatter(
        x=epoch_labels, y=p_vals,
        mode='lines+markers', name=f'Parent ({sys.parent_name})',
        line=dict(color='#2196F3', width=3),
        marker=dict(size=10),
    ))
    fig_epochs.add_trace(go.Scatter(
        x=epoch_labels, y=d_vals,
        mode='lines+markers', name=f'Daughter ({sys.daughter_name})',
        line=dict(color='#FF6B35', width=3),
        marker=dict(size=10),
    ))
    fig_epochs.update_layout(
        yaxis_title='Normalized Amount',
        height=450,
        hovermode='x unified',
    )
    st.plotly_chart(fig_epochs, use_container_width=True)

    # Final result
    st.markdown(f"""
**Final D/P ratio:** {sys.daughter_parent_ratio():.4f}

**Standard dating formula:** t = (1/\u03bb) \u00d7 ln(1 + D/P) = **{format_age(sys.apparent_age())}**

**True age:** {CURRENT_YEAR:,} years
    """)

# ── Tab 3: C-14 Age Comparison ────────────────────────────────────────────

with tab_age:
    st.subheader("What Standard Carbon Dating Reports vs. True Age")
    st.markdown(
        "The orange line shows what standard C-14 dating would report for samples "
        "of various true ages. The dashed black line is a perfect match (no error). "
        "**Everything above the dashed line is overestimated age.**"
    )

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=c14_data['true_ages'], y=c14_data['standard_dates'],
        mode='lines', name='Standard C-14 Date',
        line=dict(color='#FF6B35', width=3),
        hovertemplate='True age: %{x:,.0f} yrs<br>Standard date: %{y:,.0f} yrs<extra></extra>',
    ))

    max_val = max(c14_data['true_ages'].max(), c14_data['standard_dates'].max())
    fig1.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode='lines', name='Perfect Match (no error)',
        line=dict(color='black', dash='dash', width=1),
    ))

    flood_std = c14_model.standard_date_for_true_age(YEARS_SINCE_FLOOD)
    fig1.add_trace(go.Scatter(
        x=[YEARS_SINCE_FLOOD], y=[flood_std],
        mode='markers+text', name='Flood Event',
        marker=dict(size=14, color='#2196F3', symbol='star'),
        text=[f'Flood ({YEARS_SINCE_FLOOD:,} yrs ago)'],
        textposition='top left',
    ))

    fig1.update_layout(
        xaxis_title='True Age (years)',
        yaxis_title='Standard Carbon-14 Date (years)',
        height=550,
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )
    st.plotly_chart(fig1, use_container_width=True)

# ── Tab 4: C-14 Ratio Over Time ──────────────────────────────────────────

with tab_c14ratio:
    st.subheader("Measured C-14 Ratio Over Time")
    st.markdown(
        "Compares the C-14 ratio you'd **actually measure** in a sample (under "
        "flood-adjusted conditions) vs. what the standard model predicts. "
        "The gap between these curves is what causes the dating error."
    )

    standard_model = StandardModel()
    standard_ratios = np.array([standard_model.predict_ratio(a) for a in c14_data['true_ages']])

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=c14_data['true_ages'], y=standard_ratios,
        mode='lines', name='Standard Model Prediction',
        line=dict(color='#2196F3', width=2),
    ))
    fig2.add_trace(go.Scatter(
        x=c14_data['true_ages'], y=c14_data['measured_ratios'],
        mode='lines', name='Flood-Adjusted (actual measurement)',
        line=dict(color='#FF6B35', width=3),
    ))
    fig2.add_trace(go.Scatter(
        x=np.concatenate([c14_data['true_ages'], c14_data['true_ages'][::-1]]),
        y=np.concatenate([standard_ratios, c14_data['measured_ratios'][::-1]]),
        fill='toself', fillcolor='rgba(255, 107, 53, 0.15)',
        line=dict(width=0), showlegend=True,
        name='Dating Error Zone',
    ))
    fig2.update_layout(
        xaxis_title='True Age (years)',
        yaxis_title='C-14 / C-12 Ratio (normalized)',
        yaxis_type='log',
        height=550,
        hovermode='x unified',
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab 5: Initial C-14 at Death ─────────────────────────────────────────

with tab_initial:
    st.subheader("Atmospheric C-14 at the Time Each Organism Died")
    st.markdown(
        "Standard dating assumes this was **always 1.0** (the dashed line). "
        "Under flood conditions, it was far lower for most of history. "
        "An organism that started with less C-14 will appear older than it is."
    )

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=c14_data['true_ages'], y=c14_data['initial_ratios'],
        mode='lines', name='Flood-Adjusted Initial C-14',
        line=dict(color='#4CAF50', width=3),
    ))
    fig3.add_trace(go.Scatter(
        x=[c14_data['true_ages'].min(), c14_data['true_ages'].max()],
        y=[1.0, 1.0],
        mode='lines', name='Standard Assumption (always 1.0)',
        line=dict(color='black', dash='dash', width=1),
    ))
    fig3.add_vline(
        x=YEARS_SINCE_FLOOD, line_dash="dot", line_color="#2196F3",
        annotation_text=f"Flood (~{YEARS_SINCE_FLOOD:,} yrs ago)",
        annotation_position="top left",
    )
    fig3.update_layout(
        xaxis_title='Years Ago (true age)',
        yaxis_title='Initial C-14 Ratio (fraction of today)',
        height=550,
        hovermode='x unified',
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Tab 6: The Math ──────────────────────────────────────────────────────

with tab_math:
    st.subheader("Carbon-14 Dating Math")

    st.markdown(r"""
**Standard C-14 dating formula:**

$$t = \frac{-\ln(R_{measured})}{\lambda}$$

Where:
- $t$ = calculated age
- $R_{measured}$ = measured C-14/C-12 ratio (normalized to modern atmosphere = 1.0)
- $\lambda = \frac{\ln 2}{5730} \approx 0.000121$ per year (decay constant)

**The critical assumption:** This formula assumes the initial ratio $R_0$ was **always 1.0**
(same as today's atmosphere). The full equation is:

$$t = \frac{-\ln(R_{measured} / R_0)}{\lambda}$$

If $R_0$ was actually **lower** than 1.0, standard dating **overestimates** the age:

$$t_{standard} = t_{true} + \frac{-\ln(R_0)}{\lambda}$$

The overestimation is exactly $\frac{-\ln(R_0)}{\lambda}$ years.
    """)

    st.markdown("---")
    st.subheader("C-14 Overestimation by Initial Ratio")

    r0_examples = [0.05, 0.10, 0.20, 0.30, 0.50, 0.75, 1.0]
    rows = []
    for r0 in r0_examples:
        overest = -np.log(r0) / LAMBDA
        rows.append({
            "Initial C-14 Ratio (R\u2080)": f"{r0:.2f}",
            "Age Overestimate (years)": f"{overest:,.0f}" if r0 < 1.0 else "0 (no error)",
        })
    st.table(rows)

    effective_preflood = c14_model.effective_initial_c14(YEARS_SINCE_FLOOD + 100)
    overest_years = -np.log(effective_preflood) / LAMBDA if effective_preflood > 0 else float('inf')
    st.markdown(
        f"With current slider settings, a pre-flood organism has effective "
        f"**R\u2080 = {effective_preflood:.4f}**, adding **{overest_years:,.0f} years** "
        f"of apparent age."
    )

    # ── Long-Age Radiometric Math ──────────────────────────────────────────

    st.markdown("---")
    st.subheader("Long-Age Radiometric Dating Math")

    st.markdown(r"""
**Standard radiometric age formula** (any parent $\rightarrow$ daughter system):

$$t_{apparent} = \frac{1}{\lambda} \ln\left(1 + \frac{D}{P}\right)$$

Where:
- $\lambda = \ln(2) / t_{1/2}$ (decay constant from the half-life)
- $D$ = measured daughter isotope amount
- $P$ = measured parent isotope amount

**The assumptions:**
1. All $D$ came from in-situ decay of $P$ (no initial daughter products)
2. Decay rate $\lambda$ has been constant for all of history
3. The system has been closed (no contamination)

**The flood-adjusted model** violates all three:

**Tracking P and D through epochs:** Starting with $P_0 = 1.0$ and $D_0 = D_{initial}$,
for each epoch with duration $\Delta t$ and acceleration factor $A$:

$$P_{after} = P_{before} \cdot e^{-A \cdot \lambda \cdot \Delta t}$$
$$D_{after} = D_{before} + P_{before} - P_{after}$$

**Creation week** ($\Delta t = 6$ days, $A = 10^{11}$) is where the heavy lifting happens.
The effective decay parameter $A \cdot \lambda \cdot \Delta t$ can be large enough to
convert a significant fraction of parent into daughter — equivalent to billions of years
at normal rates.
    """)

    st.markdown("---")
    st.subheader("Epoch Breakdown (Current Settings)")

    for key in ISOTOPE_SYSTEMS:
        sys = suite.systems[key]
        info = ISOTOPE_SYSTEMS[key]
        epochs = sys.get_epoch_breakdown()

        st.markdown(f"**{info['parent']} \u2192 {info['daughter']}** "
                    f"(half-life: {info['half_life']:.3g} years)")

        st.table([{
            'Epoch': e['name'],
            'Acceleration': e['acceleration'],
            'Parent (P)': f"{e['P_after']:.6f}",
            'Daughter (D)': f"{e['D_after']:.6f}",
        } for e in epochs])

        st.markdown(
            f"Final D/P = {sys.daughter_parent_ratio():.4f} \u2192 "
            f"**Apparent age: {format_age(sys.apparent_age())}** "
            f"(true age: {CURRENT_YEAR:,} years)"
        )
        st.markdown("")

# ── Footer ──────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    f"**Torah Timeline:** Creation {CURRENT_YEAR:,} years ago | "
    f"Flood {YEARS_SINCE_FLOOD:,} years ago (year {FLOOD_YEAR} from Creation) | "
    f"C-14 half-life: {CARBON_14_HALF_LIFE:,} years | "
    f"U-238 half-life: 4.468 Gyr | "
    f"K-40 half-life: 1.248 Gyr | "
    f"Rb-87 half-life: 48.8 Gyr"
)
