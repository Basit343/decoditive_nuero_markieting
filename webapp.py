import streamlit as st
import requests
import pandas as pd
import numpy as np
from PIL import Image
import time
import logging
import hashlib

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

st.set_page_config(page_title="Image Neuro Analysis App", layout="wide")

# Enhanced Custom CSS for styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
        background: linear-gradient(45deg, #2196F3, #00BCD4);
        border: none;
        color: white;
        padding: 0.8rem;
        border-radius: 10px;
        font-weight: bold;
        transition: transform 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .welcome-msg {
        text-align: center;
        padding: 3rem;
        background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        animation: fadeIn 1.5s ease-in;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .welcome-msg h1 {
        color: #1a237e;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .image-container {
        display: flex;
        justify-content: space-between;
        margin: 1rem 0;
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .stDataFrame {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .processing-animation {
        text-align: center;
        margin: 20px;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        animation: pulse 2s infinite;
    }
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 6px solid #f3f3f3;
        border-top: 6px solid #2196F3;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    .upload-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        margin: 2rem 0;
    }
    .results-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        margin: 2rem 0;
        animation: fadeIn 1s ease-in;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'results' not in st.session_state:
    st.session_state.results = []
    st.session_state.processed_files = set()
    logger.info("Initialized results state")

st.markdown("<div class='welcome-msg'><h1>🎨 AI Image Analysis Dashboard</h1><p style='font-size: 1.2rem; color: #333;'>Unlock the power of neural analysis for your images</p></div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("📁 Upload Your Images (Maximum 100)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    st.markdown("</div>", unsafe_allow_html=True)

if uploaded_files:
    try:
        if len(uploaded_files) > 100:
            logger.error("User attempted to upload more than 100 images")
            st.error("⚠️ Please upload maximum 100 images")
        else:
            # Check which files need processing
            new_files = []
            for file in uploaded_files:
                try:
                    file_bytes = file.read()
                    file_hash = hashlib.md5(file_bytes).hexdigest()
                    file.seek(0)
                    
                    if file_hash not in st.session_state.processed_files:
                        new_files.append((file, file_hash))
                except Exception as e:
                    logger.error(f"Error reading file {file.name}: {str(e)}")
                    st.error(f"⚠️ Error reading file {file.name}. Please ensure it's a valid image file.")
                    continue
            
            if new_files:
                logger.info(f"Processing {len(new_files)} new images")
                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                animation_container = st.empty()
                
                processing_messages = [
                    "🔍 Analyzing image patterns and neural signatures...",
                    "🎨 Detecting color harmonies and visual balance...",
                    "📊 Calculating advanced neural metrics...", 
                    "🧮 Processing multi-dimensional data points...",
                    "🔄 Optimizing results with AI algorithms...",
                    "🧠 Applying deep learning analysis...",
                    "📈 Generating comprehensive insights...",
                    "⚡ Running neural network evaluations...",
                    "🎯 Fine-tuning precision metrics...",
                    "✨ Finalizing advanced calculations..."
                ]
                
                with st.spinner('Processing your images...'):
                    for idx, (file, file_hash) in enumerate(new_files):
                        msg_idx = idx % len(processing_messages)
                        animation_container.markdown(f"""
                            <div class='processing-animation' style='background: linear-gradient(120deg, #e0f7fa 0%, #b2ebf2 100%); padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                                <div class='loading-spinner'></div>
                                <h3 style='color: #006064;'>{processing_messages[msg_idx]}</h3>
                                <p style='color: #00838f;'>Processing image {idx + 1} of {len(new_files)}: {file.name}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        status_text.text(f"Processing image {idx + 1} of {len(new_files)}: {file.name}")
                        logger.info(f"Processing image {idx + 1}/{len(new_files)}: {file.name}")
                        
                        try:
                            clean_filename = file.name.replace(" ", "")
                            serialized_name = f"{file_hash}_{clean_filename}"
                            files = {'file': (serialized_name, file)}
                            
                            response = requests.post('https://neurodecoditiveai.com/analyze', files=files, timeout=30)
                            response.raise_for_status()
                            data = response.json()
                            
                            try:
                                value = (105.2838 * data['Balance'][0] - 
                                        678.0673 * data['Clarity'][0] - 
                                        854.6259 * data['Cognative'] +
                                        110.1255 * data['Exciting'] -
                                        29.6499 * data['Focus'][0] + 
                                        81304.23)
                            except (KeyError, IndexError) as e:
                                logger.error(f"Error calculating value for {file.name}: {str(e)}")
                                continue
                            
                            results.append({
                                'Image': file.name,
                                'SerializedName': serialized_name,
                                'Value': value,
                                'Balance': data['Balance'][0],
                                'Clarity': data['Clarity'][0],
                                'Cognitive': data['Cognative'],
                                'Exciting': data['Exciting'],
                                'Focus': data['Focus'][0]
                            })
                            
                            st.session_state.processed_files.add(file_hash)
                            progress_bar.progress((idx + 1) / len(new_files))
                            logger.debug(f"Successfully processed {file.name}")
                            
                            time.sleep(0.1)
                        
                        except requests.exceptions.RequestException as e:
                            logger.error(f"API Error processing {file.name}: {str(e)}")
                            st.error(f"⚠️ Error processing {file.name}. Please try again later.")
                            continue
                        except Exception as e:
                            logger.error(f"Unexpected error processing {file.name}: {str(e)}")
                            st.error(f"⚠️ An unexpected error occurred while processing {file.name}")
                            continue
                
                animation_container.empty()
                
                if results:
                    st.session_state.results = results

            if st.session_state.results:
                logger.info("Displaying analysis results")
                st.markdown("<div class='results-section'>", unsafe_allow_html=True)
                
                df = pd.DataFrame(st.session_state.results)
                df = df.sort_values('Value', ascending=False)
                
                max_value = df['Value'].max()
                df['Score (%)'] = (1 - (max_value - df['Value']) / max_value) * 100
                
                st.subheader("🏆 Top Image Analysis")
                logger.info("Displaying top image analysis")
                row = df.iloc[0]
                st.markdown(f"### 🌟 Top Ranked Image: {row['Image']}")
                
                cols = st.columns(2)
                
                with cols[0]:
                    st.markdown("**📸 Original Image**")
                    try:
                        top_image_name = row['Image']
                        top_image_idx = next(idx for idx, file in enumerate(uploaded_files) if file.name == top_image_name)
                        original_image = Image.open(uploaded_files[top_image_idx])
                        st.image(original_image, use_container_width=True)
                    except Exception as e:
                        logger.error(f"Error displaying original image: {str(e)}")
                        st.error("Unable to display original image")
                
                with cols[1]:
                    st.markdown("**🎨 Processed Image**")
                    try:
                        processed_url = f"https://neurodecoditiveai.com/analyze/uploads/processed_{row['SerializedName']}"
                        processed_response = requests.get(processed_url, timeout=30)
                        processed_response.raise_for_status()
                        processed_image = Image.open(requests.get(processed_url, stream=True).raw)
                        st.image(processed_image, use_container_width=True)
                    except Exception as e:
                        logger.error(f"Failed to load processed image: {str(e)}")
                        st.warning("Processed image not available")

                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                metrics_cols = st.columns(5)
                metrics_cols[0].metric("⚖️ Balance", f"{row['Balance']:.2f}")
                metrics_cols[1].metric("🎯 Clarity", f"{row['Clarity']:.2f}")
                metrics_cols[2].metric("🧠 Cognitive", f"{row['Cognitive']:.2f}")
                metrics_cols[3].metric("✨ Exciting", f"{row['Exciting']:.2f}")
                metrics_cols[4].metric("🎯 Focus", f"{row['Focus']:.2f}")
                st.markdown("</div>", unsafe_allow_html=True)

                st.subheader("📊 Analysis Results")
                display_df = df.drop('SerializedName', axis=1)
                st.dataframe(display_df)
                
                try:
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results",
                        data=csv,
                        file_name="image_analysis_results.csv",
                        mime="text/csv"
                    )
                    logger.info("Analysis complete - results available for download")
                except Exception as e:
                    logger.error(f"Error generating download file: {str(e)}")
                    st.error("Unable to generate download file")
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    except Exception as e:
        logger.error(f"Critical error in main application flow: {str(e)}")
        st.error("⚠️ An unexpected error occurred. Please try again later.")
