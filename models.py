import numpy as np

# ── C-14 Constants ──────────────────────────────────────────────────────────
CARBON_14_HALF_LIFE = 5730  # years (standard accepted value)
LAMBDA = np.log(2) / CARBON_14_HALF_LIFE  # decay constant
STANDARD_ATMOSPHERE_C14_RATIO = 1.0  # Normalized reference value

# ── Torah Timeline ──────────────────────────────────────────────────────────
FLOOD_YEAR = 1656  # Years from Creation to the Flood (Hebrew calendar)
CURRENT_YEAR = 5787  # Current Hebrew year
YEARS_SINCE_FLOOD = CURRENT_YEAR - FLOOD_YEAR  # ~4131 years ago
FLOOD_DURATION_DAYS = 365  # Approximately one year
CREATION_WEEK_YEARS = 6.0 / 365.25  # 6 days in years
FLOOD_YEAR_YEARS = 1.0  # Duration of the flood

# ── Long-Age Isotope Systems ───────────────────────────────────────────────
ISOTOPE_SYSTEMS = {
    'U-Pb': {
        'parent': 'U-238',
        'daughter': 'Pb-206',
        'half_life': 4.468e9,
        'lambda': np.log(2) / 4.468e9,
        'description': 'Uranium-Lead',
        'science_says': '4.5 billion years (Earth\'s age)',
    },
    'K-Ar': {
        'parent': 'K-40',
        'daughter': 'Ar-40',
        'half_life': 1.248e9,
        'lambda': np.log(2) / 1.248e9,
        'description': 'Potassium-Argon',
        'science_says': 'Millions to billions of years (rocks & fossils)',
    },
    'Rb-Sr': {
        'parent': 'Rb-87',
        'daughter': 'Sr-87',
        'half_life': 48.8e9,
        'lambda': np.log(2) / 48.8e9,
        'description': 'Rubidium-Strontium',
        'science_says': 'Billions of years (oldest rocks)',
    },
}


class StandardModel:
    """Standard carbon dating model - assumes constant atmospheric C-14 and
    constant decay rate throughout all of history."""

    def __init__(self):
        self.name = "Standard Scientific Model"

    def calculate_age(self, c14_ratio):
        """Standard age calculation: t = -ln(ratio) / lambda"""
        if c14_ratio <= 0:
            return float('inf')
        return -np.log(c14_ratio) / LAMBDA

    def predict_ratio(self, age):
        """Standard prediction: ratio = e^(-lambda * t)"""
        return np.exp(-LAMBDA * age)


