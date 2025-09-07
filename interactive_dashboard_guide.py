"""
Interactive Credit Risk Dashboard Implementation Guide
This guide shows how to use each visualization library for specific dashboard components.
"""

import streamlit as st
import pandas as pd
import numpy as np

# Sample data structure for demonstration
def create_sample_credit_data():
    """Create sample credit risk data for demonstration."""
    np.random.seed(42)
    n_customers = 1000
    
    data = {
        'customer_id': range(1, n_customers + 1),
        'credit_score': np.random.normal(650, 100, n_customers),
        'income': np.random.lognormal(10, 0.5, n_customers),
        'loan_amount': np.random.lognormal(9, 0.8, n_customers),
        'risk_score': np.random.uniform(0, 1, n_customers),
        'age': np.random.randint(18, 80, n_customers),
        'employment_years': np.random.randint(0, 40, n_customers),
        'debt_to_income': np.random.uniform(0, 0.8, n_customers),
        'loan_purpose': np.random.choice(['Home', 'Auto', 'Personal', 'Business'], n_customers),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_customers)
    }
    
    df = pd.DataFrame(data)
    df['risk_category'] = pd.cut(df['risk_score'], 
                                bins=[0, 0.3, 0.7, 1.0], 
                                labels=['Low', 'Medium', 'High'])
    return df

# =============================================================================
# PLOTLY - Main Interactive Charts (Best Streamlit Integration)
# =============================================================================

def create_risk_distribution_chart(df):
    """Interactive Risk Distribution with Hover Details"""
    import plotly.express as px
    
    fig = px.scatter(df, 
                    x='credit_score', 
                    y='income',
                    color='risk_category',
                    size='loan_amount',
                    hover_data={
                        'customer_id': True,
                        'debt_to_income': ':.2f',
                        'employment_years': True,
                        'loan_purpose': True
                    },
                    title="Credit Risk Analysis - Interactive Scatter Plot",
                    labels={
                        'credit_score': 'Credit Score',
                        'income': 'Annual Income ($)',
                        'risk_category': 'Risk Level'
                    })
    
    # Customize hover template
    fig.update_traces(
        hovertemplate="<b>Customer %{customdata[0]}</b><br>" +
                     "Credit Score: %{x}<br>" +
                     "Income: $%{y:,.0f}<br>" +
                     "Loan Amount: $%{marker.size:,.0f}<br>" +
                     "Debt-to-Income: %{customdata[1]:.1%}<br>" +
                     "Employment: %{customdata[2]} years<br>" +
                     "Purpose: %{customdata[3]}<br>" +
                     "<extra></extra>"
    )
    
    return fig

