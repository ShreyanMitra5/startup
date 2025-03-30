from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
import json
import os
from datetime import datetime

app = Flask(__name__)

def detect_column_types(df):
    """Detect the type of each column in the dataframe"""
    column_types = {}
    for column in df.columns:
        try:
            # Check if column contains categorical data
            unique_ratio = df[column].nunique() / len(df)
            if unique_ratio < 0.5:  # If less than 50% unique values, consider it categorical
                column_types[column] = 'categorical'
            # Check if column contains numeric data
            elif pd.api.types.is_numeric_dtype(df[column]):
                column_types[column] = 'numeric'
            else:
                # Try to convert to numeric, if successful, mark as numeric
                try:
                    pd.to_numeric(df[column], errors='raise')
                    column_types[column] = 'numeric'
                except:
                    column_types[column] = 'text'
        except Exception as e:
            print(f"Error processing column {column}: {str(e)}")
            column_types[column] = 'text'  # Default to text if there's an error
    return column_types

def create_biased_data(df, column_types):
    """Create biased data based on detected column types"""
    try:
        biased_df = df.copy()
        
        # Find categorical columns that might represent sensitive attributes
        sensitive_columns = [col for col, type_ in column_types.items() 
                            if type_ == 'categorical' and 
                            any(sensitive in col.lower() for sensitive in ['gender', 'race', 'ethnicity', 'sex'])]
        
        # Find numeric columns that might represent scores or measurements
        numeric_columns = [col for col, type_ in column_types.items() 
                          if type_ == 'numeric' and 
                          any(metric in col.lower() for metric in ['score', 'rate', 'income', 'salary', 'amount'])]
        
        if sensitive_columns and numeric_columns:
            # Apply bias to numeric columns for each sensitive group
            for sensitive_col in sensitive_columns:
                try:
                    unique_values = biased_df[sensitive_col].unique()
                    if len(unique_values) >= 2:
                        # Apply bias to minority groups (assuming first value is majority)
                        minority_value = unique_values[1]
                        for numeric_col in numeric_columns:
                            try:
                                # Convert to numeric if not already
                                biased_df[numeric_col] = pd.to_numeric(biased_df[numeric_col], errors='coerce')
                                
                                # Reduce values for minority group
                                mask = biased_df[sensitive_col] == minority_value
                                if 'score' in numeric_col.lower() or 'rate' in numeric_col.lower():
                                    biased_df.loc[mask, numeric_col] = biased_df.loc[mask, numeric_col].apply(
                                        lambda x: max(x * 0.8, x - 20) if pd.notnull(x) else x
                                    )
                                elif 'income' in numeric_col.lower() or 'salary' in numeric_col.lower():
                                    biased_df.loc[mask, numeric_col] = biased_df.loc[mask, numeric_col].apply(
                                        lambda x: max(x * 0.9, x - 10000) if pd.notnull(x) else x
                                    )
                            except Exception as e:
                                print(f"Error processing numeric column {numeric_col}: {str(e)}")
                except Exception as e:
                    print(f"Error processing sensitive column {sensitive_col}: {str(e)}")
        
        return biased_df
    except Exception as e:
        print(f"Error in create_biased_data: {str(e)}")
        return df  # Return original dataframe if there's an error