class FloodAdjustedModel:
    """Model that accounts for how a global catastrophic flood would alter
    carbon-14 concentrations and potentially affect dating accuracy.

    Key assumptions that differ from the standard model:
    1. Pre-flood atmosphere had LESS C-14 (water vapor canopy shielded cosmic rays)
    2. Pre-flood magnetic field was STRONGER (deflected more cosmic rays)
    3. The flood catastrophically disrupted C-14 equilibrium
    4. Post-flood C-14 has been building up toward current levels
    5. Extreme temperature and pressure during the flood affected samples
    6. Massive ocean coverage diluted atmospheric C-14
    """

    def __init__(self):
        self.name = "Flood-Adjusted Model"

        # Default parameter values
        self.pre_flood_c14_ratio = 0.30      # Fraction of today's atmospheric C-14
        self.water_vapor_canopy = 0.70        # Shielding factor (0=no shield, 1=total)
        self.magnetic_field_factor = 2.0      # Multiple of today's field strength
        self.flood_temperature_c = 100.0      # Water temperature during flood (Celsius)
        self.water_depth_feet = 90000.0       # Maximum water depth during flood
        self.post_flood_equilibrium_years = 2000  # Years for C-14 to reach new equilibrium
        self.ocean_reservoir_factor = 0.60    # Dilution from massive ocean coverage
        self.burial_depth_m = 0.0             # Sample burial depth in meters
        self.volcanic_activity_factor = 1.5   # Post-flood volcanic CO2 (dilutes C-14)

    def _cosmic_ray_shielding(self):
        """Calculate total cosmic ray shielding from vapor canopy + magnetic field.
        More shielding = less C-14 production = organisms start with less C-14."""
        # Stronger magnetic field deflects cosmic rays (roughly inverse relationship)
        magnetic_shielding = 1.0 / self.magnetic_field_factor
        # Water vapor canopy absorbs remaining cosmic rays
        canopy_transmission = 1.0 - self.water_vapor_canopy
        return magnetic_shielding * canopy_transmission

    def _temperature_pressure_factor(self):
        """Calculate how extreme temperature and pressure affect the sample.

        While nuclear decay rates are generally considered constant, the
        CONDITIONS under which carbon is deposited and preserved matter:
        - Boiling water dissolves and redeposits carbon
        - Extreme pressure compresses sediment layers rapidly
        - High temperature accelerates chemical exchange reactions
        - These cause carbon exchange that makes samples appear older
        """
        # Temperature effect: boiling water causes rapid carbon exchange
        # Normalized so room temp (20C) = 1.0
        temp_factor = 1.0 + (self.flood_temperature_c - 20.0) / 200.0

        # Pressure effect: 90,000 ft of water = ~2,700 atm
        pressure_atm = (self.water_depth_feet * 0.3048) * 9810 / 101325
        pressure_factor = 1.0 + np.log1p(pressure_atm) / 10.0

        # Burial compression: deeper burial = more carbon exchange
        burial_factor = 1.0 + self.burial_depth_m * 0.005

        return temp_factor * pressure_factor * burial_factor

    def _post_flood_c14_buildup(self, years_after_flood):
        """Model the gradual buildup of atmospheric C-14 after the flood.

        After the flood destroyed the pre-flood equilibrium, C-14 had to build
        back up from a very low level to today's concentration. During this
        buildup period, organisms incorporated LESS C-14 than modern organisms,
        so they APPEAR older than they are when dated with modern assumptions.
        """
        if years_after_flood <= 0:
            return self.pre_flood_c14_ratio

        # Exponential approach to modern equilibrium
        tau = self.post_flood_equilibrium_years / 3.0  # Time constant
        buildup = 1.0 - (1.0 - self.pre_flood_c14_ratio) * np.exp(-years_after_flood / tau)

        # Volcanic activity injects dead carbon, slowing apparent equilibrium
        volcanic_dilution = 1.0 / self.volcanic_activity_factor
        buildup *= volcanic_dilution

        # Ocean reservoir effect: massive oceans absorb and release old carbon
        buildup *= self.ocean_reservoir_factor

        return min(buildup, 1.0)

    def effective_initial_c14(self, true_age):
        """Calculate what the ACTUAL C-14/C-12 ratio was when the organism died,
        accounting for all flood effects.

        This is the key insight: standard dating assumes the initial ratio was
        always the same as today (1.0). If it was actually much lower, the
        standard model will calculate an age much older than reality.
        """
        years_after_flood = YEARS_SINCE_FLOOD - true_age

        if years_after_flood < 0:
            # Pre-flood organism
            cosmic_shielding = self._cosmic_ray_shielding()
            return self.pre_flood_c14_ratio * cosmic_shielding
        elif years_after_flood < FLOOD_DURATION_DAYS / 365.0:
            # During the flood itself
            return self.pre_flood_c14_ratio * 0.5  # Severely disrupted
        else:
            # Post-flood organism
            return self._post_flood_c14_buildup(years_after_flood)

    def predict_measured_ratio(self, true_age):
        """Predict what C-14 ratio we would MEASURE TODAY for a sample that
        actually died 'true_age' years ago, under flood-adjusted conditions.

        Steps:
        1. Calculate what C-14 ratio the organism had when it died
        2. Apply standard radioactive decay for the elapsed time
        3. Apply temperature/pressure effects from the flood
        """
        # What ratio did the organism actually start with?
        initial_ratio = self.effective_initial_c14(true_age)

        # Standard radioactive decay since death
        decayed_ratio = initial_ratio * np.exp(-LAMBDA * true_age)

        # Temperature/pressure effects during the flood further altered the sample
        years_after_flood = YEARS_SINCE_FLOOD - true_age
        if -1 <= years_after_flood <= 2:  # During or shortly after the flood
            tp_factor = self._temperature_pressure_factor()
            # High temp/pressure causes additional apparent aging
            decayed_ratio /= tp_factor

        return max(decayed_ratio, 1e-15)

    def standard_date_for_true_age(self, true_age):
        """Given a TRUE age, calculate what STANDARD carbon dating would report.

        This is the central demonstration: standard dating takes the measured
        ratio and assumes a constant initial ratio of 1.0. When the actual
        initial ratio was much lower, standard dating wildly overestimates.
        """
        measured_ratio = self.predict_measured_ratio(true_age)
        # Standard dating formula assumes initial ratio = 1.0
        if measured_ratio <= 0:
            return float('inf')
        return -np.log(measured_ratio) / LAMBDA

    def generate_comparison_data(self, max_true_age=None, steps=200):
        """Generate arrays comparing true age vs standard-dated age."""
        if max_true_age is None:
            max_true_age = CURRENT_YEAR

        true_ages = np.linspace(100, max_true_age, steps)
        standard_dates = np.array([self.standard_date_for_true_age(a) for a in true_ages])
        initial_ratios = np.array([self.effective_initial_c14(a) for a in true_ages])
        measured_ratios = np.array([self.predict_measured_ratio(a) for a in true_ages])

        return {
            'true_ages': true_ages,
            'standard_dates': standard_dates,
            'initial_ratios': initial_ratios,
            'measured_ratios': measured_ratios,
        }


# ── Long-Age Radiometric Dating ────────────────────────────────────────────

def format_age(years):
    """Format age for display: billions, millions, or thousands."""
    if years >= 1e9:
        return f'{years / 1e9:.2f} billion years'
    elif years >= 1e6:
        return f'{years / 1e6:.1f} million years'
    elif years >= 1e3:
        return f'{years / 1e3:.1f} thousand years'
    else:
        return f'{years:.0f} years'


class RadiometricSystem:
    """Models a single parent->daughter isotope system through biblical epochs.

    Tracks parent (P) and daughter (D) amounts through:
      1. Creation week — accelerated decay packs billions of years into 6 days
      2. Pre-flood normal decay (~1,650 years, negligible for Gyr half-lives)
      3. Flood year — optional additional accelerated decay
      4. Post-flood normal decay (~4,131 years, negligible)

    Then calculates what standard radiometric dating would report.
    """

    def __init__(self, system_key, initial_daughter_ratio=0.0,
                 creation_acceleration_log10=11.0,
                 flood_acceleration_log10=0.0):
        info = ISOTOPE_SYSTEMS[system_key]
        self.key = system_key
        self.parent_name = info['parent']
        self.daughter_name = info['daughter']
        self.half_life = info['half_life']
        self.decay_constant = info['lambda']
        self.description = info['description']

        self.initial_daughter_ratio = initial_daughter_ratio
        self.creation_acceleration_log10 = creation_acceleration_log10
        self.flood_acceleration_log10 = flood_acceleration_log10

    @property
    def creation_acceleration(self):
        return 10.0 ** self.creation_acceleration_log10

    @property
    def flood_acceleration(self):
        return 10.0 ** self.flood_acceleration_log10

    def _evolve(self):
        """Walk P and D through each epoch. Returns final (P, D)."""
        lam = self.decay_constant
        P = 1.0
        D = self.initial_daughter_ratio

        # Epoch 1: Creation week (6 days, accelerated)
        decay_f = np.exp(-self.creation_acceleration * lam * CREATION_WEEK_YEARS)
        consumed = P * (1.0 - decay_f)
        P *= decay_f
        D += consumed

        # Epoch 2: Pre-flood normal (~1,650 years)
        dt_pre = FLOOD_YEAR - CREATION_WEEK_YEARS
        decay_f = np.exp(-lam * dt_pre)
        consumed = P * (1.0 - decay_f)
        P *= decay_f
        D += consumed

        # Epoch 3: Flood year (accelerated)
        decay_f = np.exp(-self.flood_acceleration * lam * FLOOD_YEAR_YEARS)
        consumed = P * (1.0 - decay_f)
        P *= decay_f
        D += consumed

        # Epoch 4: Post-flood normal (~4,131 years)
        decay_f = np.exp(-lam * YEARS_SINCE_FLOOD)
        consumed = P * (1.0 - decay_f)
        P *= decay_f
        D += consumed

        return P, D

    def apparent_age(self):
        """What standard radiometric dating would report: t = (1/lam) * ln(1 + D/P)."""
        P, D = self._evolve()
        if P <= 0:
            return float('inf')
        return (1.0 / self.decay_constant) * np.log(1.0 + D / P)

    def daughter_parent_ratio(self):
        P, D = self._evolve()
        if P <= 0:
            return float('inf')
        return D / P

    def get_epoch_breakdown(self):
        """Return detailed breakdown for each epoch."""
        lam = self.decay_constant
        P = 1.0
        D = self.initial_daughter_ratio
        epochs = []

        # Creation week
        dt = CREATION_WEEK_YEARS
        eff_lam = self.creation_acceleration * lam
        decay_f = np.exp(-eff_lam * dt)
        consumed = P * (1.0 - decay_f)
        P *= decay_f
        D += consumed
        epochs.append({
            'name': 'Creation Week (6 days)',
            'duration': '6 days',
            'acceleration': f'10^{self.creation_acceleration_log10:.0f}x',
            'P_after': P, 'D_after': D, 'consumed': consumed,
        })

        # Pre-flood
        dt = FLOOD_YEAR - CREATION_WEEK_YEARS
        decay_f = np.exp(-lam * dt)
        consumed = P * (1.0 - decay_f)
        P *= decay_f
        D += consumed
        epochs.append({
            'name': f'Pre-Flood ({dt:.0f} yrs, normal)',
            'duration': f'{dt:.0f} years',
            'acceleration': '1x',
            'P_after': P, 'D_after': D, 'consumed': consumed,
        })

        # Flood year
        dt = FLOOD_YEAR_YEARS
        eff_lam = self.flood_acceleration * lam
        decay_f = np.exp(-eff_lam * dt)
        consumed = P * (1.0 - decay_f)
        P *= decay_f
        D += consumed
        epochs.append({
            'name': 'Flood Year',
            'duration': '1 year',
            'acceleration': f'10^{self.flood_acceleration_log10:.0f}x',
            'P_after': P, 'D_after': D, 'consumed': consumed,
        })

        # Post-flood
        dt = YEARS_SINCE_FLOOD
        decay_f = np.exp(-lam * dt)
        consumed = P * (1.0 - decay_f)
        P *= decay_f
        D += consumed
        epochs.append({
            'name': f'Post-Flood ({dt:,} yrs, normal)',
            'duration': f'{dt:,} years',
            'acceleration': '1x',
            'P_after': P, 'D_after': D, 'consumed': consumed,
        })

        return epochs


