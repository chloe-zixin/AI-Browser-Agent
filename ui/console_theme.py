from __future__ import annotations


def inject_console_theme() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: #f2f6f5;
            color: #18343a;
        }

        [data-testid="stHeader"] {
            background: rgba(242, 246, 245, 0.94);
        }

        [data-testid="stAppViewContainer"] .main .block-container {
            max-width: 1320px;
            padding: 2rem 2rem 3rem;
        }

        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"],
        [data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
            color: #18343a;
        }

        [data-testid="stAppViewContainer"] [data-testid="stMetric"] {
            min-height: 106px;
            padding: 14px 16px;
            border: 1px solid #d7e2e0;
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(24, 52, 58, 0.04);
        }

        [data-testid="stAppViewContainer"] [data-testid="stMetricLabel"] {
            color: #536b70;
        }

        [data-testid="stAppViewContainer"] [data-testid="stMetricValue"] {
            color: #145e56;
        }

        [data-testid="stAppViewContainer"] [data-testid="stDataFrame"] {
            overflow: hidden;
            border: 1px solid #d7e2e0;
            border-radius: 8px;
            background: #ffffff;
        }

        [data-testid="stAppViewContainer"] [data-testid="stTextInput"] input,
        [data-testid="stAppViewContainer"] [data-testid="stNumberInput"] input,
        [data-testid="stAppViewContainer"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            border-color: #c6d6d3;
            border-radius: 6px;
            background: #ffffff;
            color: #18343a;
        }

        [data-testid="stAppViewContainer"] [data-testid="stNumberInput"] button {
            border-color: #c6d6d3;
            background: #f5f8f7;
            color: #145e56;
        }

        [data-testid="stAppViewContainer"] [data-testid="stNumberInput"] button:hover {
            background: #e7f0ee;
            color: #0f4d47;
        }

        [data-testid="stAppViewContainer"] [data-testid="stForm"] {
            padding: 16px 18px 8px;
            margin: 16px 0 24px;
            border: 1px solid #d7e2e0;
            border-radius: 8px;
            background: #ffffff;
        }

        [data-testid="stAppViewContainer"] [data-testid="stFormSubmitButton"] button {
            width: 100%;
            min-height: 42px;
            border: 1px solid #145e56;
            border-radius: 6px;
            background: #145e56;
            color: #ffffff;
            box-shadow: none;
        }

        [data-testid="stAppViewContainer"] [data-testid="stFormSubmitButton"] button p,
        [data-testid="stAppViewContainer"] [data-testid="stFormSubmitButton"] button span {
            color: #ffffff;
        }

        [data-testid="stAppViewContainer"] [data-testid="stFormSubmitButton"] button:hover {
            border-color: #0f4d47;
            background: #0f4d47;
        }

        [data-testid="stAppViewContainer"] [data-testid="stButton"] button {
            width: auto;
            min-height: 38px;
            padding: 0.35rem 0.8rem;
            border: 1px solid #bfd0cd;
            border-radius: 6px;
            background: #ffffff;
            color: #145e56;
            box-shadow: none;
        }

        [data-testid="stAppViewContainer"] [data-testid="stButton"] button p,
        [data-testid="stAppViewContainer"] [data-testid="stButton"] button span {
            color: #145e56;
        }

        [data-testid="stAppViewContainer"] [data-testid="stButton"] button:hover {
            border-color: #145e56;
            background: #eaf3f1;
        }

        [data-testid="stAppViewContainer"] .st-key-source-page-link [data-testid="stLinkButton"] a {
            min-height: 40px;
            padding: 0.4rem 0.8rem;
            border: 1px solid #b8cbea;
            border-radius: 6px;
            background: #f8fafc;
            color: #175cd3;
            text-decoration: none;
            box-shadow: none;
        }

        [data-testid="stAppViewContainer"] .st-key-source-page-link [data-testid="stLinkButton"] a p {
            color: #175cd3 !important;
        }

        [data-testid="stAppViewContainer"] .st-key-source-page-link [data-testid="stLinkButton"] a:hover {
            border-color: #84adff;
            background: #eff6ff;
            color: #1849a9;
        }

        [data-testid="stAppViewContainer"] .st-key-source-page-link [data-testid="stLinkButton"] a:hover p {
            color: #1849a9 !important;
        }

        [data-testid="stAppViewContainer"] .st-key-source-page-link [data-testid="stLinkButton"] a:focus-visible {
            outline: 3px solid #84adff;
            outline-offset: 2px;
            border-color: #175cd3;
            background: #ffffff;
            color: #175cd3;
        }

        [data-testid="stAppViewContainer"] .st-key-source-page-link [data-testid="stLinkButton"] a:focus-visible p {
            color: #175cd3 !important;
        }

        [data-testid="stAppViewContainer"] [data-testid="stAlert"] {
            border: 1px solid #d7e2e0;
            border-radius: 6px;
            background: #ffffff;
        }

        [data-testid="stAppViewContainer"] [data-testid="stAlert"] p,
        [data-testid="stAppViewContainer"] [data-testid="stAlert"] span {
            color: #18343a;
        }

        @media (max-width: 700px) {
            [data-testid="stAppViewContainer"] .main .block-container {
                padding: 1.2rem 1rem 2rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )