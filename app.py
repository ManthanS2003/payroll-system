import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import base64
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================================
# CLOUD DEPLOYMENT CONFIGURATION
# =========================================
# Set page config MUST be the first Streamlit command
st.set_page_config(
    page_title="SAP ERP Payroll Management System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# CUSTOM CSS FOR BETTER UI
# =========================================
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .salary-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3B82F6;
    }
    </style>
""", unsafe_allow_html=True)

# Custom CSS
# st.markdown("""
# <style>
#     .stApp {
#         background-color: #f5f7fa;
#     }
#     .big-font {
#         font-size: 30px !important;
#         font-weight: bold;
#         color: #1e3a8a;
#     }
#     .salary-box {
#         background-color: #10b981;
#         padding: 20px;
#         border-radius: 10px;
#         color: white;
#         text-align: center;
#     }
#     .info-box {
#         background-color: #3b82f6;
#         padding: 15px;
#         border-radius: 10px;
#         color: white;
#     }
# </style>
# """, unsafe_allow_html=True)

# Title
st.markdown("<p class='big-font'>🏢 SAP ERP Payroll Management System</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    working_days = st.number_input("Working Days/Month", min_value=20, max_value=30, value=26)
    ot_rate = st.number_input("Overtime Rate (x)", min_value=1.0, max_value=2.5, value=1.5, step=0.1)
    tax_percent = st.slider("Tax Deduction (%)", 0, 30, 10)
    
    st.markdown("---")
    st.header("📂 Upload Files")
    
    # File uploaders
    emp_file = st.file_uploader("Employee CSV", type=['csv'], key="emp")
    att_file = st.file_uploader("Attendance CSV", type=['csv'], key="att")

# Main content
if emp_file is not None and att_file is not None:
    try:
        # Read CSV files
        employee_df = pd.read_csv(emp_file)
        attendance_df = pd.read_csv(att_file)
        
        # Clean column names
        employee_df.columns = employee_df.columns.str.strip()
        attendance_df.columns = attendance_df.columns.str.strip()
        
        # Convert IDs to string
        employee_df['Employee ID'] = employee_df['Employee ID'].astype(str)
        attendance_df['Employee ID'] = attendance_df['Employee ID'].astype(str)
        
        st.success("✅ Files uploaded successfully!")
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Employees", len(employee_df))
        with col2:
            st.metric("Departments", employee_df['Department'].nunique())
        with col3:
            avg_salary = employee_df['Base Salary (INR)'].mean()
            st.metric("Avg Salary", f"₹{avg_salary:,.0f}")
        with col4:
            avg_leaves = attendance_df['Leave Days'].mean()
            st.metric("Avg Leaves", f"{avg_leaves:.1f} days")
        
        st.markdown("---")
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["💰 Salary Processing", "📊 Dashboard", "📋 Data View"])
        
        # Tab 1: Salary Processing
        with tab1:
            st.subheader("Process Employee Salary")
            
            # Search and select
            search = st.text_input("🔍 Search Employee (Name or ID)")
            
            if search:
                filtered = employee_df[
                    employee_df['Employee Name'].str.contains(search, case=False) |
                    employee_df['Employee ID'].str.contains(search, case=False)
                ]
            else:
                filtered = employee_df
            
            # Create display names
            employee_df['Display'] = employee_df['Employee ID'] + " - " + employee_df['Employee Name'] + " (" + employee_df['Department'] + ")"
            
            selected = st.selectbox("Select Employee", employee_df['Display'].tolist())
            
            if selected and st.button("💰 Calculate Salary", type="primary"):
                emp_id = selected.split(" - ")[0]
                
                # Get employee data
                emp_data = employee_df[employee_df['Employee ID'] == emp_id].iloc[0]
                
                # Get attendance data
                att_data = attendance_df[attendance_df['Employee ID'] == emp_id]
                
                if len(att_data) > 0:
                    att_record = att_data.iloc[0]
                    leaves = att_record['Leave Days']
                    overtime = att_record.get('Overtime Hours', 0) if 'Overtime Hours' in att_record else 0
                    
                    # Calculations
                    base = emp_data['Base Salary (INR)']
                    per_day = base / working_days
                    leave_ded = per_day * leaves
                    hourly_rate = base / (working_days * 8)
                    ot_pay = hourly_rate * overtime * ot_rate
                    gross = base - leave_ded + ot_pay
                    tax = gross * (tax_percent / 100)
                    pf = base * 0.12
                    net = gross - tax - pf
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 👤 Employee Details")
                        st.write(f"**Name:** {emp_data['Employee Name']}")
                        st.write(f"**ID:** {emp_data['Employee ID']}")
                        st.write(f"**Department:** {emp_data['Department']}")
                        st.write(f"**Designation:** {emp_data['Designation']}")
                    
                    with col2:
                        st.markdown("### 📅 Attendance")
                        st.write(f"**Leave Days:** {leaves}")
                        st.write(f"**Overtime Hours:** {overtime}")
                        st.write(f"**Working Days:** {working_days - leaves}")
                    
                    st.markdown("### 💵 Salary Breakdown")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info("**Earnings**")
                        st.write(f"Base: ₹{base:,.2f}")
                        st.write(f"OT Pay: ₹{ot_pay:,.2f}")
                        st.success(f"Gross: ₹{gross:,.2f}")
                    
                    with col2:
                        st.warning("**Deductions**")
                        st.write(f"Leave: ₹{leave_ded:,.2f}")
                        st.write(f"Tax (10%): ₹{tax:,.2f}")
                        st.write(f"PF (12%): ₹{pf:,.2f}")
                    
                    with col3:
                        st.markdown('<div class="salary-box">', unsafe_allow_html=True)
                        st.markdown(f"### Net Salary")
                        st.markdown(f"## ₹{net:,.2f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Payslip generation
                    payslip = f"""
                    ========================================
                    SAP ERP PAYSLIP
                    ========================================
                    
                    Employee: {emp_data['Employee Name']}
                    ID: {emp_data['Employee ID']}
                    Department: {emp_data['Department']}
                    
                    ----------------------------------------
                    EARNINGS
                    ----------------------------------------
                    Base Salary:     ₹{base:>10,.2f}
                    Overtime Pay:    ₹{ot_pay:>10,.2f}
                    ----------------------------------------
                    GROSS SALARY:    ₹{gross:>10,.2f}
                    
                    DEDUCTIONS
                    ----------------------------------------
                    Leave Deduction: ₹{leave_ded:>10,.2f}
                    Tax (10%):       ₹{tax:>10,.2f}
                    PF (12%):        ₹{pf:>10,.2f}
                    ----------------------------------------
                    NET SALARY:      ₹{net:>10,.2f}
                    ========================================
                    """
                    
                    st.download_button(
                        "📥 Download Payslip",
                        payslip,
                        f"Payslip_{emp_id}.txt",
                        "text/plain"
                    )
                else:
                    st.error("No attendance record found!")
        
        # Tab 2: Dashboard
        with tab2:
            st.subheader("📊 Analytics Dashboard")
            
            # Department salary chart
            dept_salary = employee_df.groupby('Department')['Base Salary (INR)'].mean().sort_values()
            fig1 = px.bar(x=dept_salary.values, y=dept_salary.index, orientation='h',
                         title='Average Salary by Department',
                         color=dept_salary.values, color_continuous_scale='Viridis')
            st.plotly_chart(fig1, use_container_width=True)
            
            # Department distribution
            col1, col2 = st.columns(2)
            with col1:
                dept_count = employee_df['Department'].value_counts()
                fig2 = px.pie(values=dept_count.values, names=dept_count.index, title='Employee Distribution')
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                # Salary distribution
                fig3 = px.histogram(employee_df, x='Base Salary (INR)', nbins=30,
                                   title='Salary Distribution', color_discrete_sequence=['#3b82f6'])
                st.plotly_chart(fig3, use_container_width=True)
            
            # Top earners
            st.subheader("🏆 Top 10 Earners")
            top_earners = employee_df.nlargest(10, 'Base Salary (INR)')[['Employee Name', 'Department', 'Base Salary (INR)']]
            st.dataframe(top_earners, use_container_width=True)
        
        # Tab 3: Data View
        with tab3:
            st.subheader("Employee Master Data")
            st.dataframe(employee_df, use_container_width=True)
            
            st.subheader("Attendance Records")
            st.dataframe(attendance_df, use_container_width=True)
            
            # Export option
            if st.button("Export All Salaries"):
                all_salaries = []
                for _, emp in employee_df.iterrows():
                    att = attendance_df[attendance_df['Employee ID'] == str(emp['Employee ID'])]
                    if len(att) > 0:
                        leaves = att.iloc[0]['Leave Days']
                        overtime = att.iloc[0].get('Overtime Hours', 0)
                        
                        base = emp['Base Salary (INR)']
                        per_day = base / working_days
                        leave_ded = per_day * leaves
                        hourly_rate = base / (working_days * 8)
                        ot_pay = hourly_rate * overtime * ot_rate
                        gross = base - leave_ded + ot_pay
                        tax = gross * (tax_percent / 100)
                        pf = base * 0.12
                        net = gross - tax - pf
                        
                        all_salaries.append({
                            'Employee ID': emp['Employee ID'],
                            'Name': emp['Employee Name'],
                            'Department': emp['Department'],
                            'Base Salary': base,
                            'Leaves': leaves,
                            'Leave Deduction': leave_ded,
                            'Overtime Pay': ot_pay,
                            'Gross Salary': gross,
                            'Tax': tax,
                            'PF': pf,
                            'Net Salary': net
                        })
                
                salary_df = pd.DataFrame(all_salaries)
                st.dataframe(salary_df, use_container_width=True)
                
                csv = salary_df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv, "all_salaries.csv", "text/csv")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please ensure CSV files have correct columns: 'Employee ID', 'Employee Name', 'Department', 'Designation', 'Base Salary (INR)'")

else:
    st.info("""
    ### 📌 Getting Started
    
    1. Upload **Employee CSV** file with columns:
       - Employee ID, Employee Name, Department, Designation, Base Salary (INR)
    
    2. Upload **Attendance CSV** file with columns:
       - Employee ID, Leave Days, Overtime Hours
    
    3. Configure payroll settings in sidebar
    
    4. Process salaries and download payslips
    """)
    
    # Sample data preview
    with st.expander("📝 Sample CSV Format"):
        st.code("""
        Employee CSV Format:
        Employee ID,Employee Name,Department,Designation,Base Salary (INR)
        1001,John Doe,IT,Developer,50000
        1002,Jane Smith,HR,Manager,60000
        
        Attendance CSV Format:
        Employee ID,Leave Days,Overtime Hours
        1001,2,5
        1002,0,10
        """)