class LongAgeRadiometricSuite:
    """Groups all long-age isotope systems with shared acceleration settings."""

    DEFAULT_CREATION_ACCEL_LOG10 = 11.0
    DEFAULT_FLOOD_ACCEL_LOG10 = 0.0
    DEFAULT_INITIAL_DAUGHTERS = {
        'U-Pb': 0.55,
        'K-Ar': 0.30,
        'Rb-Sr': 0.10,
    }

    def __init__(self, creation_accel_log10=None, flood_accel_log10=None,
                 initial_daughters=None):
        ca = creation_accel_log10 if creation_accel_log10 is not None else self.DEFAULT_CREATION_ACCEL_LOG10
        fa = flood_accel_log10 if flood_accel_log10 is not None else self.DEFAULT_FLOOD_ACCEL_LOG10
        daughters = initial_daughters if initial_daughters is not None else self.DEFAULT_INITIAL_DAUGHTERS

        self.systems = {}
        for key in ISOTOPE_SYSTEMS:
            self.systems[key] = RadiometricSystem(
                system_key=key,
                initial_daughter_ratio=daughters.get(key, 0.0),
                creation_acceleration_log10=ca,
                flood_acceleration_log10=fa,
            )

    def apparent_ages(self):
        return {k: s.apparent_age() for k, s in self.systems.items()}

    def summary_table(self):
        rows = []
        for key, sys in self.systems.items():
            age = sys.apparent_age()
            rows.append({
                'System': f'{sys.parent_name} \u2192 {sys.daughter_name}',
                'Half-Life': f'{sys.half_life:.3g} years',
                'D/P Ratio': f'{sys.daughter_parent_ratio():.4f}',
                'Apparent Age': format_age(age),
                'True Age': f'{CURRENT_YEAR:,} years',
            })
        return rows
