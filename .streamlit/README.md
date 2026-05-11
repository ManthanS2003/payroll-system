# SAP ERP Payroll Management System

An enterprise-grade payroll management system built with Streamlit, featuring automated salary calculations, tax deductions, and real-time analytics.

## Features

- ✅ Automated salary calculation with tax & deductions
- ✅ Professional Tax and Provident Fund calculations
- ✅ Overtime calculation with multiplier
- ✅ Interactive dashboards and analytics
- ✅ Bulk salary export to Excel
- ✅ Professional payslip generation
- ✅ Department-wise analytics
- ✅ Employee performance tracking

## Demo

Upload your employee and attendance CSV files to get started:

### Employee CSV Format
- Employee ID
- Employee Name
- Department
- Designation
- Base Salary (INR)
- Bonus (INR)
- Net Salary (INR)
- Payment Date

### Attendance CSV Format
- Employee ID
- Leave Days
- Overtime Hours

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py