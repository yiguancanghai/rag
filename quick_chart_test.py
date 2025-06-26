#!/usr/bin/env python3
"""
Quick chart visibility test - Immediate verification of chart display fixes
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))

from app.utils.config import get_custom_css

def main():
    """Quick chart test"""
    
    st.set_page_config(
        page_title="Quick Chart Test",
        page_icon="📊",
        layout="wide"
    )
    
    # Apply enhanced CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    st.title("📊 Quick Chart Display Test")
    st.write("🎯 **TEST GOAL**: Verify that ALL chart text is clearly visible")
    
    # Test 1: Simple Bar Chart
    st.subheader("Test 1: Bar Chart")
    
    fig1 = go.Figure(data=[
        go.Bar(
            x=["Messages", "Users", "Documents"],
            y=[42, 15, 8],
            marker_color=["#0066cc", "#ff6b6b", "#28a745"],
            text=[42, 15, 8],
            textposition="auto",
            textfont=dict(color="white", size=16, family="Arial Black")
        )
    ])
    
    fig1.update_layout(
        title={
            'text': "TEST: Can you read this title clearly?",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#000000', 'family': 'Arial Black'}
        },
        height=300,
        showlegend=False,
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(color='#000000', family='Arial Black', size=14),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#000000',
            linewidth=3,
            tickfont=dict(color='#000000', size=14, family='Arial Black'),
            title="X Axis Label - Can you read this?",
            title_font=dict(color='#000000', size=16, family='Arial Black')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#cccccc',
            gridwidth=2,
            zeroline=False,
            showline=True,
            linecolor='#000000',
            linewidth=3,
            tickfont=dict(color='#000000', size=14, family='Arial Black'),
            title="Y Axis Label - Can you read this?",
            title_font=dict(color='#000000', size=16, family='Arial Black')
        ),
        margin=dict(l=80, r=40, t=80, b=80)
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Test 2: Line Chart with Multiple Lines
    st.subheader("Test 2: Line Chart")
    
    dates = pd.date_range('2024-01-01', periods=7)
    data = pd.DataFrame({
        'Date': dates,
        'User Messages': [5, 8, 6, 12, 9, 7, 11],
        'AI Responses': [5, 8, 6, 12, 9, 7, 11]
    })
    
    fig2 = px.line(
        data, 
        x='Date', 
        y=['User Messages', 'AI Responses'],
        title="TEST: Line Chart - Check Legend and Labels",
        color_discrete_sequence=['#0066cc', '#ff6b6b']
    )
    
    fig2.update_layout(
        title={
            'text': "TEST: Line Chart - Check Legend and Labels",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#000000', 'family': 'Arial Black'}
        },
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(color='#000000', family='Arial Black', size=14),
        legend=dict(
            font=dict(color='#000000', size=14, family='Arial Black'),
            bgcolor='#ffffff',
            bordercolor='#000000',
            borderwidth=3
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='#cccccc',
            zeroline=False,
            showline=True,
            linecolor='#000000',
            linewidth=3,
            tickfont=dict(color='#000000', size=14, family='Arial Black'),
            title_font=dict(color='#000000', size=16, family='Arial Black')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#cccccc',
            gridwidth=2,
            zeroline=False,
            showline=True,
            linecolor='#000000',
            linewidth=3,
            tickfont=dict(color='#000000', size=14, family='Arial Black'),
            title_font=dict(color='#000000', size=16, family='Arial Black')
        ),
        margin=dict(l=80, r=40, t=80, b=80)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Test 3: Pie Chart
    st.subheader("Test 3: Pie Chart")
    
    fig3 = px.pie(
        values=[60, 40],
        names=['User Messages', 'AI Responses'],
        title="TEST: Pie Chart - Check All Text",
        color_discrete_sequence=['#0066cc', '#ff6b6b']
    )
    
    fig3.update_layout(
        title={
            'text': "TEST: Pie Chart - Check All Text",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#000000', 'family': 'Arial Black'}
        },
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(color='#000000', family='Arial Black', size=14),
        legend=dict(
            font=dict(color='#000000', size=14, family='Arial Black'),
            bgcolor='#ffffff',
            bordercolor='#000000',
            borderwidth=3
        ),
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    fig3.update_traces(
        textfont=dict(color='#000000', size=16, family='Arial Black'),
        textinfo='label+percent'
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # Verification Section
    st.markdown("---")
    st.header("🔍 Verification Checklist")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Check These Items:")
        checks = [
            "Chart titles are clearly visible",
            "X and Y axis labels are readable", 
            "Tick labels on axes are clear",
            "Legend text is visible",
            "Data labels on charts are readable",
            "All text is black and bold"
        ]
        
        for check in checks:
            st.write(f"• {check}")
    
    with col2:
        st.subheader("🎯 Expected Results:")
        st.write("• **All text should be BLACK and BOLD**")
        st.write("• **Chart backgrounds should be WHITE**") 
        st.write("• **No text should be invisible or hard to read**")
        st.write("• **All charts should look professional**")
    
    if st.button("🚀 I can see all text clearly!", type="primary"):
        st.success("🎉 Excellent! The chart display fix is working perfectly!")
        st.balloons()
        st.info("💡 You can now use the main application with confidence that all charts will display properly.")
    
    if st.button("❌ Some text is still hard to read"):
        st.error("😞 The fix needs more work. Please describe which specific text is hard to read.")
        st.info("🔧 Try refreshing the page or clearing your browser cache.")

if __name__ == "__main__":
    main() 