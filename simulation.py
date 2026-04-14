import numpy as np
import pandas as pd
from models import create_model, StandardModel

class CarbonSimulation:
    """Handles carbon-14 dating simulations with various models"""
    
    def __init__(self):
        # Initialize with standard model and a flood model
        self.standard_model = StandardModel()
        self.custom_model = None
        self.results = {}
    
    def setup_custom_model(self, model_type, **parameters):
        """
        Set up a custom model with specific parameters
        
        Parameters:
        - model_type: "standard", "flood", or "young_earth"
        - parameters: model-specific parameters
        """
        self.custom_model = create_model(model_type)
        
        # Set parameters if it's an adjustable model
        if hasattr(self.custom_model, 'set_parameters'):
            self.custom_model.set_parameters(**parameters)
        
        return self.custom_model
    
    def run_simulation(self, true_age, burial_depth=0, atmospheric_exposure=True,
                      water_pressure=0, pre_flood_c14=1.0, post_flood_c14=1.0):
        """
        Run a simulation comparing standard dating with adjusted model
        
        Parameters:
        - true_age: Actual years since death
        - burial_depth: Depth of burial in meters
        - atmospheric_exposure: If the sample was exposed to atmosphere
        - water_pressure: Water pressure factor (0-10)
        - pre_flood_c14: C-14 concentration factor pre-flood
        - post_flood_c14: C-14 concentration factor post-flood
        
        Returns:
        - Dictionary with simulation results
        """
        if self.custom_model is None:
            # Default to a flood model if none is set
            self.custom_model = create_model("flood")
        
        # Step 1: Calculate what C14 ratio we would measure today
        # if the organism died true_age years ago under custom model
        if self.custom_model.__class__.__name__ == "StandardModel":
            # Standard model only takes the age parameter
            c14_ratio = self.custom_model.predict_ratio(true_age)
        else:
            # Flood adjusted models take additional parameters
            c14_ratio = self.custom_model.predict_ratio(
                true_age, burial_depth, atmospheric_exposure, water_pressure
            )
        
        # Step 2: Calculate what age standard dating would assign
        standard_date = self.standard_model.calculate_age(c14_ratio)
        
        # Step 3: Store results
        self.results = {
            'true_age': true_age,
            'measured_c14_ratio': c14_ratio,
            'standard_date': standard_date,
            'error_years': standard_date - true_age,
            'error_percent': (standard_date - true_age) / true_age * 100 if true_age > 0 else float('inf'),
            'burial_depth': burial_depth,
            'atmospheric_exposure': atmospheric_exposure,
            'water_pressure': water_pressure,
            'model_name': self.custom_model.name
        }
        
        return self.results
    
    def generate_decay_curves(self, max_age=10000, steps=100):
        """
        Generate decay curves for both models for visualization
        
        Parameters:
        - max_age: Maximum age to simulate (years)
        - steps: Number of data points
        
        Returns:
        - DataFrame with time points and C14 ratios for both models
        """
        if self.custom_model is None:
            self.custom_model = create_model("flood")
            
        ages = np.linspace(0, max_age, steps)
        standard_ratios = [self.standard_model.predict_ratio(age) for age in ages]
        
        # Use parameters from last simulation if available
        burial_depth = self.results.get('burial_depth', 0)
        atmospheric_exposure = self.results.get('atmospheric_exposure', True)
        water_pressure = self.results.get('water_pressure', 0)
        
        if self.custom_model.__class__.__name__ == "StandardModel":
            # Standard model only takes the age parameter
            custom_ratios = [self.custom_model.predict_ratio(age) for age in ages]
        else:
            # Flood adjusted models take additional parameters
            custom_ratios = [self.custom_model.predict_ratio(
                age, burial_depth, atmospheric_exposure, water_pressure
            ) for age in ages]
        
        return pd.DataFrame({
            'age': ages,
            'standard_ratio': standard_ratios,
            'custom_ratio': custom_ratios
        })
    
    def export_to_csv(self, filename="simulation_results.csv"):
        """Export simulation results to CSV"""
        if not self.results:
            raise ValueError("No simulation results to export")
            
        # Create DataFrame from results
        df = pd.DataFrame([self.results])
        df.to_csv(filename, index=False)
        return filename
        
    def export_curves_to_csv(self, filename="decay_curves.csv", max_age=10000, steps=100):
        """Export decay curves to CSV"""
        curves = self.generate_decay_curves(max_age, steps)
        curves.to_csv(filename, index=False)
        return filename
