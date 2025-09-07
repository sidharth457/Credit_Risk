"""
Test script to verify that all interactive visualization libraries are working correctly.
This script tests plotly, plotnine, bokeh, and altair installations.
"""

import sys

def test_imports():
    """Test if all visualization libraries can be imported successfully."""
    libraries = {
        'plotly': None,
        'plotnine': None,
        'bokeh': None,
        'altair': None
    }
    
    # Test Plotly
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        libraries['plotly'] = "✓ Plotly imported successfully"
        print("✓ Plotly - Interactive web-based visualizations")
    except ImportError as e:
        libraries['plotly'] = f"✗ Plotly import failed: {e}"
        print(f"✗ Plotly import failed: {e}")
    
    # Test Plotnine
    try:
        from plotnine import ggplot, aes, geom_point
        libraries['plotnine'] = "✓ Plotnine imported successfully"
        print("✓ Plotnine - Grammar of Graphics for Python")
    except ImportError as e:
        libraries['plotnine'] = f"✗ Plotnine import failed: {e}"
        print(f"✗ Plotnine import failed: {e}")
    
    # Test Bokeh
    try:
        from bokeh.plotting import figure, show
        from bokeh.models import HoverTool
        libraries['bokeh'] = "✓ Bokeh imported successfully"
        print("✓ Bokeh - Interactive web plots with hover tools")
    except ImportError as e:
        libraries['bokeh'] = f"✗ Bokeh import failed: {e}"
        print(f"✗ Bokeh import failed: {e}")
    
    # Test Altair
    try:
        import altair as alt
        libraries['altair'] = "✓ Altair imported successfully"
        print("✓ Altair - Statistical visualization library")
    except ImportError as e:
        libraries['altair'] = f"✗ Altair import failed: {e}"
        print(f"✗ Altair import failed: {e}")
    
    return libraries

def show_library_capabilities():
    """Display the capabilities of each library for interactive dashboards."""
    print("\n" + "="*60)
    print("INTERACTIVE DASHBOARD CAPABILITIES")
    print("="*60)
    
    print("\n📊 PLOTLY:")
    print("  • Real-time hover information")
    print("  • Interactive zoom, pan, select")
    print("  • Dynamic filtering and updates")
    print("  • 3D visualizations")
    print("  • Built-in Streamlit integration")
    
    print("\n📈 PLOTNINE:")
    print("  • Grammar of Graphics approach")
    print("  • Layered visualizations")
    print("  • Statistical transformations")
    print("  • Faceting for multiple views")
    
    print("\n🎯 BOKEH:")
    print("  • Server-based interactivity")
    print("  • Custom JavaScript callbacks")
    print("  • Real-time streaming data")
    print("  • Advanced hover tools")
    print("  • Widget-based dashboards")
    
    print("\n📋 ALTAIR:")
    print("  • Declarative statistical visualization")
    print("  • Interactive selections")
    print("  • Linked brushing between charts")
    print("  • Automatic chart recommendations")

if __name__ == "__main__":
    print("Testing Interactive Visualization Libraries...")
    print("="*50)
    
    results = test_imports()
    
    # Check if all imports were successful
    all_success = all("✓" in status for status in results.values())
    
    if all_success:
        print(f"\n🎉 SUCCESS: All visualization libraries are ready!")
        show_library_capabilities()
        
        print(f"\n💡 RECOMMENDATION FOR CREDIT RISK DASHBOARD:")
        print("  • Use PLOTLY for main interactive charts (best Streamlit integration)")
        print("  • Use ALTAIR for statistical analysis views")
        print("  • Use BOKEH for advanced real-time monitoring")
        print("  • Use PLOTNINE for exploratory data analysis")
        
    else:
        print(f"\n⚠️  Some libraries failed to import. Check the errors above.")
        sys.exit(1)
