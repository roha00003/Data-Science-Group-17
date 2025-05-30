import pandas as pd
import argparse
import matplotlib.pyplot as plt

#Write results to file
def write_results(path,results):
    with open(path,"w") as f:
        f.write(results)

#Check Hospital Service Area
def count_clm(df,pos,output):
    # Get the first column (by position)
    first_column = df.iloc[:, pos]

    # Count occurrences
    counts = first_column.value_counts()

    # Print result
    write_results("output\\statistic\\"+output+".txt",str(counts))

def count_rel_clm(df,pos1,pos2,output):
    # Group by first column and count values in second column
    counts = df.groupby(df.columns[pos1])[df.columns[pos2]].value_counts()

    # Optional: convert to DataFrame
    counts_df = counts.reset_index(name='count')

    # Print result
    write_results("output\\statistic\\"+output+".txt",str(counts))

def costs(df,pos,output):
    total_charges = pd.to_numeric(df.iloc[:, pos], errors='coerce')  # Convert to numeric, handle non-numeric safely
    raw_charges = df.iloc[:, pos].astype(str)
    clean_charges = pd.to_numeric(raw_charges.str.replace(",", ""), errors='coerce')
    clean_charges = clean_charges.dropna()
    # Drop NaN values (in case of blanks or non-numeric entries)
    total_charges = total_charges.dropna()

    # Calculate stats
    min_val = clean_charges.min()
    max_val = clean_charges.max()
    mean_val = clean_charges.mean()
    results=f"Min: {min_val}\nMax: {max_val}\nMean: {mean_val}"
    # Print result
    write_results("output\\statistic\\"+output+".txt",str(results))

def plot_cost(df,pos,output):
    raw_charges = df.iloc[:, pos].astype(str)
    clean_charges = pd.to_numeric(raw_charges.str.replace(",", ""), errors='coerce').dropna()
    
    bins = [0, 10000, 50000, 100000, 250000, 500000, 1000000, clean_charges.max()]
    labels = ['<10K', '10K–50K', '50K–100K', '100K–250K', '250K–500K', '500K–1M', '1M+']

    # Group data into bins
    binned = pd.cut(clean_charges, bins=bins, labels=labels, right=False)
    grouped = binned.value_counts().sort_index()

    # Plot as a bar chart
    plt.figure(figsize=(10, 6))
    grouped.plot(kind='bar', edgecolor='black')
    plt.title("Total Charges Grouped by Range")
    plt.xlabel("Charge Range")
    plt.ylabel("Number of Records")
    plt.grid(axis='y')

    # Save the plot
    plt.tight_layout()
    plt.savefig("output\\statistic\\"+output+".png", dpi=300, bbox_inches='tight')
'''
#parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--output", required = True)
args = parser.parse_args()

#create output directory
output= "output\\statistic\\"+args.output+".txt"
'''
pd.set_option('display.max_rows', None)
#read data
df = pd.read_csv("data\Topic 4\Hospital_Inpatient_Discharges__SPARCS_De-Identified___2022_20250423.csv")
#count_clm(df,30,"emergency-department-indicator")
#count_rel_clm(df,22,23,"mdc-description")
#costs(df,32,"total-costs")
plot_cost(df,32,"total-cost")