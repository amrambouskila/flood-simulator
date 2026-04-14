import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_decay_curves_matplotlib(simulation_data, show=True, save_path=None):
    """
    Plot decay curves using Matplotlib
    
    Parameters:
    - simulation_data: DataFrame with age, standard_ratio, and custom_ratio columns
    - show: Whether to display the plot
    - save_path: Path to save the figure
    
    Returns:
    - Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot decay curves
    ax.plot(simulation_data['age'], simulation_data['standard_ratio'], 
            'b-', label='Standard Model')
    ax.plot(simulation_data['age'], simulation_data['custom_ratio'], 
            'r-', label=f'Custom Model')
    
    # Add labels and legend
    ax.set_xlabel('Age (years)')
    ax.set_ylabel('Remaining C-14 Ratio')
    ax.set_title('Carbon-14 Decay Curves: Standard vs. Custom Model')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # Set y-axis to log scale for better visualization of exponential decay
    ax.set_yscale('log')
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    # Show if requested
    if show:
        plt.show()
    
    return fig


def plot_age_comparison(true_ages, standard_dates, model_name, show=True, save_path=None):
    """
    Plot comparison between true ages and standard-dated ages
    
    Parameters:
    - true_ages: List of true ages
    - standard_dates: List of dates as calculated by standard model
    - model_name: Name of the custom model
    - show: Whether to display the plot
    - save_path: Path to save the figure
    
    Returns:
    - Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the comparison
    ax.scatter(true_ages, standard_dates, c='purple', alpha=0.6)
    
    # Add reference line (y = x, where dates would be equal)
    max_val = max(max(true_ages), max(standard_dates))
    ax.plot([0, max_val], [0, max_val], 'k--', label='Perfect Match')
    
    # Add labels and legend
    ax.set_xlabel('True Age (years)')
    ax.set_ylabel('Standard Carbon Date (years)')
    ax.set_title(f'True Age vs Standard Carbon Date\n(Using {model_name} assumptions)')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    # Show if requested
    if show:
        plt.show()
    
    return fig


def plot_interactive_decay_curves(simulation_data, result=None):
    """
    Create an interactive Plotly visualization of decay curves
    
    Parameters:
    - simulation_data: DataFrame with age, standard_ratio and custom_ratio columns
    - result: Optional dictionary with single simulation result for highlighting
    
    Returns:
    - Plotly figure object
    """
    # Create figure with secondary y-axis for age comparison
    fig = make_subplots(rows=2, cols=1, 
                       subplot_titles=("Carbon-14 Decay Curves", "Age Comparison"),
                       vertical_spacing=0.2)
    
    # Add decay curves to first subplot
    fig.add_trace(
        go.Scatter(
            x=simulation_data['age'], 
            y=simulation_data['standard_ratio'],
            name="Standard Model",
            line=dict(color="blue")
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=simulation_data['age'], 
            y=simulation_data['custom_ratio'],
            name="Custom Model",
            line=dict(color="red")
        ),
        row=1, col=1
    )
    
    # Add line where ratio values match to show error
    if result:
        true_age = result['true_age']
        standard_date = result['standard_date']
        measured_ratio = result['measured_c14_ratio']
        
        # Add vertical line at true age
        fig.add_trace(
            go.Scatter(
                x=[true_age, true_age], 
                y=[0, measured_ratio],
                name="True Age",
                line=dict(color="green", dash="dash")
            ),
            row=1, col=1
        )
        
        # Add vertical line at standard date
        fig.add_trace(
            go.Scatter(
                x=[standard_date, standard_date], 
                y=[0, measured_ratio],
                name="Standard Date",
                line=dict(color="purple", dash="dash")
            ),
            row=1, col=1
        )
        
        # Add horizontal line at measured ratio
        fig.add_trace(
            go.Scatter(
                x=[0, max(true_age, standard_date)], 
                y=[measured_ratio, measured_ratio],
                name="Measured Ratio",
                line=dict(color="gray", dash="dash")
            ),
            row=1, col=1
        )
        
        # Add point to second subplot showing the difference
        fig.add_trace(
            go.Scatter(
                x=[true_age], 
                y=[standard_date],
                mode="markers",
                marker=dict(size=12, color="red"),
                name="Simulation Point"
            ),
            row=2, col=1
        )
        
    # Add reference line to second subplot (y = x, where dates would be equal)
    max_age = simulation_data['age'].max()
    fig.add_trace(
        go.Scatter(
            x=[0, max_age], 
            y=[0, max_age],
            name="Perfect Match",
            line=dict(color="black", dash="dash")
        ),
        row=2, col=1
    )
    
    # Generate points for the curve in the second subplot
    ages = simulation_data['age']
    standard_dates = []
    # We use a subset of points to avoid overcrowding
    sample_points = np.linspace(0, len(ages)-1, 20).astype(int)
    for i in sample_points:
        if i < len(ages) and i >= 0:
            age = ages[i]
            ratio = simulation_data['custom_ratio'][i]
            # Calculate what standard dating would estimate for this ratio
            # Simplified calculation assuming standard half-life of 5730 years
            if ratio > 0:
                standard_date = -5730 * np.log(ratio) / np.log(2)
                standard_dates.append((age, standard_date))
    
    if standard_dates:
        x_vals, y_vals = zip(*standard_dates)
        fig.add_trace(
            go.Scatter(
                x=x_vals, 
                y=y_vals,
                mode="lines+markers",
                marker=dict(size=8),
                name="Model Curve",
                line=dict(color="orange")
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        title="Flood-Adjusted Carbon-14 Simulation",
        height=800,
        legend_title="Legend",
        hovermode="closest"
    )
    
    fig.update_yaxes(title_text="C-14 Ratio", type="log", row=1, col=1)
    fig.update_xaxes(title_text="Age (years)", row=1, col=1)
    
    fig.update_yaxes(title_text="Standard Carbon Date (years)", row=2, col=1)
    fig.update_xaxes(title_text="True Age (years)", row=2, col=1)
    
    return fig