def analyze_bias(data, column_types):
    """Analyze bias in the data based on detected column types"""
    try:
        df = pd.DataFrame(data)
        
        bias_metrics = {}
        bias_present = {}
        
        # Find sensitive columns
        sensitive_columns = [col for col, type_ in column_types.items() 
                            if type_ == 'categorical' and 
                            any(sensitive in col.lower() for sensitive in ['gender', 'race', 'ethnicity', 'sex'])]
        
        # Find numeric columns
        numeric_columns = [col for col, type_ in column_types.items() 
                          if type_ == 'numeric' and 
                          any(metric in col.lower() for metric in ['score', 'rate', 'income', 'salary', 'amount'])]
        
        if sensitive_columns and numeric_columns:
            for sensitive_col in sensitive_columns:
                try:
                    unique_values = df[sensitive_col].unique()
                    if len(unique_values) >= 2:
                        majority_value = unique_values[0]
                        minority_value = unique_values[1]
                        
                        bias_metrics[sensitive_col] = {}
                        bias_present[sensitive_col] = {}
                        
                        for numeric_col in numeric_columns:
                            try:
                                # Convert to numeric if not already
                                df[numeric_col] = pd.to_numeric(df[numeric_col], errors='coerce')
                                
                                majority_mean = float(df[df[sensitive_col] == majority_value][numeric_col].mean())
                                minority_mean = float(df[df[sensitive_col] == minority_value][numeric_col].mean())
                                
                                bias_metrics[sensitive_col][numeric_col] = {
                                    f'{majority_value}_mean': majority_mean,
                                    f'{minority_value}_mean': minority_mean
                                }
                                
                                # Determine if bias is present based on the type of metric
                                if 'score' in numeric_col.lower() or 'rate' in numeric_col.lower():
                                    threshold = 20
                                elif 'income' in numeric_col.lower() or 'salary' in numeric_col.lower():
                                    threshold = 10000
                                else:
                                    threshold = (majority_mean + minority_mean) / 2 * 0.1  # 10% difference
                                
                                bias_present[sensitive_col][numeric_col] = bool(abs(majority_mean - minority_mean) > threshold)
                            except Exception as e:
                                print(f"Error processing numeric column {numeric_col}: {str(e)}")
                except Exception as e:
                    print(f"Error processing sensitive column {sensitive_col}: {str(e)}")
        
        return bias_metrics, bias_present
    except Exception as e:
        print(f"Error in analyze_bias: {str(e)}")
        return {}, {}

def prepare_visualization_data(data, column_types):
    """Prepare visualization data based on detected column types"""
    try:
        df = pd.DataFrame(data)
        viz_data = {}
        
        # Add distribution for categorical columns
        categorical_columns = [col for col, type_ in column_types.items() if type_ == 'categorical']
        for col in categorical_columns:
            try:
                viz_data[f'{col}_distribution'] = df[col].value_counts().to_dict()
            except Exception as e:
                print(f"Error processing categorical column {col}: {str(e)}")
        
        # Add ranges for numeric columns
        numeric_columns = [col for col, type_ in column_types.items() if type_ == 'numeric']
        for col in numeric_columns:
            try:
                # Convert to numeric if not already
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                if 'score' in col.lower() or 'rate' in col.lower():
                    ranges = {
                        '0-20%': len(df[df[col] < 20]),
                        '20-40%': len(df[(df[col] >= 20) & (df[col] < 40)]),
                        '40-60%': len(df[(df[col] >= 40) & (df[col] < 60)]),
                        '60-80%': len(df[(df[col] >= 60) & (df[col] < 80)]),
                        '80-100%': len(df[df[col] >= 80])
                    }
                else:
                    # Calculate dynamic ranges based on data distribution
                    min_val = df[col].min()
                    max_val = df[col].max()
                    range_size = (max_val - min_val) / 4
                    ranges = {
                        f'{min_val:.0f}-{min_val+range_size:.0f}': len(df[df[col] < min_val+range_size]),
                        f'{min_val+range_size:.0f}-{min_val+2*range_size:.0f}': len(df[(df[col] >= min_val+range_size) & (df[col] < min_val+2*range_size)]),
                        f'{min_val+2*range_size:.0f}-{min_val+3*range_size:.0f}': len(df[(df[col] >= min_val+2*range_size) & (df[col] < min_val+3*range_size)]),
                        f'{min_val+3*range_size:.0f}-{max_val:.0f}': len(df[df[col] >= min_val+3*range_size])
                    }
                viz_data[f'{col}_ranges'] = ranges
            except Exception as e:
                print(f"Error processing numeric column {col}: {str(e)}")
        
        return viz_data
    except Exception as e:
        print(f"Error in prepare_visualization_data: {str(e)}")
        return {}

