@echo off
echo Installing required packages...
pip install streamlit pandas numpy plotly

echo.
echo Starting Payroll System...
python -m streamlit run payroll_app.py

pause