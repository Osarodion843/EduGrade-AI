"""EduGrade AI theme engine: light/dark CSS design tokens and the theme toggle."""

from __future__ import annotations

import streamlit as st

THEME_CSS_LIGHT = """
<style>
:root {
    --edu-bg-primary: #ffffff;
    --edu-bg-secondary: #f1f5f9;
    --edu-bg-tertiary: #f1f5f9;
    --edu-text-primary: #0f172a;
    --edu-text-secondary: #334155;
    --edu-text-muted: #64748b;
    --edu-accent: #2563eb;
    --edu-accent-hover: #1d4ed8;
    --edu-success: #10b981;
    --edu-success-bg: #d1fae5;
    --edu-warning: #f59e0b;
    --edu-warning-bg: #fef3c7;
    --edu-danger: #ef4444;
    --edu-border: #cbd5e1;
    --edu-card-bg: #ffffff;
    --edu-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
}

/* Force light mode on everything */
.stApp, .stApp * {
    background-color: var(--edu-bg-secondary) !important;
    color: var(--edu-text-primary) !important;
}

[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
.stSidebar,
.stSidebar * {
    background-color: var(--edu-bg-tertiary) !important;
    color: var(--edu-text-primary) !important;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--edu-text-primary) !important;
}

.edu-title {
    color: var(--edu-text-primary);
    font-weight: 700;
    letter-spacing: -0.025em;
}

.edu-subtitle {
    color: var(--edu-text-secondary);
}

.edu-card {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    margin-bottom: 1rem;
}

.edu-card-header {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--edu-text-primary);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.edu-metric-card {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 10px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

.edu-metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--edu-accent);
}

.edu-metric-label {
    font-size: 0.875rem;
    color: var(--edu-text-secondary);
    margin-top: 0.25rem;
}

.edu-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.625rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

.edu-badge-success {
    background: var(--edu-success-bg);
    color: var(--edu-success);
    border: 1px solid #a7f3d0;
}

.edu-badge-warning {
    background: var(--edu-warning-bg);
    color: #92400e;
    border: 1px solid #fcd34d;
}

.edu-badge-danger {
    background: #fee2e2;
    color: var(--edu-danger);
    border: 1px solid #fecaca;
}

.edu-badge-info {
    background: #dbeafe;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}

.edu-progress-tracker {
    background: var(--edu-card-bg);
    border: 1px solid var(--edu-border);
    border-radius: 10px;
    padding: 1rem;
    margin-top: 1rem;
}

.edu-progress-label {
    font-size: 0.875rem;
    color: var(--edu-text-secondary);
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
}

.edu-split-panel {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 10px;
    padding: 1rem;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.edu-feedback-box {
    background: #ffffff;
    border: 2px solid #cbd5e1;
    border-left: 4px solid var(--edu-accent);
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
    color: var(--edu-text-primary);
    box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.05);
}

.edu-question-row {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
}

.edu-q-number {
    font-weight: 700;
    color: var(--edu-accent);
    min-width: 2rem;
}

.edu-q-status {
    font-size: 0.75rem;
    font-weight: 600;
}

/* Input fields - force dark text on light background */
input, textarea, select,
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 2px solid #94a3b8 !important;
    border-radius: 8px !important;
}

input::placeholder, textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

/* Labels */
label, .stLabel, [data-testid="stWidgetLabel"] p {
    color: #0f172a !important;
    font-weight: 600 !important;
}

/* Buttons */
.stButton > button {
    background: #2563eb !important;
    color: white !important;
    border: 2px solid #1d4ed8 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.625rem 1.5rem !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: #1d4ed8 !important;
    border-color: #1e40af !important;
}

/* Metrics */
.stMetric {
    background: #ffffff !important;
    border: 2px solid #94a3b8 !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1) !important;
}

.stMetric > div {
    color: #0f172a !important;
}

.stMetric [data-testid="stMetricLabel"] {
    color: #334155 !important;
}

.stMetric [data-testid="stMetricValue"] {
    color: #2563eb !important;
}

/* Alerts */
.stAlert {
    background: #ffffff !important;
    border: 2px solid #94a3b8 !important;
    color: #0f172a !important;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1) !important;
}

/* File uploader */
.stFileUploader > div {
    background: #f8fafc !important;
    border: 2px solid #94a3b8 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}

.stFileUploader > div:hover {
    border-color: #2563eb !important;
    background: #f1f5f9 !important;
}

/* Radio buttons */
.stRadio > div {
    color: #0f172a !important;
}

.stRadio label {
    color: #0f172a !important;
    font-weight: 500 !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 2px solid #94a3b8 !important;
    border-radius: 8px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #f1f5f9 !important;
    border-bottom: 2px solid #cbd5e1 !important;
}

.stTabs [data-baseweb="tab"] {
    color: #334155 !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #2563eb !important;
    border-bottom: 2px solid #2563eb !important;
}

/* Divider */
hr, .stDivider {
    border-color: #cbd5e1 !important;
    border-width: 2px !important;
}

/* Caption text */
.stCaption, .stCaption p {
    color: #334155 !important;
}

/* Info/warning/error boxes */
.stAlert > div {
    color: #0f172a !important;
}

/* Container for the main app */
[data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
}

/* Main container */
.block-container {
    background-color: #f8fafc !important;
    padding-top: 2rem !important;
}
</style>
"""