def calculate_differences(original_df, biased_df):
    """Calculate differences between original and biased data"""
    differences = {}
    
    # Get numeric columns
    numeric_columns = biased_df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_columns:
        # Calculate mean differences by gender
        gender_diffs = biased_df.groupby('gender')[col].mean() - original_df.groupby('gender')[col].mean()
        differences[col] = {
            'mean_differences': gender_diffs.to_dict(),
            'original_mean': original_df[col].mean(),
            'biased_mean': biased_df[col].mean(),
            'total_change': biased_df[col].mean() - original_df[col].mean()
        }
    
    return differences

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            # Read the CSV file
            print(f"Attempting to read file: {file.filename}")
            print(f"File content type: {file.content_type}")
            print(f"File size: {file.content_length} bytes")
            
            # Try to read the first few lines to check format
            file_content = file.read(1000).decode('utf-8')
            print(f"First 1000 characters of file:\n{file_content}")
            
            # Reset file pointer
            file.seek(0)
            
            # Read the CSV file
            df = pd.read_csv(file)
            print(f"Successfully read CSV with columns: {df.columns.tolist()}")
            print(f"DataFrame shape: {df.shape}")
            print(f"DataFrame info:\n{df.info()}")
            
            # Basic data cleaning
            print("Starting data cleaning...")
            # Remove rows where all values are NaN
            df = df.dropna(how='all')
            # Forward fill NaN values using the recommended method
            df = df.ffill()
            print(f"Data cleaning complete. Shape: {df.shape}")
            
            # Ensure all column names are strings and strip whitespace
            df.columns = df.columns.str.strip()
            
            # Detect column types
            print("Detecting column types...")
            column_types = detect_column_types(df)
            print(f"Detected column types: {column_types}")
            
            # Create biased data
            print("Creating biased data...")
            biased_df = create_biased_data(df, column_types)
            print("Biased data creation complete")
            
            # Calculate differences between original and biased data
            differences = calculate_differences(df, biased_df)
            print("Differences calculated:", differences)
            
            # Analyze bias for both original and biased data
            print("Analyzing bias in original data...")
            original_bias_metrics, original_bias_present = analyze_bias(df.to_dict('records'), column_types)
            print("Analyzing bias in biased data...")
            biased_bias_metrics, biased_bias_present = analyze_bias(biased_df.to_dict('records'), column_types)
            
            # Prepare visualization data for both datasets
            print("Preparing visualization data...")
            original_viz_data = prepare_visualization_data(df.to_dict('records'), column_types)
            biased_viz_data = prepare_visualization_data(biased_df.to_dict('records'), column_types)
            
            # Save biased data to a temporary file
            print("Saving biased data...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            biased_filename = f'biased_data_{timestamp}.csv'
            
            # Ensure the temp directory exists
            os.makedirs('static/temp', exist_ok=True)
            
            # Save the file
            biased_df.to_csv(f'static/temp/{biased_filename}', index=False)
            print("File saved successfully")
            
            return jsonify({
                'original': {
                    'bias_metrics': original_bias_metrics,
                    'bias_present': original_bias_present,
                    'visualization_data': original_viz_data
                },
                'biased': {
                    'bias_metrics': biased_bias_metrics,
                    'bias_present': biased_bias_present,
                    'visualization_data': biased_viz_data,
                    'download_link': f'/download/{biased_filename}'
                },
                'column_types': column_types,
                'original_data': df.to_dict('records'),
                'biased_data': biased_df.to_dict('records'),
                'differences': differences
            })
        except pd.errors.EmptyDataError:
            return jsonify({'error': 'The uploaded file is empty'}), 400
        except pd.errors.ParserError as e:
            return jsonify({
                'error': 'Invalid CSV format. Please check your file format.',
                'details': str(e)
            }), 400
        except UnicodeDecodeError:
            return jsonify({
                'error': 'File encoding error. Please ensure the file is UTF-8 encoded.',
                'details': 'The file appears to be in a different encoding format.'
            }), 400
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"Error processing file: {str(e)}")
            print(f"Full traceback: {error_traceback}")
            return jsonify({
                'error': f'Error processing file: {str(e)}',
                'details': error_traceback
            }), 500
    
    return jsonify({'error': 'Invalid file type. Please upload a CSV file.'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            f'static/temp/{filename}',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    # Create temp directory if it doesn't exist
    os.makedirs('static/temp', exist_ok=True)
    app.run(debug=True) 