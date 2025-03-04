import streamlit as st
import requests
import pandas as pd
import numpy as np
from PIL import Image
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Image Analysis App", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .welcome-msg {
        text-align: center;
        padding: 2rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .image-container {
        display: flex;
        justify-content: space-between;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    logger.info("Initialized authentication state")
if 'results' not in st.session_state:
    st.session_state.results = []
    logger.info("Initialized results state")

# Login Section
if not st.session_state.authenticated:
    logger.info("User not authenticated - showing login screen")
    st.markdown("<div class='welcome-msg'><h1>Welcome to Image Analysis App</h1></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email")
    with col2:
        username = st.text_input("Username")
        
    if st.button("Login"):
        if email and username:
            logger.info(f"User {username} logged in successfully")
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            logger.warning("Login attempt failed - missing credentials")
            st.error("Please provide both email and username")

# Main App
else:
    logger.info(f"Showing main app for user {st.session_state.username}")
    st.markdown(f"<div class='welcome-msg'><h2>Welcome {st.session_state.username}!</h2></div>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Upload Images (Maximum 100)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    if uploaded_files:
        if len(uploaded_files) > 100:
            logger.error("User attempted to upload more than 100 images")
            st.error("Please upload maximum 100 images")
        else:
            logger.info(f"Processing {len(uploaded_files)} images")
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Add loading animation
            with st.spinner('Processing your images...'):
                for idx, file in enumerate(uploaded_files):
                    # Show processing animation
                    status_text.text(f"Processing image {idx + 1} of {len(uploaded_files)}: {file.name}")
                    logger.info(f"Processing image {idx + 1}/{len(uploaded_files)}: {file.name}")
                    
                    # API call
                    try:
                        files = {'file': file}
                        response = requests.post('https://neurodecoditiveai.com/analyze', files=files)
                        data = response.json()
                        
                        # Calculate Value
                        value = (105.2838 * data['Balance'][0] - 
                                678.0673 * data['Clarity'][0] - 
                                854.6259 * data['Cognative'] +
                                110.1255 * data['Exciting'] -
                                29.6499 * data['Focus'][0] + 
                                81304.23)
                        
                        results.append({
                            'Image': file.name,
                            'Value': value,
                            'Balance': data['Balance'][0],
                            'Clarity': data['Clarity'][0],
                            'Cognitive': data['Cognative'],
                            'Exciting': data['Exciting'],
                            'Focus': data['Focus'][0]
                        })
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                        logger.debug(f"Successfully processed {file.name}")
                        
                        # Add small delay for smooth animation
                        time.sleep(0.1)
                    
                    except Exception as e:
                        logger.error(f"Error processing {file.name}: {str(e)}")
                        st.error(f"Error processing {file.name}: {str(e)}")
            if results:
                logger.info("Generating analysis results")
                # Convert to DataFrame and sort by Value
                df = pd.DataFrame(results)
                df = df.sort_values('Value', ascending=False)
                
                st.subheader("Analysis Results")
                
                # Calculate and display percentages
                max_value = df['Value'].max()
                df['Score (%)'] = (1 - (max_value - df['Value']) / max_value) * 100
                
                # Display results
                st.dataframe(df)
                
                # Display top image with processed version
                st.subheader("Top Image Analysis")
                logger.info("Displaying top image analysis")
                row = df.iloc[0]
                st.markdown(f"### Top Ranked Image: {row['Image']}")
                cols = st.columns(2)
                
                # Display original image
                with cols[0]:
                    st.markdown("**Original Image**")
                    # Find index of top scoring image
                    top_image_name = row['Image']
                    top_image_idx = next(idx for idx, file in enumerate(uploaded_files) if file.name == top_image_name)
                    original_image = Image.open(uploaded_files[top_image_idx])
                    st.image(original_image, use_container_width=True)
                
                # Display processed image
                with cols[1]:
                    st.markdown("**Processed Image**")
                    try:
                        processed_url = f"https://neurodecoditiveai.com/analyze/uploads/processed_{row['Image']}"
                        processed_response = requests.get(processed_url)
                        if processed_response.status_code == 200:
                            processed_image = Image.open(requests.get(processed_url, stream=True).raw)
                            st.image(processed_image, use_container_width=True)
                        else:
                            logger.warning(f"Primary processed image URL failed for {row['Image']}")
                            st.warning("Processed image not available")
                            # Try alternate URL format
                            alt_processed_url = f"https://neurodecoditiveai.com/analyze/uploads/processed_{original_image.filename}"
                            alt_response = requests.get(alt_processed_url)
                            if alt_response.status_code == 200:
                                processed_image = Image.open(requests.get(alt_processed_url, stream=True).raw)
                                st.image(processed_image, use_container_width=True)
                    except Exception as e:
                        logger.error(f"Failed to load processed image: {str(e)}")
                        st.warning(f"Unable to load processed image: {str(e)}")
                # Display metrics
                metrics_cols = st.columns(5)
                metrics_cols[0].metric("Balance", f"{row['Balance']:.2f}")
                metrics_cols[1].metric("Clarity", f"{row['Clarity']:.2f}")
                metrics_cols[2].metric("Cognitive", f"{row['Cognitive']:.2f}")
                metrics_cols[3].metric("Exciting", f"{row['Exciting']:.2f}")
                metrics_cols[4].metric("Focus", f"{row['Focus']:.2f}")
                
                # Plot top images scores
                st.subheader("Top Images Scores")
                fig = st.bar_chart(df['Score (%)'].head(10))
                
                # Download results
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Results",
                    data=csv,
                    file_name="image_analysis_results.csv",
                    mime="text/csv"
                )
                logger.info("Analysis complete - results available for download")

    if st.sidebar.button("Logout"):
        logger.info(f"User {st.session_state.username} logged out")
        st.session_state.authenticated = False
        st.rerun()
