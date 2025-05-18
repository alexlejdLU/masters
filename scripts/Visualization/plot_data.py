import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Run the script with:
# streamlit run scripts/visualization/plot_data.py --server.port 8502


# Page config
st.set_page_config(page_title="Interactive Data Visualization", layout="wide")
st.title("Interactive Data Visualization")

# Define path to data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data_clean")

# Get list of CSV files
@st.cache_data
def get_csv_files():
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    return [os.path.basename(file) for file in csv_files]

# Load selected data file
@st.cache_data
def load_data(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    df = pd.read_csv(file_path)
    # Convert date columns to datetime if they exist
    for col in df.columns:
        if 'date' in col.lower():
            df[col] = pd.to_datetime(df[col])
    return df

# File selection widget
csv_files = get_csv_files()
selected_file = st.sidebar.selectbox("Select Data File", csv_files)

if selected_file:
    # Load the data
    df = load_data(selected_file)
    
    # Display the dataframe
    st.subheader(f"Data Preview: {selected_file}")
    st.dataframe(df.head())
    
    # Get column information
    st.sidebar.header("Plot Controls")
    
    # Identify date columns and numeric columns
    date_columns = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    # If no date columns were found through type checking, try to find them by name
    if not date_columns:
        date_columns = [col for col in df.columns if 'date' in col.lower()]
    
    # Axis selection
    all_columns = date_columns + numeric_columns
    if len(all_columns) > 0:
        x_axis = st.sidebar.selectbox("X-axis", options=all_columns, index=0 if date_columns else min(0, len(all_columns)-1))
        y_axis = st.sidebar.selectbox("Primary Y-axis", options=numeric_columns, index=0 if len(numeric_columns) > 0 else 0)
        
        # Secondary Y-axis
        use_secondary_axis = st.sidebar.checkbox("Use Secondary Y-axis")
        secondary_y_axis = None
        if use_secondary_axis:
            secondary_y_axis = st.sidebar.selectbox(
                "Secondary Y-axis", 
                options=[col for col in numeric_columns if col != y_axis],
                index=0
            )
        
        # Optional color by
        color_by = st.sidebar.selectbox("Color by (optional)", options=['None'] + numeric_columns, index=0)
        color_column = None if color_by == 'None' else color_by
        
        # Plot type selection
        plot_type = st.sidebar.selectbox(
            "Plot Type",
            options=["Line", "Scatter", "Bar"],
            index=0
        )
        
        # Plot title
        if secondary_y_axis:
            plot_title = f"{plot_type} Plot: {y_axis} & {secondary_y_axis} vs {x_axis}"
        else:
            plot_title = f"{plot_type} Plot: {y_axis} vs {x_axis}"
            
        st.subheader(plot_title)
        
        # Create the plot with secondary y-axis if selected
        if secondary_y_axis:
            # Create figure with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Primary Y-axis trace
            if plot_type == "Line":
                trace1 = go.Scatter(
                    x=df[x_axis], 
                    y=df[y_axis], 
                    name=y_axis,
                    mode='lines'  # No markers
                )
            elif plot_type == "Scatter":
                trace1 = go.Scatter(
                    x=df[x_axis], 
                    y=df[y_axis], 
                    name=y_axis,
                    mode='markers'
                )
            else:  # Bar
                trace1 = go.Bar(
                    x=df[x_axis], 
                    y=df[y_axis], 
                    name=y_axis
                )
            
            # Secondary Y-axis trace
            if plot_type == "Line":
                trace2 = go.Scatter(
                    x=df[x_axis], 
                    y=df[secondary_y_axis], 
                    name=secondary_y_axis,
                    mode='lines',  # No markers
                    line=dict(color='#FF4B4B')
                )
            elif plot_type == "Scatter":
                trace2 = go.Scatter(
                    x=df[x_axis], 
                    y=df[secondary_y_axis], 
                    name=secondary_y_axis,
                    mode='markers',
                    marker=dict(color='#FF4B4B')
                )
            else:  # Bar
                trace2 = go.Bar(
                    x=df[x_axis], 
                    y=df[secondary_y_axis], 
                    name=secondary_y_axis,
                    marker=dict(color='#FF4B4B')
                )
            
            # Add traces
            fig.add_trace(trace1, secondary_y=False)
            fig.add_trace(trace2, secondary_y=True)
            
            # Set axis titles
            fig.update_xaxes(title_text=x_axis)
            fig.update_yaxes(title_text=y_axis, secondary_y=False)
            fig.update_yaxes(title_text=secondary_y_axis, secondary_y=True)
            
        else:
            # Single y-axis plot
            if plot_type == "Line":
                fig = px.line(
                    df, 
                    x=x_axis, 
                    y=y_axis, 
                    color=color_column, 
                    markers=False  # No markers
                )
            elif plot_type == "Scatter":
                fig = px.scatter(
                    df, 
                    x=x_axis, 
                    y=y_axis, 
                    color=color_column
                )
            else:  # Bar
                fig = px.bar(
                    df, 
                    x=x_axis, 
                    y=y_axis, 
                    color=color_column
                )
        
        # Update layout for better visibility
        fig.update_layout(
            height=600,
            width=800,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional plot settings
        st.sidebar.header("Additional Settings")
        
        # Statistics tab
        if st.sidebar.checkbox("Show Plot Statistics"):
            st.subheader("Statistics for Selected Data")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{y_axis} Statistics:**")
                st.write(df[[y_axis]].describe())
                
            if secondary_y_axis:
                with col2:
                    st.write(f"**{secondary_y_axis} Statistics:**")
                    st.write(df[[secondary_y_axis]].describe())
        
        # Show row count
        st.sidebar.metric("Total Records", df.shape[0])
    else:
        st.error("No suitable columns found for plotting. The file may not contain numeric or date data.")
else:
    st.error("No CSV files found in the data directory. Please add CSV files to the data_clean folder.")
