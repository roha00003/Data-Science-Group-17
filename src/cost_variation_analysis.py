import matplotlib
matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False

# Suppress all matplotlib font warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', message='.*font.*')
warnings.filterwarnings('ignore', message='.*Glyph.*')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import os
import glob

# Suppress matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

class CostVariationAnalyzer:
    def __init__(self, csv_path):
       
        self.csv_path = csv_path
        self.df = None
        self.load_data()
        if self.df is not None:
            self.prepare_data()
            self.create_output_dirs()
    
    def load_data(self):
       
        try:
            # Check if the exact file exists
            if os.path.exists(self.csv_path):
                print(f"Loading file: {self.csv_path}")
                self.df = pd.read_csv(self.csv_path)
                print(f"Successfully loaded {len(self.df)} rows")
                return
            
            # If exact path doesn't exist, try to find CSV files in the data directory
            data_dir = os.path.dirname(self.csv_path) if os.path.dirname(self.csv_path) else "./data"
            csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
            
            if csv_files:
                print(f"Found CSV files in {data_dir}:")
                for i, file in enumerate(csv_files):
                    print(f"{i+1}. {os.path.basename(file)}")
                
                # Try to load the first CSV file
                self.csv_path = csv_files[0]
                print(f"\nTrying to load: {self.csv_path}")
                self.df = pd.read_csv(self.csv_path)
                print(f"Successfully loaded {len(self.df)} rows")
            else:
                print(f"No CSV files found in {data_dir}")
               
                
        except FileNotFoundError:
            print(f"Error: File not found at {self.csv_path}")
         
       
    
    def create_output_dirs(self):
        
        os.makedirs("output/analysis", exist_ok=True)
        os.makedirs("output/analysis/plots", exist_ok=True)
    
    def prepare_data(self):
        
        if self.df is None:
            return
            
        
        
        # Clean cost data
        cost_cols = ['Total Charges', 'Total Costs']
        for col in cost_cols:
            if col in self.df.columns:
             
                # More robust cleaning
                self.df[col + '_clean'] = (
                    self.df[col]
                    .astype(str)
                    .str.replace(r'[\$,]', '', regex=True)
                    .replace('', np.nan)
                )
                self.df[col + '_clean'] = pd.to_numeric(
                    self.df[col + '_clean'], 
                    errors='coerce'
                )
        
        # Remove outliers (top 1% and bottom 1% for costs)
        for col in ['Total Charges_clean', 'Total Costs_clean']:
            if col in self.df.columns:
                # Only calculate quantiles for non-null values
                valid_data = self.df[col].dropna()
                if len(valid_data) > 0:
                    q1 = valid_data.quantile(0.01)
                    q99 = valid_data.quantile(0.99)
                    self.df[col + '_filtered'] = self.df[col].where(
                        (self.df[col] >= q1) & (self.df[col] <= q99)
                    )
                    print(f"Filtered {col}: removed outliers outside ${q1:,.2f} - ${q99:,.2f}")
    
    def _save_plot_safely(self, filename, title=""):
      
        try:
            plt.figure(figsize=(12, 8))
            if title:
                plt.suptitle(title, fontsize=14, y=0.95)
            plt.tight_layout()
            plt.savefig(f'output/analysis/plots/{filename}', 
                       dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            return True
        except Exception as e:
            print(f"Error saving plot {filename}: {e}")
            plt.close()
            return False
    
    def analyze_regional_variations(self):
       
       
    
        results = []
    
        # 1. Hospital Service Area Analysis
        if 'Hospital Service Area' in self.df.columns and 'Total Costs_clean' in self.df.columns:
            hsa_data = self.df.dropna(subset=['Hospital Service Area', 'Total Costs_clean'])
        
            if len(hsa_data) > 0:
                hsa_costs = hsa_data.groupby('Hospital Service Area')['Total Costs_clean'].agg([
                    'count', 'mean', 'median', 'std'
                ]).round(2)
            
                results.append("1. Costs By Hospital Service Area")
                results.append(str(hsa_costs))
                results.append("")
            
                # Statistical test (ANOVA) 
                try:
                    hsa_groups = [group['Total Costs_clean'].dropna().values 
                                 for name, group in hsa_data.groupby('Hospital Service Area')]
                    hsa_groups = [group for group in hsa_groups if len(group) > 5]  # At least 5 observations
                
                    if len(hsa_groups) > 1:
                        f_stat, p_value = stats.f_oneway(*hsa_groups)
                        results.append(f"ANOVA F-Statistic: {f_stat:.4f}, p-value: {p_value:.4f}")
                        if p_value < 0.05:
                            results.append("Result: Significant differences between regions (p < 0.05)")
                        else:
                            results.append("Result: No significant differences between regions (p >= 0.05)")
                        results.append("")
                except Exception as e:
                    results.append(f"ANOVA test failed: {e}")
                    results.append("")
            
               
                try:
                    # Prepare data for all analyses
                    hsa_data_viz = None
                    county_data = None  
                    zip_data = None

                    if 'Hospital Service Area' in self.df.columns and 'Total Costs_clean' in self.df.columns:
                        hsa_data_viz = self.df.dropna(subset=['Hospital Service Area', 'Total Costs_clean'])
                        if len(hsa_data_viz) == 0:
                            hsa_data_viz = None

                    if 'Hospital County' in self.df.columns and 'Total Costs_clean' in self.df.columns:
                        county_data = self.df.dropna(subset=['Hospital County', 'Total Costs_clean'])
                        if len(county_data) == 0:
                            county_data = None

                    if 'Zip Code - 3 digits' in self.df.columns and 'Total Costs_clean' in self.df.columns:
                        zip_data = self.df[
                            (self.df['Zip Code - 3 digits'].notna()) & 
                            (self.df['Zip Code - 3 digits'] != '') &
                            (self.df['Total Costs_clean'].notna())
                        ]
                        if len(zip_data) == 0:
                            zip_data = None

                    # FIGURE SETUP 
                    plt.style.use('seaborn-v0_8-whitegrid')  # Use modern style
                    fig = plt.figure(figsize=(20, 16))  # Adjusted size for 2x2 layout

                    #  color palettes
                    primary_colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83', 
                                     '#0D7377', '#14A085', '#7B2D26', '#5D737E', '#F4B942']
                    secondary_colors = plt.cm.Set3(np.linspace(0, 1, 12))
                    accent_colors = plt.cm.viridis(np.linspace(0.1, 0.9, 15))

                    plot_count = 0

                    # PLOT 1: HSA Boxplot Analysis 
                    if hsa_data_viz is not None and len(hsa_data_viz) > 0:
                        ax1 = plt.subplot(2, 2, 1)
    
                        # Create boxplot data 
                        box_data = []
                        labels = []
                        hsa_summary = hsa_data_viz.groupby('Hospital Service Area')['Total Costs_clean'].agg(['mean', 'count'])
                        hsa_summary = hsa_summary.sort_values('mean', ascending=False)  # Sort by mean cost
    
                        for name in hsa_summary.index:
                            group_data = hsa_data_viz[hsa_data_viz['Hospital Service Area'] == name]['Total Costs_clean'].dropna().values
                            if len(group_data) > 0:
                                box_data.append(group_data)
                                # Truncate long names for better readability
                                display_name = name[:15] + '...' if len(name) > 15 else name
                                labels.append(f"{display_name}\n(n={len(group_data)})")
    
                        if len(box_data) > 0:
                            bp = plt.boxplot(box_data, tick_labels=labels, patch_artist=True, 
                                            widths=0.7, 
                                            boxprops=dict(linewidth=2.5, alpha=0.85),
                                            whiskerprops=dict(linewidth=2.5, color='#34495E'),
                                            capprops=dict(linewidth=2.5, color='#34495E'),
                                            medianprops=dict(linewidth=3.5, color='white'),
                                            flierprops=dict(marker='o', markerfacecolor='#E74C3C', 
                                                          markersize=5, alpha=0.7, markeredgecolor='white'))
        
                            # Apply gradient colors
                            for i, patch in enumerate(bp['boxes']):
                                patch.set_facecolor(primary_colors[i % len(primary_colors)])
                                patch.set_edgecolor('#2C3E50')
        
                            plt.title('Healthcare Costs by Hospital Service Area', 
                                     fontsize=18, fontweight='bold', color='#2C3E50', pad=20)
                            plt.ylabel('Total Costs (USD)', fontsize=16, fontweight='bold', color='#2C3E50')
                            plt.xticks(rotation=45, ha='right', fontsize=12)
        
                            #  formatting
                            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K' if x >= 1000 else f'${x:.0f}'))
                            ax1.set_facecolor('#FAFBFC')
                            ax1.grid(True, axis='y', alpha=0.4, linestyle='--', color='#BDC3C7', linewidth=1)
        
                            # statistics box
                            total_cases = sum(len(data) for data in box_data)
                            avg_cost = np.mean([np.mean(data) for data in box_data])
                            max_cost = max([np.max(data) for data in box_data])
                            min_cost = min([np.min(data) for data in box_data])
        
                            stats_text = f'Total Cases: {total_cases:,}\nRegions: {len(box_data)}\nAvg: ${avg_cost:,.0f}\nRange: ${min_cost:,.0f} - ${max_cost:,.0f}'
                            plt.text(0.02, 0.98, stats_text, 
                                    transform=ax1.transAxes, verticalalignment='top',
                                    bbox=dict(boxstyle='round,pad=0.8', facecolor='white', alpha=0.95, edgecolor='#34495E'),
                                    fontsize=11, fontweight='bold', color='#2C3E50')
        
                            plot_count += 1

                    # PLOT 2: HSA Mean Costs 
                    if hsa_data_viz is not None and len(hsa_data_viz) > 0:
                        ax2 = plt.subplot(2, 2, 2)
    
                        # Filter out any negative costs and calculate statistics
                        hsa_filtered = hsa_data_viz[hsa_data_viz['Total Costs_clean'] >= 0]  # Remove negatives
                        hsa_means = hsa_filtered.groupby('Hospital Service Area')['Total Costs_clean'].agg(['mean', 'count', 'std'])
                        hsa_means = hsa_means[hsa_means['count'] >= 5]  # At least 5 cases for reliability
                        hsa_means = hsa_means.sort_values('mean', ascending=False)
    
                        if len(hsa_means) > 0:
                            # Create gradient effect
                            norm = plt.Normalize(vmin=hsa_means['mean'].min(), vmax=hsa_means['mean'].max())
                            colors_mapped = plt.cm.RdYlBu_r(norm(hsa_means['mean']))
        
                            bars = plt.bar(range(len(hsa_means)), hsa_means['mean'], 
                                          color=colors_mapped, alpha=0.85, 
                                          edgecolor='#2C3E50', linewidth=2)
        
                            # Add error bars for standard deviation (ensure no negative values)
                            std_values = hsa_means['std'].fillna(0)  # Replace NaN with 0
                            plt.errorbar(range(len(hsa_means)), hsa_means['mean'], 
                                        yerr=std_values, fmt='none', 
                                        ecolor='#34495E', capsize=5, capthick=2, alpha=0.7)
        
                            plt.title('Average Costs by Hospital Service Area\n(Positive Values Only, Min 5 Cases)', 
                                     fontsize=18, fontweight='bold', color='#2C3E50', pad=20)
                            plt.ylabel('Average Cost (USD)', fontsize=16, fontweight='bold', color='#2C3E50')
        
                            # x-axis labels
                            x_labels = [name[:12] + '...' if len(name) > 12 else name for name in hsa_means.index]
                            plt.xticks(range(len(hsa_means)), x_labels, rotation=45, ha='right', fontsize=12)
        
                            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K' if x >= 1000 else f'${x:.0f}'))
                            ax2.set_facecolor('#FAFBFC')
                            ax2.grid(True, axis='y', alpha=0.4, linestyle='--', color='#BDC3C7', linewidth=1)
            
                            # Set y-axis to start from 0 to avoid negative display
                            ax2.set_ylim(bottom=0)
        
                            # value labels with background
                            for i, bar in enumerate(bars):
                                height = bar.get_height()
                                case_count = hsa_means.iloc[i]['count']
                                plt.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                                        f'${height/1000:.0f}K\n({case_count:,})', 
                                        ha='center', va='bottom', fontsize=10, fontweight='bold',
                                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
                            plot_count += 1

                    # PLOT 3: County Analysis 
                    if county_data is not None and len(county_data) > 0:
                        ax3 = plt.subplot(2, 2, 3)
    
                        # Filter out negative costs
                        county_filtered = county_data[county_data['Total Costs_clean'] >= 0]
                        county_costs = county_filtered.groupby('Hospital County')['Total Costs_clean'].agg([
                            'count', 'mean', 'median', 'std'
                        ]).round(2)
                        county_costs = county_costs[county_costs['count'] >= 10]  # At least 10 cases
                        top_counties = county_costs.sort_values('mean', ascending=True).tail(15)  # Bottom-up for horizontal
    
                        if len(top_counties) > 0:
                            y_pos = np.arange(len(top_counties))
        
                            # Create gradient colors
                            norm = plt.Normalize(vmin=top_counties['mean'].min(), vmax=top_counties['mean'].max())
                            colors_county = plt.cm.plasma(norm(top_counties['mean']))
        
                            bars = plt.barh(y_pos, top_counties['mean'], 
                                           color=colors_county, alpha=0.85, 
                                           edgecolor='#2C3E50', linewidth=1.5)
        
                            # county labels
                            labels = []
                            for county in top_counties.index:
                                if len(county) > 18:
                                    labels.append(county[:15] + '...')
                                else:
                                    labels.append(county)
        
                            plt.yticks(y_pos, labels, fontsize=12)
                            plt.xlabel('Average Cost (USD)', fontsize=16, fontweight='bold', color='#2C3E50')
                            plt.title('Top 15 Counties by Average Cost\n(Positive Values, Min 10 Cases)', 
                                     fontsize=18, fontweight='bold', color='#2C3E50', pad=20)
        
                            ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K' if x >= 1000 else f'${x:.0f}'))
                            ax3.set_facecolor('#FAFBFC')
                            ax3.grid(True, axis='x', alpha=0.4, linestyle='--', color='#BDC3C7', linewidth=1)
        
                            # value labels
                            for i, bar in enumerate(bars):
                                width = bar.get_width()
                                case_count = top_counties.iloc[i]['count']
                                plt.text(width + max(top_counties['mean']) * 0.02, 
                                        bar.get_y() + bar.get_height()/2, 
                                        f'${width/1000:.0f}K\n({case_count:,})', 
                                        ha='left', va='center', fontsize=10, fontweight='bold',
                                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
                            plot_count += 1

                    # PLOT 4: ZIP Code Analysis 
                    if zip_data is not None and len(zip_data) > 0:
                        ax4 = plt.subplot(2, 2, 4)
    
                        # Filter out negative costs
                        zip_filtered = zip_data[zip_data['Total Costs_clean'] >= 0]
                        zip_costs = zip_filtered.groupby('Zip Code - 3 digits')['Total Costs_clean'].agg([
                            'count', 'mean', 'median', 'std'
                        ]).round(2)
                        zip_costs = zip_costs[zip_costs['count'] >= 50]  # At least 50 cases
                        top_zips = zip_costs.sort_values('mean', ascending=False).head(12)  # Top 12 for better spacing
    
                        if len(top_zips) > 0:
                            # Create gradient
                            norm = plt.Normalize(vmin=top_zips['mean'].min(), vmax=top_zips['mean'].max())
                            colors_zip = plt.cm.viridis(norm(top_zips['mean']))
        
                            bars = plt.bar(range(len(top_zips)), top_zips['mean'], 
                                          color=colors_zip, alpha=0.85, 
                                          edgecolor='#2C3E50', linewidth=2)
        
                            plt.title('Top 12 ZIP Areas by Average Cost\n(Positive Values, Min 50 Cases)', 
                                     fontsize=18, fontweight='bold', color='#2C3E50', pad=20)
                            plt.xlabel('ZIP Code (First 3 Digits)', fontsize=16, fontweight='bold', color='#2C3E50')
                            plt.ylabel('Average Cost (USD)', fontsize=16, fontweight='bold', color='#2C3E50')
        
                            plt.xticks(range(len(top_zips)), top_zips.index, rotation=0, fontsize=12, fontweight='bold')
                            ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K' if x >= 1000 else f'${x:.0f}'))
                            ax4.set_facecolor('#FAFBFC')
                            ax4.grid(True, axis='y', alpha=0.4, linestyle='--', color='#BDC3C7', linewidth=1)
            
                            # Set y-axis to start from 0
                            ax4.set_ylim(bottom=0)
        
                            # value labels
                            for i, bar in enumerate(bars):
                                height = bar.get_height()
                                case_count = top_zips.iloc[i]['count']
                                plt.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                                        f'${height/1000:.0f}K\n({case_count:,})', 
                                        ha='center', va='bottom', fontsize=10, fontweight='bold',
                                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
                            plot_count += 1

                    # OVERALL STYLING 
                    if plot_count > 0:
                        # Main title 
                        fig.suptitle('Regional Healthcare Cost Analysis Dashboard', 
                                     fontsize=26, fontweight='bold', color='#2C3E50', y=0.96)
    
                        # Add subtitle 
                        subtitle_text = "Geographic variations in healthcare costs across service areas, counties, and ZIP codes"
                        fig.text(0.5, 0.92, subtitle_text, ha='center', fontsize=16, 
                                color='#5D6D7E', style='italic')
    
                        # subplot borders and styling
                        for ax in fig.get_axes():
                            for spine in ax.spines.values():
                                spine.set_edgecolor('#34495E')
                                spine.set_linewidth(2)
                            ax.tick_params(colors='#2C3E50', which='both')
                            ax.xaxis.label.set_color('#2C3E50')
                            ax.yaxis.label.set_color('#2C3E50')
    
                        # layout for 2x2 grid
                        plt.tight_layout()
                        plt.subplots_adjust(top=0.88, bottom=0.08, left=0.08, right=0.95, 
                                           hspace=0.35, wspace=0.25)
    
                        # Save 
                        plt.savefig('output/analysis/plots/regional_cost_variations.png', 
                                   dpi=300, bbox_inches='tight', facecolor='white', 
                                   edgecolor='none', pad_inches=0.2)
           
                    else:
                        print("⚠ No regional data available for visualization")

                    plt.close()

                except Exception as e:
                    print(f"Regional visualization failed: {e}")
                    import traceback
                    traceback.print_exc()
                    plt.close()

        # 2. County Analysis 
        if 'Hospital County' in self.df.columns and 'Total Costs_clean' in self.df.columns:
            county_data = self.df.dropna(subset=['Hospital County', 'Total Costs_clean'])
        
            if len(county_data) > 0:
                county_costs = county_data.groupby('Hospital County')['Total Costs_clean'].agg([
                    'count', 'mean', 'median', 'std'
                ]).round(2)
            
                # Only show counties with at least 10 cases
                county_costs = county_costs[county_costs['count'] >= 10]
            
                results.append("2. Costs By County (Top 15, minimum 10 cases):")
                county_top = county_costs.sort_values('mean', ascending=False).head(15)
                results.append(str(county_top))
                results.append("")
    
        # 3. ZIP Code Analysis
        if 'Zip Code - 3 digits' in self.df.columns and 'Total Costs_clean' in self.df.columns:
            zip_data = self.df[
                (self.df['Zip Code - 3 digits'].notna()) & 
                (self.df['Zip Code - 3 digits'] != '') &
                (self.df['Total Costs_clean'].notna())
            ]
        
            if len(zip_data) > 0:
                zip_costs = zip_data.groupby('Zip Code - 3 digits')['Total Costs_clean'].agg([
                    'count', 'mean', 'median', 'std'
                ]).round(2)
                zip_costs = zip_costs[zip_costs['count'] >= 50]  # At least 50 cases
            
                results.append("3. Costs By ZIP Code (Top 15, minimum 50 cases):")
                zip_top = zip_costs.sort_values('mean', ascending=False).head(15)
                results.append(str(zip_top))
                results.append("")
    
        # Save results
        try:
            with open('output/analysis/regional_analysis.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(results))
        except Exception as e:
            print(f"Error saving regional analysis: {e}")
    
        return results
    
    def analyze_hospital_specializations(self):
        
      
        
       
    
        results = []
    
        # 1. APR-DRG Analysis (Diagnosis Related Groups)
        if 'APR DRG Description' in self.df.columns and 'Total Costs_clean' in self.df.columns:
            drg_data = self.df.dropna(subset=['APR DRG Description', 'Total Costs_clean'])
        
            if len(drg_data) > 0:
                drg_costs = drg_data.groupby('APR DRG Description')['Total Costs_clean'].agg([
                    'count', 'mean', 'median', 'std'
                ]).round(2)
                drg_costs = drg_costs[drg_costs['count'] >= 30]  # At least 30 cases
            
                results.append("1. Costs By Diagnosis Related Groups (Top 20, minimum 30 cases):")
                drg_top = drg_costs.sort_values('mean', ascending=False).head(20)
                results.append(str(drg_top))
                results.append("")
    
        # 2. Major Diagnostic Category (MDC) Analysis
        if 'APR MDC Description' in self.df.columns and 'Total Costs_clean' in self.df.columns:
            mdc_data = self.df.dropna(subset=['APR MDC Description', 'Total Costs_clean'])
        
            if len(mdc_data) > 0:
                mdc_costs = mdc_data.groupby('APR MDC Description')['Total Costs_clean'].agg([
                    'count', 'mean', 'median', 'std'
                ]).round(2)
            
                results.append("2. Costs By Major Diagnostic Category:")
                mdc_sorted = mdc_costs.sort_values('mean', ascending=False)
                results.append(str(mdc_sorted))
                results.append("")
            
                # Combined visualization 
                try:
                    # Create a single figure with multiple subplots
                    fig = plt.figure(figsize=(20, 12))
                    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1.2, 1])
                
                    # Get top DRGs for plotting
                    top_drgs = drg_costs.sort_values('mean', ascending=False).head(15)
                
                    if len(top_drgs) > 0:
                        # Top left: DRG horizontal bar chart
                        ax1 = fig.add_subplot(gs[0, 0])
                        y_pos = np.arange(len(top_drgs))

                        # Create gradient colors
                        colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(top_drgs)))

                        bars = ax1.barh(y_pos, top_drgs['mean'], 
                                       color=colors, alpha=0.8, edgecolor='#2C3E50', linewidth=1)

                        # Truncate long descriptions
                        labels = []
                        for desc in top_drgs.index:
                            if len(desc) > 45:
                                # truncation at word boundaries
                                words = desc.split()
                                truncated = []
                                char_count = 0
                                for word in words:
                                    if char_count + len(word) + 1 <= 45:
                                        truncated.append(word)
                                        char_count += len(word) + 1
                                    else:
                                        break
                                labels.append(' '.join(truncated) + '...')
                            else:
                                labels.append(desc)

                        ax1.set_yticks(y_pos)
                        ax1.set_yticklabels(labels, fontsize=9)
                        ax1.set_xlabel('Average Cost (USD)', fontsize=11, fontweight='bold')
                        ax1.set_title('Top 15 Most Expensive DRG Categories', fontsize=14, fontweight='bold', pad=15)

                        # Format x-axis
                        ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                        ax1.grid(True, axis='x', alpha=0.3, linestyle='--')

                        # Add value labels
                        for i, bar in enumerate(bars):
                            width = bar.get_width()
                            if width > 0:
                                ax1.text(width + max(top_drgs['mean']) * 0.02, 
                                        bar.get_y() + bar.get_height()/2, 
                                        f'${width:,.0f}', ha='left', va='center', 
                                        fontsize=9, fontweight='bold', color='#2C3E50')

                        # Top right: Case volume vs cost scatter
                        ax2 = fig.add_subplot(gs[0, 1])
                        ax2.scatter(top_drgs['count'], top_drgs['mean'], 
                                   s=top_drgs['count']*2, c=colors, alpha=0.7, 
                                   edgecolors='#2C3E50', linewidth=1)

                        ax2.set_xlabel('Number of Cases', fontsize=11, fontweight='bold')
                        ax2.set_ylabel('Average Cost (USD)', fontsize=11, fontweight='bold')
                        ax2.set_title('Case Volume vs Average Cost\n(Bubble size = Volume)', 
                                     fontsize=14, fontweight='bold', pad=15)

                        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                        ax2.grid(True, alpha=0.3, linestyle='--')

                        # Add trend line
                        if len(top_drgs) > 3:
                            z = np.polyfit(top_drgs['count'], top_drgs['mean'], 1)
                            p = np.poly1d(z)
                            x_trend = np.linspace(top_drgs['count'].min(), top_drgs['count'].max(), 100)
                            ax2.plot(x_trend, p(x_trend), "--", color='#E74C3C', alpha=0.8, linewidth=2)

                    # Bottom: MDC costs bar chart (spanning both columns)
                    ax3 = fig.add_subplot(gs[1, :])
                
                    # Create bar chart for MDC
                    bars_mdc = ax3.bar(range(len(mdc_sorted)), mdc_sorted['mean'], 
                                      color=plt.cm.Set2(np.linspace(0, 1, len(mdc_sorted))), 
                                      alpha=0.8, edgecolor='#2C3E50', linewidth=1)
                
                    ax3.set_title('Average Costs By Major Diagnostic Category', fontsize=14, fontweight='bold', pad=15)
                    ax3.set_xlabel('MDC Category', fontsize=11, fontweight='bold')
                    ax3.set_ylabel('Average Costs (USD)', fontsize=11, fontweight='bold')
                
                    # Rotate and truncate labels
                    labels_mdc = [desc[:25] + '...' if len(desc) > 25 else desc 
                                 for desc in mdc_sorted.index]
                    ax3.set_xticks(range(len(mdc_sorted)))
                    ax3.set_xticklabels(labels_mdc, rotation=45, ha='right', fontsize=9)
                
                    # Format y-axis
                    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                    ax3.grid(True, axis='y', alpha=0.3, linestyle='--')
                
                    # Add value labels on bars
                    for bar in bars_mdc:
                        height = bar.get_height()
                        if height > 0:
                            ax3.text(bar.get_x() + bar.get_width()/2., height + max(mdc_sorted['mean']) * 0.01,
                                    f'${height:,.0f}', ha='center', va='bottom', 
                                    fontsize=8, fontweight='bold', color='#2C3E50')

                    # Add overall title
                    fig.suptitle('Hospital Specialization Cost Analysis', fontsize=18, fontweight='bold', y=0.98)
                
                    plt.tight_layout()
                    plt.subplots_adjust(top=0.93)  # Make room for suptitle
                    plt.savefig('output/analysis/plots/hospital_specialization_cost_variations.png', 
                               dpi=300, bbox_inches='tight', facecolor='white')
                   
                    plt.close()

                except Exception as e:
                    results.append(f"Visualization failed: {e}")
                    plt.close()
    
        # Save results
        try:
            with open('output/analysis/specialization_analysis.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(results))
        except Exception as e:
            print(f"Error saving specialization analysis: {e}")
    
        return results
    
    def analyze_patient_demographics(self):
       
       
            
        
        
        results = []
        
        # 1. Age Group Analysis 
        if 'Age Group' in self.df.columns and 'Total Costs_clean' in self.df.columns:
            age_data = self.df.dropna(subset=['Age Group', 'Total Costs_clean'])
            
            if len(age_data) > 0:
                age_costs = age_data.groupby('Age Group')['Total Costs_clean'].agg([
                    'count', 'mean', 'median', 'std'
                ]).round(2)
                
                results.append("1. Costs By Age Group:")
                results.append(str(age_costs))
                results.append("")
                
                # Statistical test
                try:
                    age_groups = [group['Total Costs_clean'].dropna().values 
                                 for name, group in age_data.groupby('Age Group')]
                    age_groups = [group for group in age_groups if len(group) > 5]
                    
                    if len(age_groups) > 1:
                        f_stat, p_value = stats.f_oneway(*age_groups)
                        results.append(f"ANOVA F-Statistic: {f_stat:.4f}, p-value: {p_value:.4f}")
                        if p_value < 0.05:
                            results.append("Result: Significant age group differences (p < 0.05)")
                        else:
                            results.append("Result: No significant age group differences (p >= 0.05)")
                        results.append("")
                except Exception as e:
                    results.append(f"Age group ANOVA failed: {e}")
                    results.append("")
               #  Age Group Visualization
                try:
                    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))

                    # Ensure no negative values and clean data
                    age_costs_clean = age_costs[age_costs['mean'] > 0].copy()
                    age_costs_clean = age_costs_clean[age_costs_clean['std'] >= 0]  # Remove negative std

                    # Plot 1: Bar chart with error bars 
                    colors = plt.cm.viridis(np.linspace(0, 1, len(age_costs_clean)))
                    x_pos = np.arange(len(age_costs_clean))

                    # Calculate error bars but ensure they don't go below zero
                    lower_errors = np.minimum(age_costs_clean['std'], age_costs_clean['mean'])
                    upper_errors = age_costs_clean['std']
                    error_bars = [lower_errors, upper_errors]

                    bars = ax1.bar(x_pos, age_costs_clean['mean'], 
                                   yerr=error_bars, capsize=8,
                                   color=colors, alpha=0.8, 
                                   edgecolor='#2C3E50', linewidth=1.5)

                    ax1.set_title('Average Healthcare Costs by Age Group\n(Mean ± Standard Deviation)', 
                                  fontsize=16, fontweight='bold', pad=20)
                    ax1.set_xlabel('Age Group', fontsize=12, fontweight='bold')
                    ax1.set_ylabel('Average Cost (USD)', fontsize=12, fontweight='bold')
                    ax1.set_xticks(x_pos)
                    ax1.set_xticklabels(age_costs_clean.index, rotation=0)
                    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                    ax1.grid(True, axis='y', alpha=0.3, linestyle='--')
                    ax1.set_ylim(bottom=0)  # Force y-axis to start at 0

                    # Add value labels
                    for i, bar in enumerate(bars):
                        height = bar.get_height()
                        ax1.text(bar.get_x() + bar.get_width()/2., height + upper_errors.iloc[i] + height*0.05,
                                f'${height:,.0f}', ha='center', va='bottom', 
                                fontsize=11, fontweight='bold')

                    # Plot 2: Case counts
                    bars2 = ax2.bar(x_pos, age_costs_clean['count'], 
                                    color=colors, alpha=0.7, edgecolor='#2C3E50', linewidth=1)
                    ax2.set_title('Number of Cases by Age Group', fontsize=16, fontweight='bold', pad=20)
                    ax2.set_xlabel('Age Group', fontsize=12, fontweight='bold')
                    ax2.set_ylabel('Number of Cases', fontsize=12, fontweight='bold')
                    ax2.set_xticks(x_pos)
                    ax2.set_xticklabels(age_costs_clean.index, rotation=0)
                    ax2.grid(True, axis='y', alpha=0.3, linestyle='--')

                    # Add count labels
                    for bar in bars2:
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                f'{height:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

                    # Plot 3: Box plot 
                    age_groups_data = []
                    age_labels = []
    
                    for name, group in age_data.groupby('Age Group'):
                        data = group['Total Costs_clean'].dropna().values
                        if len(data) > 0 and name in age_costs_clean.index:
                            age_groups_data.append(data)
                            age_labels.append(name)

                    if len(age_groups_data) > 0:
                        bp = ax3.boxplot(age_groups_data, tick_labels=age_labels, patch_artist=True,
                                        boxprops=dict(linewidth=2, alpha=0.8),
                                        whiskerprops=dict(linewidth=2, color='#2C3E50'),
                                        capprops=dict(linewidth=2, color='#2C3E50'),
                                        medianprops=dict(linewidth=3, color='white'),
                                        flierprops=dict(marker='o', markerfacecolor='#E74C3C', 
                                                      markersize=4, alpha=0.6, markeredgecolor='white'))

                        #  distinct colors for each box
                        beautiful_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                                           '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE']
        
                        for i, patch in enumerate(bp['boxes']):
                            patch.set_facecolor(beautiful_colors[i % len(beautiful_colors)])
                            patch.set_alpha(0.85)
                            patch.set_edgecolor('#2C3E50')
                            patch.set_linewidth(2)

                    ax3.set_title('Cost Distribution by Age Group\n(Box Plot)', fontsize=16, fontweight='bold', pad=20)
                    ax3.set_xlabel('Age Group', fontsize=12, fontweight='bold')
                    ax3.set_ylabel('Total Costs (USD)', fontsize=12, fontweight='bold')
                    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                    ax3.grid(True, axis='y', alpha=0.3, linestyle='--')
                    ax3.set_facecolor('#FAFAFA')  # Light background for better readability

                    # Plot 4: Coefficient of variation (std/mean)
                    cv = (age_costs_clean['std'] / age_costs_clean['mean']) * 100
                    bars4 = ax4.bar(x_pos, cv, color=colors, alpha=0.7, edgecolor='#2C3E50', linewidth=1)
                    ax4.set_title('Cost Variability by Age Group\n(Coefficient of Variation)', 
                                  fontsize=16, fontweight='bold', pad=20)
                    ax4.set_xlabel('Age Group', fontsize=12, fontweight='bold')
                    ax4.set_ylabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
                    ax4.set_xticks(x_pos)
                    ax4.set_xticklabels(age_costs_clean.index, rotation=0)
                    ax4.grid(True, axis='y', alpha=0.3, linestyle='--')

                    # Add CV labels
                    for i, bar in enumerate(bars4):
                        height = bar.get_height()
                        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                                f'{height:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

                    plt.tight_layout()
                    plt.savefig('output/analysis/plots/demographic_cost_variations.png', 
                                dpi=300, bbox_inches='tight', facecolor='white')
                    plt.close()

                except Exception as e:
                    results.append(f"Age group visualization failed: {e}")
                    plt.close()
        
        # Save results
        try:
            with open('output/analysis/demographics_analysis.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(results))
        except Exception as e:
            print(f"Error saving demographics analysis: {e}")
        
        return results
    
    def generate_summary_report(self):
        
        
        
        
        summary = []
        summary.append("COMPREHENSIVE COST VARIATION ANALYSIS REPORT")
        summary.append("=" * 60)
        summary.append("")
        
        # Basic statistics 
        if 'Total Costs_clean' in self.df.columns:
            costs = self.df['Total Costs_clean'].dropna()
            if len(costs) > 0:
                summary.append("BASIC COST STATISTICS:")
                summary.append("-" * 30)
                summary.append(f"Total Records Analyzed: {len(costs):,}")
                summary.append(f"Mean Cost: ${costs.mean():,.2f}")
                summary.append(f"Median Cost: ${costs.median():,.2f}")
                summary.append(f"Standard Deviation: ${costs.std():,.2f}")
                summary.append(f"Minimum Cost: ${costs.min():,.2f}")
                summary.append(f"Maximum Cost: ${costs.max():,.2f}")
                summary.append("")
                
                # Percentile analysis
                summary.append("COST DISTRIBUTION PERCENTILES:")
                summary.append("-" * 30)
                for p in [10, 25, 50, 75, 90, 95, 99]:
                    summary.append(f"{p}th Percentile: ${costs.quantile(p/100):,.2f}")
                summary.append("")
        
        # Data quality assessment
        summary.append("DATA QUALITY ASSESSMENT:")
        summary.append("-" * 30)
        summary.append(f"Total Rows in Dataset: {len(self.df):,}")
        
        # Check completeness of key columns
        key_columns = ['Total Costs', 'Total Charges', 'Hospital Service Area', 
                      'APR DRG Description', 'Age Group']
        
        for col in key_columns:
            if col in self.df.columns:
                missing_count = self.df[col].isna().sum()
                missing_pct = (missing_count / len(self.df)) * 100
                summary.append(f"{col}: {missing_count:,} missing ({missing_pct:.1f}%)")
        
        summary.append("")
        
        summary.append("AVAILABLE DATA COLUMNS:")
        summary.append("-" * 30)
        summary.append(", ".join(sorted(self.df.columns.tolist())))
        summary.append("")
        
        # Analysis completion status
        summary.append("ANALYSIS COMPONENTS COMPLETED:")
     
        
        summary.append("FILES GENERATED:")
        summary.append("-" * 30)
        summary.append("• output/analysis/regional_analysis.txt")
        summary.append("• output/analysis/specialization_analysis.txt")
        summary.append("• output/analysis/demographics_analysis.txt")
        summary.append("• output/analysis/summary_report.txt")
        summary.append("• output/analysis/plots/ (visualization files)")
        
        # Save summary
        try:
            with open('output/analysis/summary_report.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(summary))
        except Exception as e:
            print(f"Error saving summary report: {e}")
        
        return summary
    
    def run_complete_analysis(self):
        
        if self.df is None:
            print("Cannot run analysis - no data loaded")
            return
            
        print("Starting Complete Cost Variation Analysis...")

        
        # Run all analyses
        try:
            self.analyze_regional_variations()
            print("✓ Regional analysis completed")
        except Exception as e:
            print(f"✗ Regional analysis failed: {e}")
        
        try:
            self.analyze_hospital_specializations()
            print("✓ Specialization analysis completed")
        except Exception as e:
            print(f"✗ Specialization analysis failed: {e}")
        
        try:
            self.analyze_patient_demographics()
            print("✓ Demographics analysis completed")
        except Exception as e:
            print(f"✗ Demographics analysis failed: {e}")
        
        try:
            self.generate_summary_report()
            print("✓ Summary report completed")
        except Exception as e:
            print(f"✗ Summary report failed: {e}")
        
        print("\nAnalysis Complete!")
        print("Results saved in 'output/analysis/' directory")

# Main execution
if __name__ == "__main__":
    # Try multiple possible file paths
    possible_paths = [
        r".\data\Hospital_Inpatient_Discharges__SPARCS_De-Identified___2022_20250423.csv",
        r".\data\Hospital_Inpatient_Discharges__SPARCS_De-Identified___2022_20250423",
        r"./data/Hospital_Inpatient_Discharges__SPARCS_De-Identified___2022_20250423.csv",
        r"Hospital_Inpatient_Discharges__SPARCS_De-Identified___2022_20250423.csv"
    ]
    
    # Initialize analyzer
    analyzer = None
    for path in possible_paths:
        try:
            analyzer = CostVariationAnalyzer(path)
            if analyzer.df is not None:
                break
        except:
            continue
    
    if analyzer is None or analyzer.df is None:
        print("Could not load data from any of the attempted paths:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\nPlease check that your CSV file exists and the path is correct.")
    else:
        # Run complete analysis
        analyzer.run_complete_analysis()
        
        print("\nGenerated Analysis Files:")
        print("- output/analysis/regional_analysis.txt")
        print("- output/analysis/specialization_analysis.txt") 
        print("- output/analysis/demographics_analysis.txt")
        print("- output/analysis/summary_report.txt")
        print("- output/analysis/plots/ (visualization files)")