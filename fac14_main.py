#!/usr/bin/env python3
"""
Flood-Adjusted Carbon-14 Simulation Program (FAC14)
This program simulates alternative carbon-14 decay timelines, accounting for
a global cataclysmic event (e.g., a worldwide flood) that may have altered
atmospheric and geological conditions.
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Import our modules
from models import create_model
from simulation import CarbonSimulation
import visualization as viz

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Flood-Adjusted Carbon-14 Simulation Program (FAC14)')
    
    parser.add_argument('--age', type=float, default=5000,
                       help='Time since organism death (years)')
    parser.add_argument('--depth', type=float, default=0,
                       help='Burial depth (meters)')
    parser.add_argument('--exposure', action='store_true',
                       help='Whether the sample had atmospheric exposure')
    parser.add_argument('--pressure', type=float, default=0,
                       help='Water pressure/exposure levels (0-10)')
    parser.add_argument('--pre-flood-c14', type=float, default=0.5,
                       help='Pre-Flood C-14 concentration factor')
    parser.add_argument('--post-flood-c14', type=float, default=1.0,
                       help='Post-Flood C-14 concentration factor')
    parser.add_argument('--model', type=str, default='flood',
                       choices=['standard', 'flood', 'young_earth'],
                       help='Decay model to use')
    parser.add_argument('--export', action='store_true',
                       help='Export results to CSV')
    parser.add_argument('--plot', action='store_true',
                       help='Show plots')
    parser.add_argument('--interactive', action='store_true',
                       help='Use interactive Plotly plots instead of Matplotlib')
    
    return parser.parse_args()

def get_user_input():
    """Interactive prompt for user input"""
    print("\n===== Flood-Adjusted Carbon-14 Simulation Program (FAC14) =====\n")
    
    # Model selection
    print("\nSelect a model:")
    print("1. Standard Scientific Model")
    print("2. Flood-Calibrated Model")
    print("3. Young Earth Model")
    model_choice = input("Enter choice (1-3) [2]: ").strip() or "2"
    model_map = {"1": "standard", "2": "flood", "3": "young_earth"}
    model_type = model_map.get(model_choice, "flood")
    
    # Sample parameters
    print("\nEnter sample parameters:")
    try:
        age = float(input("Time since organism death (years) [5000]: ").strip() or "5000")
        depth = float(input("Burial depth (meters) [0]: ").strip() or "0")
        exposure_input = input("Atmospheric exposure (y/n) [y]: ").strip() or "y"
        exposure = exposure_input.lower() in ('y', 'yes', 'true')
        pressure = float(input("Water pressure level (0-10) [0]: ").strip() or "0")
        
        # Model parameters
        print("\nEnter model parameters:")
        pre_flood = float(input("Pre-Flood C-14 concentration factor (0-1) [0.5]: ").strip() or "0.5")
        post_flood = float(input("Post-Flood C-14 concentration factor (0-2) [1.0]: ").strip() or "1.0")
        
        # Visualization preferences
        print("\nVisualization options:")
        plot = input("Show plots? (y/n) [y]: ").strip() or "y"
        plot = plot.lower() in ('y', 'yes', 'true')
        interactive = input("Use interactive plots? (y/n) [n]: ").strip() or "n"
        interactive = interactive.lower() in ('y', 'yes', 'true')
        export = input("Export results to CSV? (y/n) [y]: ").strip() or "y"
        export = export.lower() in ('y', 'yes', 'true')
        
        # Create args-like object
        class Args:
            pass
        
        args = Args()
        args.age = age
        args.depth = depth
        args.exposure = exposure
        args.pressure = pressure
        args.pre_flood_c14 = pre_flood
        args.post_flood_c14 = post_flood
        args.model = model_type
        args.plot = plot
        args.interactive = interactive
        args.export = export
        
        return args
    
    except ValueError as e:
        print(f"Error in input: {e}")
        print("Using default values instead.")
        args = parse_args()
        args.model = model_type
        return args

def format_output(results):
    """Format simulation results for display"""
    output = "\n===== SIMULATION RESULTS =====\n\n"
    output += f"Model used: {results['model_name']}\n"
    output += f"True age: {results['true_age']:.2f} years\n"
    output += f"Standard carbon date: {results['standard_date']:.2f} years\n"
    output += f"Difference: {results['error_years']:.2f} years\n"
    output += f"Percentage error: {results['error_percent']:.2f}%\n\n"
    output += "Sample conditions:\n"
    output += f"- Burial depth: {results['burial_depth']:.2f} meters\n"
    output += f"- Atmospheric exposure: {'Yes' if results['atmospheric_exposure'] else 'No'}\n"
    output += f"- Water pressure factor: {results['water_pressure']:.2f}\n"
    
    return output

def run_batch_simulation(model_type="flood", max_age=10000, steps=20):
    """Run a batch of simulations across different ages"""
    sim = CarbonSimulation()
    custom_model = sim.setup_custom_model(model_type)
    
    true_ages = np.linspace(1000, max_age, steps)
    standard_dates = []
    
    for age in true_ages:
        result = sim.run_simulation(age)
        standard_dates.append(result['standard_date'])
    
    return true_ages, standard_dates, custom_model.name

def main():
    """Main program entry point"""
    # Check if running from command line with arguments
    if len(sys.argv) > 1:
        args = parse_args()
    else:
        # Otherwise get user input interactively
        args = get_user_input()
    
    # Initialize the simulation
    sim = CarbonSimulation()
    
    # Set up the custom model with parameters
    model_params = {
        'initial_c14_ratio': args.pre_flood_c14,
        'cosmic_ray_factor': args.post_flood_c14 * 2,  # Scale appropriately
        'equilibrium_delay': 1500 if args.model == "flood" else 2500,
        'water_vapor_shield': 0.7 if args.model == "flood" else 0.9
    }
    
    custom_model = sim.setup_custom_model(args.model, **model_params)
    
    # Run the simulation
    result = sim.run_simulation(
        args.age,
        args.depth,
        args.exposure,
        args.pressure,
        args.pre_flood_c14,
        args.post_flood_c14
    )
    
    # Display results
    print(format_output(result))
    
    # Export results if requested
    if args.export:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"simulation_results_{timestamp}.csv"
        curves_file = f"decay_curves_{timestamp}.csv"
        
        sim.export_to_csv(results_file)
        sim.export_curves_to_csv(curves_file)
        
        print(f"Results saved to {results_file}")
        print(f"Decay curves saved to {curves_file}")
    
    # Generate visualizations if requested
    if args.plot:
        # Get decay curves
        curves = sim.generate_decay_curves()
        
        if args.interactive:
            try:
                import plotly
                # Create interactive plot
                fig = viz.plot_interactive_decay_curves(curves, result)
                
                # Show plot in browser
                fig.show()
                
                # Save interactive plot if exporting
                if args.export:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    html_file = f"interactive_plot_{timestamp}.html"
                    fig.write_html(html_file)
                    print(f"Interactive plot saved to {html_file}")
            except ImportError:
                print("Plotly not available. Using Matplotlib instead.")
                args.interactive = False
        
        if not args.interactive:
            # Generate matplotlib plots
            # Decay curves plot
            fig1 = viz.plot_decay_curves_matplotlib(curves, show=False)
            
            # Batch simulation for age comparison
            true_ages, standard_dates, model_name = run_batch_simulation(args.model)
            fig2 = viz.plot_age_comparison(true_ages, standard_dates, model_name, 
                                          show=False)
            
            # Save plots if exporting
            if args.export:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                decay_plot = f"decay_curves_{timestamp}.png"
                comparison_plot = f"age_comparison_{timestamp}.png"
                
                fig1.savefig(decay_plot, dpi=300, bbox_inches='tight')
                fig2.savefig(comparison_plot, dpi=300, bbox_inches='tight')
                
                print(f"Decay curves plot saved to {decay_plot}")
                print(f"Age comparison plot saved to {comparison_plot}")
            
            # Show plots
            plt.show()

if __name__ == "__main__":
    main()
