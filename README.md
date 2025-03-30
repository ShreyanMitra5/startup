# Perfectly Biased Dataset Generator

This tool helps you create "perfectly biased" datasets for stress-testing AI models. It systematically injects various types of biases into real-world datasets while maintaining a realistic appearance.

## Features

- Correlation Bias: Creates unrealistically perfect correlations between features
- Group Bias: Injects systematic differences between groups
- Selection Bias: Filters data based on specific criteria
- Temporal Bias: Adds systematic trends over time
- Visualization tools to compare original and biased data

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The tool is now a command-line interface that takes a CSV file as input and generates biased versions with your specified parameters.

Basic usage:
```bash
python main.py input.csv [options]
```

### Command Line Options

#### Required Arguments
- `input_file`: Path to the input CSV file

#### Optional Arguments
- `--output`, `-o`: Output CSV file path (default: biased_data.csv)

#### Correlation Bias
- `--correlation`, `-c`: Apply correlation bias
- `--correlation-target`: Target column for correlation bias
- `--correlation-features`: Feature columns for correlation bias (space-separated)
- `--correlation-strength`: Correlation strength (0-1, default: 0.95)

#### Group Bias
- `--group-bias`, `-g`: Apply group bias
- `--group-column`: Column containing group labels
- `--group-target`: Target column for group bias
- `--group-strength`: Group bias strength (default: 0.8)

#### Selection Bias
- `--selection-bias`, `-s`: Apply selection bias
- `--selection-column`: Column for selection bias
- `--selection-threshold`: Threshold for selection bias
- `--selection-direction`: Selection direction ('above' or 'below', default: 'above')

#### Temporal Bias
- `--temporal-bias`, `-t`: Apply temporal bias
- `--time-column`: Time column for temporal bias
- `--temporal-target`: Target column for temporal bias
- `--trend-strength`: Temporal trend strength (default: 0.5)

#### Visualization
- `--visualize`, `-v`: Generate visualizations
- `--plot-columns`: Columns to plot (x y)
- `--plot-output`: Output path for visualization plot

### Examples

1. Apply correlation bias:
```bash
python main.py input.csv --correlation --correlation-target income --correlation-features age education --correlation-strength 0.9
```

2. Apply group bias:
```bash
python main.py input.csv --group-bias --group-column gender --group-target salary --group-strength 0.3
```

3. Apply selection bias:
```bash
python main.py input.csv --selection-bias --selection-column score --selection-threshold 70 --selection-direction above
```

4. Apply temporal bias:
```bash
python main.py input.csv --temporal-bias --time-column date --temporal-target sales --trend-strength 0.2
```

5. Generate visualization:
```bash
python main.py input.csv --visualize --plot-columns income age --plot-output bias_plot.png
```

6. Combine multiple biases:
```bash
python main.py input.csv \
    --correlation --correlation-target income --correlation-features education \
    --group-bias --group-column gender --group-target salary \
    --visualize --plot-columns income education --plot-output combined_bias.png
```

## Warning

This tool is designed for testing AI model robustness and bias detection. The generated datasets contain artificial biases that may not reflect real-world patterns. Use responsibly and transparently when testing AI models. 