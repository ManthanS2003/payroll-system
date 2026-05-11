# install_and_run.ps1
Write-Host "Installing required packages..." -ForegroundColor Green
python -m pip install --upgrade pip
python -m pip install streamlit pandas numpy plotly

Write-Host "`nStarting Payroll Management System..." -ForegroundColor Green
python -m streamlit run payroll_app.py

Read-Host "`nPress Enter to exit"