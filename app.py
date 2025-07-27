import streamlit as st
import pandas as pd
import io

# Set page configuration
st.set_page_config(
    page_title="Taluka Data Filter",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Taluka Data Analysis Dashboard")
st.markdown("Filter and analyze data based on Taluka, Difficult Area, and UG Eligible Posts")

# File upload section
# st.sidebar.header("📁 Data Upload")

# For deployment on Streamlit Cloud, you can either:
# 1. Load a file from the repository
# 2. Allow users to upload their own file

# Option 1: Load from repository (recommended for deployment)
@st.cache_data
def load_default_data():
    try:
        # Replace 'your_data.xlsx' with your actual file name in the repository
        df = pd.read_excel('data.xlsx')  
        return df
    except FileNotFoundError:
        return None

# Option 2: File uploader for user uploads
# uploaded_file = st.sidebar.file_uploader(
#     "Upload Excel File", 
#     type=['xlsx', 'xls'],
#     help="Upload your Excel file containing the data"
# )

# Load data
df = None

# if uploaded_file is not None:
#     try:
#         df = pd.read_excel(uploaded_file)
#         st.sidebar.success("✅ File uploaded successfully!")
#     except Exception as e:
#         st.sidebar.error(f"❌ Error reading file: {str(e)}")
# else:
    # Try to load default data from repository
df = load_default_data()
# if df is not None:
#     st.sidebar.info("📄 Using default data file")
# else:
#     st.sidebar.warning("⚠️ No data file found. Please upload an Excel file.")

# Main application logic
if df is not None:
    # Display basic info about the dataset
    st.subheader("📋 Dataset Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        if 'UG_Eligible_Post' in df.columns:
            eligible_count = len(df[df['UG_Eligible_Post'] > 1])
            st.metric("Records with UG_Eligible_Post > 1", eligible_count)

    # Show column names for reference
    # with st.expander("📝 Available Columns"):
    #     st.write(list(df.columns))

    # Filter section
    st.subheader("🔍 Filters")
    
    # Create filter columns
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        # Taluka filter
        if 'Taluka' in df.columns:
            taluka_options = ['All'] + sorted(df['Taluka'].dropna().unique().tolist())
            selected_taluka = st.selectbox("Select Taluka", taluka_options)
        else:
            st.error("'Taluka' column not found in the dataset")
            selected_taluka = 'All'
    
    with filter_col2:
        # Difficult Area filter
        if 'Difficult Area' in df.columns:
            difficult_area_options = ['All'] + sorted(df['Difficult Area'].dropna().unique().tolist())
            selected_difficult_area = st.selectbox("Select Difficult Area", difficult_area_options)
        else:
            st.error("'Difficult Area' column not found in the dataset")
            selected_difficult_area = 'All'
    
    with filter_col3:
        # Medium filter (should be Marathi)
        if 'Medium' in df.columns:
            medium_options = ['All'] + sorted(df['Medium'].dropna().unique().tolist())
            selected_medium = st.selectbox("Select Medium", medium_options, 
                                         index=medium_options.index('Marathi') if 'Marathi' in medium_options else 0)
        else:
            st.error("'Medium' column not found in the dataset")
            selected_medium = 'All'

    # Apply filters
    filtered_df = df.copy()
    
    # Filter by Taluka
    if selected_taluka != 'All' and 'Taluka' in df.columns:
        filtered_df = filtered_df[filtered_df['Taluka'] == selected_taluka]
    
    # Filter by Difficult Area
    if selected_difficult_area != 'All' and 'Difficult Area' in df.columns:
        filtered_df = filtered_df[filtered_df['Difficult Area'] == selected_difficult_area]
    
    # Filter by Medium
    if selected_medium != 'All' and 'Medium' in df.columns:
        filtered_df = filtered_df[filtered_df['Medium'] == selected_medium]
    
    # Filter by UG_Eligible_Post > 1
    if 'UG_Eligible_Post' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['UG_Eligible_Post'] > 1]
    else:
        st.error("'UG_Eligible_Post' column not found in the dataset")
    
    # Sort by UG_Eligible_Post in descending order
    if 'UG_Eligible_Post' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('UG_Eligible_Post', ascending=False)
    
    # Reorder columns to show UG_Eligible_Post and UG_Current_Clear_Post as 4th and 5th columns
    if len(filtered_df) > 0:
        cols = filtered_df.columns.tolist()
        
        # Remove UG_Eligible_Post and UG_Current_Clear_Post from their current positions
        if 'UG_Eligible_Post' in cols:
            cols.remove('UG_Eligible_Post')
        if 'UG_Current_Clear_Post' in cols:
            cols.remove('UG_Current_Clear_Post')
        
        # Insert them at positions 3 and 4 (4th and 5th columns, 0-indexed)
        if 'UG_Eligible_Post' in filtered_df.columns:
            cols.insert(3, 'UG_Eligible_Post')
        if 'UG_Current_Clear_Post' in filtered_df.columns:
            cols.insert(4, 'UG_Current_Clear_Post')
        
        # Reorder the dataframe
        filtered_df = filtered_df[cols]
    
    # Display results
    st.subheader("📊 Filtered Results")
    
    if len(filtered_df) > 0:
        # Display summary
        st.success(f"Found {len(filtered_df)} records matching your criteria")
        
        # Display the dataframe
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400
        )
        
        # Download button
        def convert_df_to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Filtered_Data')
            return output.getvalue()
        
        excel_data = convert_df_to_excel(filtered_df)
        st.download_button(
            label="📥 Download Filtered Data as Excel",
            data=excel_data,
            file_name=f"filtered_data_{selected_taluka}_{selected_difficult_area}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Show some statistics
        if 'UG_Eligible_Post' in filtered_df.columns:
            st.subheader("📈 Statistics")
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                st.metric("Total UG Eligible Posts", filtered_df['UG_Eligible_Post'].sum())
            with stats_col2:
                st.metric("Average UG Eligible Posts", round(filtered_df['UG_Eligible_Post'].mean(), 2))
            with stats_col3:
                st.metric("Max UG Eligible Posts", filtered_df['UG_Eligible_Post'].max())
    
    else:
        st.warning("⚠️ No records found matching your criteria. Please adjust your filters.")
        
# else:
#     st.info("👆 Please upload an Excel file or ensure the default data file is available in the repository.")
    
#     # Instructions for deployment
#     st.subheader("📋 Deployment Instructions")
#     st.markdown("""
#     **For Streamlit Cloud deployment:**
    
#     1. **Upload your data file to the repository:**
#        - Add your Excel file (e.g., `data.xlsx`) to the same directory as this app
#        - Update the file name in the `load_default_data()` function
    
#     2. **Required files for deployment:**
#        - `streamlit_app.py` (this file)
#        - `requirements.txt` with the following content:
#          ```
#          streamlit
#          pandas
#          openpyxl
#          ```
#        - Your data file (e.g., `data.xlsx`)
    
#     3. **Expected Excel file columns:**
#        - `Taluka`
#        - `Difficult Area`
#        - `Medium`
#        - `UG_Eligible_Post`
#        - `UG_Current_Clear_Post`
#     """)

# # Footer
# st.markdown("---")
# st.markdown("*Built with Streamlit* 🎈")
