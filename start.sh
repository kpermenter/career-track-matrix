#!/bin/bash
PORT=${PORT:-8501}
streamlit run impact_enhanced_streamlit.py \
  --server.headless true \
  --server.port $PORT \
  --server.address 0.0.0.0 \
  --server.enableCORS false \
  --server.enableXsrfProtection false