THEME_CSS_DARK = """
<style>
:root {
    --edu-bg-primary: #0f172a;
    --edu-bg-secondary: #020617;
    --edu-bg-tertiary: #1e293b;
    --edu-text-primary: #f1f5f9;
    --edu-text-secondary: #94a3b8;
    --edu-text-muted: #64748b;
    --edu-accent: #60a5fa;
    --edu-accent-hover: #3b82f6;
    --edu-success: #34d399;
    --edu-success-bg: #064e3b;
    --edu-warning: #fbbf24;
    --edu-warning-bg: #451a03;
    --edu-danger: #f87171;
    --edu-border: #334155;
    --edu-card-bg: #1e293b;
    --edu-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.2);
}

.stApp {
    background-color: var(--edu-bg-secondary);
}

h1, h2, h3, h4, h5, h6 {
    color: var(--edu-text-primary) !important;
}

.edu-title {
    color: var(--edu-text-primary);
    font-weight: 700;
    letter-spacing: -0.025em;
}

.edu-subtitle {
    color: var(--edu-text-secondary);
}

.edu-card {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    margin-bottom: 1rem;
}

.edu-card-header {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--edu-text-primary);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.edu-metric-card {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 10px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

.edu-metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--edu-accent);
}

.edu-metric-label {
    font-size: 0.875rem;
    color: var(--edu-text-muted);
    margin-top: 0.25rem;
}

.edu-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.625rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

.edu-badge-success {
    background: var(--edu-success-bg);
    color: var(--edu-success);
    border: 1px solid #065f46;
}

.edu-badge-warning {
    background: var(--edu-warning-bg);
    color: #fbbf24;
    border: 1px solid #b45309;
}

.edu-badge-danger {
    background: #450a0a;
    color: var(--edu-danger);
    border: 1px solid #7f1d1d;
}

.edu-badge-info {
    background: #1e3a8a;
    color: #93c5fd;
    border: 1px solid #1e40af;
}

.edu-progress-tracker {
    background: #1e293b !important;
    border: 2px solid #334155 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    margin-top: 1rem !important;
}

.edu-progress-label {
    font-size: 0.875rem;
    color: #94a3b8 !important;
    margin-bottom: 0.5rem !important;
    display: flex;
    justify-content: space-between;
}

.edu-split-panel {
    background: #1e293b !important;
    border: 2px solid #334155 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

.edu-feedback-box {
    background: #1e293b !important;
    border: 2px solid #334155 !important;
    border-left: 4px solid var(--edu-accent) !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    margin-top: 1rem !important;
    color: #f1f5f9 !important;
    box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.3) !important;
}

.edu-question-row {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
    padding: 0.75rem !important;
    margin-bottom: 0.5rem !important;
}

.edu-q-number {
    font-weight: 700;
    color: var(--edu-accent);
    min-width: 2rem;
}

.edu-q-status {
    font-size: 0.75rem;
    font-weight: 600;
}

input, textarea, select {
    background-color: #0f172a !important;
    color: #f1f5f9 !important;
    border: 2px solid #334155 !important;
    border-radius: 8px !important;
}

input::placeholder, textarea::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

/* Buttons */
.stButton > button {
    background: #60a5fa !important;
    color: #0f172a !important;
    border: 2px solid #3b82f6 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.625rem 1.5rem !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: #3b82f6 !important;
    border-color: #2563eb !important;
}

/* Metrics */
.stMetric {
    background: #1e293b !important;
    border: 2px solid #334155 !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.2) !important;
}

.stMetric > div {
    color: #f1f5f9 !important;
}

.stMetric [data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

.stMetric [data-testid="stMetricValue"] {
    color: #60a5fa !important;
}

/* Alerts */
.stAlert {
    background: #1e293b !important;
    border: 2px solid #334155 !important;
    color: #f1f5f9 !important;
    box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.3) !important;
}

/* File uploader */
.stFileUploader > div {
    background: #1e293b !important;
    border: 2px solid #334155 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}

.stFileUploader > div:hover {
    border-color: #60a5fa !important;
    background: #0f172a !important;
}

/* Radio buttons */
.stRadio > div {
    color: #f1f5f9 !important;
}

.stRadio label {
    color: #f1f5f9 !important;
    font-weight: 500 !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background-color: #0f172a !important;
    color: #f1f5f9 !important;
    border: 2px solid #334155 !important;
    border-radius: 8px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #1e293b !important;
    border-bottom: 2px solid #334155 !important;
}

.stTabs [data-baseweb="tab"] {
    color: #94a3b8 !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #60a5fa !important;
    border-bottom: 2px solid #60a5fa !important;
}

/* Divider */
hr, .stDivider {
    border-color: #334155 !important;
    border-width: 2px !important;
}

/* Caption text */
.stCaption, .stCaption p {
    color: #94a3b8 !important;
}

/* Info/warning/error boxes */
.stAlert > div {
    color: #f1f5f9 !important;
}

/* Input fields - force light text on dark background */
input, textarea, select,
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background-color: #0f172a !important;
    color: #f1f5f9 !important;
    border: 2px solid #334155 !important;
}

input::placeholder, textarea::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

/* Labels */
label, .stLabel, [data-testid="stWidgetLabel"] p {
    color: var(--edu-text-primary) !important;
    font-weight: 500 !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background-color: var(--edu-bg-primary) !important;
    color: var(--edu-text-primary) !important;
    border: 1px solid var(--edu-border) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--edu-bg-tertiary) !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--edu-text-secondary) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--edu-accent) !important;
}

/* Divider */
hr, .stDivider {
    border-color: var(--edu-border) !important;
}

/* Caption text */
.stCaption, .stCaption p {
    color: var(--edu-text-secondary) !important;
}

/* Info/warning/error boxes */
.stAlert > div {
    color: var(--edu-text-primary) !important;
}
</style>
"""


def inject_theme_css(theme: str) -> None:
    if theme == "dark":
        st.markdown(THEME_CSS_DARK, unsafe_allow_html=True)
    else:
        st.markdown(THEME_CSS_LIGHT, unsafe_allow_html=True)


def theme_toggle_button() -> None:
    current = st.session_state.get("theme", "light")
    label = "Dark Mode" if current == "light" else "Light Mode"
    if st.button(label, key="theme_toggle", width="stretch"):
        st.session_state.theme = "dark" if current == "light" else "light"
        st.rerun()

