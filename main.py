import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Union, Optional
from sklearn.preprocessing import StandardScaler
import random
import argparse
import os

class BiasInjector:
    def __init__(self, data: pd.DataFrame):
        self.original_data = data.copy()
        self.biased_data = data.copy()
        
    def inject_correlation_bias(self, 
                              target_col: str, 
                              feature_cols: List[str],
                              correlation_strength: float = 0.95) -> None:
        """
        Inject perfect correlation bias between target and features
        """
        if target_col not in self.biased_data.columns:
            raise ValueError(f"Target column {target_col} not found in data")
            
        for col in feature_cols:
            if col not in self.biased_data.columns:
                raise ValueError(f"Feature column {col} not found in data")
                
            # Create perfectly correlated data
            target_values = self.biased_data[target_col].values
            noise = np.random.normal(0, 0.1, len(target_values))
            self.biased_data[col] = correlation_strength * target_values + (1 - correlation_strength) * noise
            
    def inject_group_bias(self,
                         group_col: str,
                         target_col: str,
                         bias_strength: float = 0.8) -> None:
        """
        Inject systematic bias between groups
        """
        if group_col not in self.biased_data.columns or target_col not in self.biased_data.columns:
            raise ValueError("Group or target column not found in data")
            
        groups = self.biased_data[group_col].unique()
        if len(groups) != 2:
            raise ValueError("Group bias injection currently supports binary groups only")
            
        # Create systematic difference between groups
        for group in groups:
            mask = self.biased_data[group_col] == group
            if group == groups[0]:
                self.biased_data.loc[mask, target_col] *= (1 + bias_strength)
            else:
                self.biased_data.loc[mask, target_col] *= (1 - bias_strength)
                
    def inject_selection_bias(self,
                            selection_col: str,
                            threshold: float,
                            direction: str = 'above') -> None:
        """
        Inject selection bias by filtering data based on a threshold
        """
        if selection_col not in self.biased_data.columns:
            raise ValueError(f"Selection column {selection_col} not found in data")
            
        if direction == 'above':
            mask = self.biased_data[selection_col] > threshold
        else:
            mask = self.biased_data[selection_col] < threshold
            
        self.biased_data = self.biased_data[mask].copy()
        
    def inject_temporal_bias(self,
                           time_col: str,
                           target_col: str,
                           trend_strength: float = 0.5) -> None:
        """
        Inject temporal bias by adding a systematic trend
        """
        if time_col not in self.biased_data.columns or target_col not in self.biased_data.columns:
            raise ValueError("Time or target column not found in data")
            
        # Convert time column to numeric if it's not already
        if not np.issubdtype(self.biased_data[time_col].dtype, np.number):
            self.biased_data[time_col] = pd.to_datetime(self.biased_data[time_col])
            self.biased_data[time_col] = self.biased_data[time_col].astype(np.int64)
            
        # Add systematic trend
        time_values = self.biased_data[time_col].values
        trend = np.linspace(0, trend_strength, len(time_values))
        self.biased_data[target_col] *= (1 + trend)
        
    def visualize_bias(self,
                      col1: str,
                      col2: str,
                      output_path: Optional[str] = None,
                      title: str = "Bias Visualization") -> None:
        """
        Visualize the bias between two columns
        """
        plt.figure(figsize=(12, 6))
        
        # Plot original data
        plt.subplot(1, 2, 1)
        sns.scatterplot(data=self.original_data, x=col1, y=col2, alpha=0.5)
        plt.title("Original Data")
        
        # Plot biased data
        plt.subplot(1, 2, 2)
        sns.scatterplot(data=self.biased_data, x=col1, y=col2, alpha=0.5)
        plt.title("Biased Data")
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            plt.close()
        else:
            plt.show()

def parse_args():
    parser = argparse.ArgumentParser(description='Generate biased datasets for AI stress testing')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('--output', '-o', default='biased_data.csv', help='Output CSV file path')
    parser.add_argument('--correlation', '-c', action='store_true', help='Apply correlation bias')
    parser.add_argument('--correlation-target', help='Target column for correlation bias')
    parser.add_argument('--correlation-features', nargs='+', help='Feature columns for correlation bias')
    parser.add_argument('--correlation-strength', type=float, default=0.95, help='Correlation strength (0-1)')
    
    parser.add_argument('--group-bias', '-g', action='store_true', help='Apply group bias')
    parser.add_argument('--group-column', help='Column containing group labels')
    parser.add_argument('--group-target', help='Target column for group bias')
    parser.add_argument('--group-strength', type=float, default=0.8, help='Group bias strength')
    
    parser.add_argument('--selection-bias', '-s', action='store_true', help='Apply selection bias')
    parser.add_argument('--selection-column', help='Column for selection bias')
    parser.add_argument('--selection-threshold', type=float, help='Threshold for selection bias')
    parser.add_argument('--selection-direction', choices=['above', 'below'], default='above', help='Selection direction')
    
    parser.add_argument('--temporal-bias', '-t', action='store_true', help='Apply temporal bias')
    parser.add_argument('--time-column', help='Time column for temporal bias')
    parser.add_argument('--temporal-target', help='Target column for temporal bias')
    parser.add_argument('--trend-strength', type=float, default=0.5, help='Temporal trend strength')
    
    parser.add_argument('--visualize', '-v', action='store_true', help='Generate visualizations')
    parser.add_argument('--plot-columns', nargs=2, help='Columns to plot (x y)')
    parser.add_argument('--plot-output', help='Output path for visualization plot')
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Load input data
    print(f"Loading data from {args.input_file}...")
    df = pd.read_csv(args.input_file)
    injector = BiasInjector(df)
    
    # Apply requested biases
    print("Applying biases...")
    
    if args.correlation:
        if not args.correlation_target or not args.correlation_features:
            raise ValueError("Correlation bias requires --correlation-target and --correlation-features")
        injector.inject_correlation_bias(
            args.correlation_target,
            args.correlation_features,
            args.correlation_strength
        )
    
    if args.group_bias:
        if not args.group_column or not args.group_target:
            raise ValueError("Group bias requires --group-column and --group-target")
        injector.inject_group_bias(
            args.group_column,
            args.group_target,
            args.group_strength
        )
    
    if args.selection_bias:
        if not args.selection_column or args.selection_threshold is None:
            raise ValueError("Selection bias requires --selection-column and --selection-threshold")
        injector.inject_selection_bias(
            args.selection_column,
            args.selection_threshold,
            args.selection_direction
        )
    
    if args.temporal_bias:
        if not args.time_column or not args.temporal_target:
            raise ValueError("Temporal bias requires --time-column and --temporal-target")
        injector.inject_temporal_bias(
            args.time_column,
            args.temporal_target,
            args.trend_strength
        )
    
    # Save biased dataset
    print(f"Saving biased dataset to {args.output}...")
    injector.biased_data.to_csv(args.output, index=False)
    
    # Generate visualization if requested
    if args.visualize:
        if not args.plot_columns:
            raise ValueError("Visualization requires --plot-columns")
        print("Generating visualization...")
        injector.visualize_bias(
            args.plot_columns[0],
            args.plot_columns[1],
            args.plot_output
        )
    
    print("Done!")

if __name__ == "__main__":
    main()