def create_risk_metrics_dashboard(df):
    """Dynamic Risk Metrics Dashboard"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Risk Distribution', 'Loan Purpose Analysis', 
                      'Age vs Risk', 'Regional Risk Comparison'),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "box"}]]
    )
    
    # Risk distribution pie chart
    risk_counts = df['risk_category'].value_counts()
    fig.add_trace(
        go.Pie(labels=risk_counts.index, values=risk_counts.values,
               name="Risk Distribution"),
        row=1, col=1
    )
    
    # Loan purpose bar chart
    purpose_risk = df.groupby('loan_purpose')['risk_score'].mean()
    fig.add_trace(
        go.Bar(x=purpose_risk.index, y=purpose_risk.values,
               name="Avg Risk by Purpose"),
        row=1, col=2
    )
    
    # Age vs Risk scatter
    fig.add_trace(
        go.Scatter(x=df['age'], y=df['risk_score'],
                  mode='markers', name="Age vs Risk",
                  hovertemplate="Age: %{x}<br>Risk: %{y:.2f}<extra></extra>"),
        row=2, col=1
    )
    
    # Regional risk box plot
    for region in df['region'].unique():
        region_data = df[df['region'] == region]['risk_score']
        fig.add_trace(
            go.Box(y=region_data, name=region),
            row=2, col=2
        )
    
    fig.update_layout(height=800, showlegend=True,
                     title_text="Credit Risk Dashboard - Multi-Chart View")
    return fig

# =============================================================================
# ALTAIR - Statistical Analysis Views
# =============================================================================

def create_statistical_analysis_chart(df):
    """Interactive Selection and Filtering with Altair"""
    import altair as alt
    
    # Enable Altair to render in Streamlit
    alt.data_transformers.enable('json')
    
    # Base chart
    base = alt.Chart(df).add_selection(
        alt.selection_interval(bind='scales')
    )
    
    # Credit score distribution
    hist = base.mark_bar().encode(
        alt.X('credit_score:Q', bin=alt.Bin(maxbins=30)),
        alt.Y('count()'),
        alt.Color('risk_category:N'),
        tooltip=['count()', 'risk_category:N']
    ).properties(
        width=300,
        height=200,
        title='Credit Score Distribution by Risk'
    )
    
    # Income vs Loan Amount with selection
    scatter = base.mark_circle(size=60).encode(
        alt.X('income:Q', scale=alt.Scale(type='log')),
        alt.Y('loan_amount:Q', scale=alt.Scale(type='log')),
        alt.Color('risk_score:Q', scale=alt.Scale(scheme='viridis')),
        tooltip=['customer_id:O', 'income:Q', 'loan_amount:Q', 'risk_score:Q']
    ).properties(
        width=300,
        height=200,
        title='Income vs Loan Amount (Log Scale)'
    )
    
    # Combine charts
    chart = (hist | scatter)
    return chart

def create_correlation_heatmap(df):
    """Correlation Matrix Heatmap with Altair"""
    import altair as alt
    
    # Calculate correlation matrix
    numeric_cols = ['credit_score', 'income', 'loan_amount', 'risk_score', 
                   'age', 'employment_years', 'debt_to_income']
    corr_matrix = df[numeric_cols].corr().reset_index().melt('index')
    corr_matrix.columns = ['var1', 'var2', 'correlation']
    
    heatmap = alt.Chart(corr_matrix).mark_rect().encode(
        alt.X('var1:O', title=''),
        alt.Y('var2:O', title=''),
        alt.Color('correlation:Q', 
                 scale=alt.Scale(scheme='redblue', domain=[-1, 1])),
        tooltip=['var1:O', 'var2:O', 'correlation:Q']
    ).properties(
        width=400,
        height=400,
        title='Feature Correlation Matrix'
    )
    
    return heatmap

# =============================================================================
# BOKEH - Advanced Real-time Monitoring Dashboards
# =============================================================================

def bokeh_examples():
    """Examples of Bokeh charts for real-time monitoring."""
    
    # 1. Real-time Risk Monitoring with Advanced Hover
    def realtime_risk_monitor(df):
        from bokeh.plotting import figure
        from bokeh.models import HoverTool, ColorBar, LinearColorMapper
        from bokeh.palettes import Viridis256
        from bokeh.transform import transform
        
        # Create color mapper
        color_mapper = LinearColorMapper(palette=Viridis256, 
                                       low=df['risk_score'].min(), 
                                       high=df['risk_score'].max())
        
        # Create figure
        p = figure(title="Real-time Credit Risk Monitor",
                  x_axis_label='Credit Score',
                  y_axis_label='Debt-to-Income Ratio',
                  width=700, height=500)
        
        # Add circle markers
        circles = p.circle('credit_score', 'debt_to_income', 
                          size='loan_amount_scaled',
                          color=transform('risk_score', color_mapper),
                          alpha=0.7,
                          source=df)
        
        # Advanced hover tool
        hover = HoverTool(tooltips=[
            ("Customer ID", "@customer_id"),
            ("Credit Score", "@credit_score"),
            ("Income", "$@income{0,0}"),
            ("Loan Amount", "$@loan_amount{0,0}"),
            ("Risk Score", "@risk_score{0.000}"),
            ("Risk Category", "@risk_category"),
            ("Employment Years", "@employment_years"),
            ("Loan Purpose", "@loan_purpose"),
            ("Region", "@region")
        ])
        
        p.add_tools(hover)
        
        # Add color bar
        color_bar = ColorBar(color_mapper=color_mapper, width=8, location=(0,0))
        p.add_layout(color_bar, 'right')
        
        return p
    
    # 2. Interactive Dashboard with Widgets
    def interactive_dashboard_with_widgets():
        from bokeh.layouts import column, row
        from bokeh.models import Select, Slider, CheckboxGroup
        from bokeh.plotting import figure
        
        # This would be implemented with Bokeh server for full interactivity
        # Here's the structure:
        
        # Widgets
        risk_filter = Select(title="Risk Category:", 
                           options=["All", "Low", "Medium", "High"])
        
        credit_range = Slider(title="Credit Score Range", 
                            start=300, end=850, value=500, step=10)
        
        loan_purposes = CheckboxGroup(labels=["Home", "Auto", "Personal", "Business"],
                                    active=[0, 1, 2, 3])
        
        # Plot (would be updated based on widget values)
        plot = figure(title="Filtered Risk Analysis", width=600, height=400)
        
        # Layout
        controls = column(risk_filter, credit_range, loan_purposes)
        layout = row(controls, plot)
        
        return layout

# =============================================================================
# PLOTNINE - Exploratory Data Analysis
# =============================================================================

def plotnine_examples():
    """Examples of Plotnine charts for exploratory data analysis."""
    
    # 1. Grammar of Graphics Approach
    def exploratory_analysis(df):
        from plotnine import (ggplot, aes, geom_point, geom_smooth, 
                            facet_wrap, theme_minimal, labs, 
                            scale_color_gradient, geom_histogram, geom_boxplot)
        
        # Multi-faceted analysis
        p1 = (ggplot(df, aes(x='credit_score', y='risk_score', color='income')) +
              geom_point(alpha=0.6) +
              geom_smooth(method='lm', se=False) +
              facet_wrap('~loan_purpose') +
              scale_color_gradient(low='blue', high='red') +
              theme_minimal() +
              labs(title='Credit Score vs Risk by Loan Purpose',
                   x='Credit Score',
                   y='Risk Score',
                   color='Income'))
        
        return p1
    
    # 2. Statistical Distributions
    def distribution_analysis(df):
        from plotnine import (ggplot, aes, geom_histogram, geom_density,
                            facet_grid, theme_minimal, labs)
        
        # Risk score distribution by category
        p2 = (ggplot(df, aes(x='risk_score', fill='risk_category')) +
              geom_histogram(alpha=0.7, bins=30) +
              facet_grid('risk_category~region') +
              theme_minimal() +
              labs(title='Risk Score Distribution by Category and Region',
                   x='Risk Score',
                   y='Count'))
        
        return p2

# =============================================================================
# STREAMLIT INTEGRATION EXAMPLE
# =============================================================================

def main_dashboard():
    """Main Streamlit dashboard integrating all visualization libraries."""
    
    st.title("🏦 Interactive Credit Risk Dashboard")
    st.markdown("Dynamic visualizations that change based on customer data")
    
    # Load data
    df = create_sample_credit_data()
    
    # Sidebar filters
    st.sidebar.header("Dashboard Filters")
    selected_risk = st.sidebar.multiselect("Risk Categories", 
                                          df['risk_category'].unique(),
                                          default=df['risk_category'].unique())
    
    credit_range = st.sidebar.slider("Credit Score Range", 
                                   int(df['credit_score'].min()),
                                   int(df['credit_score'].max()),
                                   (500, 750))
    
    # Filter data based on selections
    filtered_df = df[
        (df['risk_category'].isin(selected_risk)) &
        (df['credit_score'].between(credit_range[0], credit_range[1]))
    ]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", len(filtered_df))
    with col2:
        st.metric("Avg Risk Score", f"{filtered_df['risk_score'].mean():.3f}")
    with col3:
        st.metric("High Risk %", f"{(filtered_df['risk_category']=='High').mean()*100:.1f}%")
    with col4:
        st.metric("Avg Loan Amount", f"${filtered_df['loan_amount'].mean():,.0f}")
    
    # Plotly Charts (Main Interactive)
    st.header("📊 Main Interactive Analysis (Plotly)")
    plotly_fig = create_risk_distribution_chart(filtered_df)
    st.plotly_chart(plotly_fig, use_container_width=True)
    
    # Altair Charts (Statistical Analysis)
    st.header("📈 Statistical Analysis (Altair)")
    altair_chart = create_statistical_analysis_chart(filtered_df)
    st.altair_chart(altair_chart, use_container_width=True)
    
    # Real-time updates message
    st.info("💡 All charts update automatically when you change the filters - demonstrating real-time interactivity!")

if __name__ == "__main__":
    st.set_page_config(page_title="Credit Risk Dashboard", layout="wide")
    main_dashboard()
