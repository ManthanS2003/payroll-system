import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page config
st.set_page_config(
    page_title="SAP ERP Payroll Management System",
    page_icon="💼",
    layout="wide"
)

# Title
st.title("🏢 SAP ERP Payroll Management System")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    working_days = st.number_input("Working Days/Month", min_value=20, max_value=30, value=26)
    ot_rate = st.number_input("Overtime Rate (x)", min_value=1.0, max_value=2.5, value=1.5, step=0.1)
    tax_percent = st.slider("Tax Deduction (%)", 0, 30, 10)
    
    st.markdown("---")
    st.header("📂 Upload Files")
    emp_file = st.file_uploader("Employee CSV", type=['csv'], key="emp")
    att_file = st.file_uploader("Attendance CSV", type=['csv'], key="att")

# Main content
if emp_file and att_file:
    try:
        # Load data
        employee_df = pd.read_csv(emp_file)
        attendance_df = pd.read_csv(att_file)
        
        # Clean data
        employee_df.columns = employee_df.columns.str.strip()
        attendance_df.columns = attendance_df.columns.str.strip()
        employee_df['Employee ID'] = employee_df['Employee ID'].astype(str)
        attendance_df['Employee ID'] = attendance_df['Employee ID'].astype(str)
        
        st.success("✅ Files uploaded successfully!")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Employees", len(employee_df))
        with col2:
            st.metric("Departments", employee_df['Department'].nunique())
        with col3:
            st.metric("Avg Salary", f"₹{employee_df['Base Salary (INR)'].mean():,.0f}")
        with col4:
            st.metric("Avg Leaves", f"{attendance_df['Leave Days'].mean():.1f} days")
        
        st.markdown("---")
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["💰 Salary Processing", "📊 Dashboard", "📋 Data View"])
        
        # Tab 1: Salary Processing
        with tab1:
            st.subheader("Process Employee Salary")
            
            # Employee selection
            employee_df['Display'] = employee_df['Employee ID'] + " - " + employee_df['Employee Name'] + " (" + employee_df['Department'] + ")"
            selected = st.selectbox("Select Employee", employee_df['Display'].tolist())
            
            if selected and st.button("💰 Calculate Salary", type="primary"):
                emp_id = selected.split(" - ")[0]
                emp_data = employee_df[employee_df['Employee ID'] == emp_id].iloc[0]
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
                        st.write(f"Tax ({tax_percent}%): ₹{tax:,.2f}")
                        st.write(f"PF (12%): ₹{pf:,.2f}")
                    
                    with col3:
                        st.success(f"### Net Salary\n## ₹{net:,.2f}")
                    
                    # Payslip
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
                    Tax ({tax_percent}%):       ₹{tax:>10,.2f}
                    PF (12%):        ₹{pf:>10,.2f}
                    ----------------------------------------
                    NET SALARY:      ₹{net:>10,.2f}
                    ========================================
                    """
                    
                    st.download_button("📥 Download Payslip", payslip, f"Payslip_{emp_id}.txt", "text/plain")
                else:
                    st.error("No attendance record found!")
        
        # Tab 2: Dashboard
        with tab2:
            st.subheader("📊 Analytics Dashboard")
            
            dept_salary = employee_df.groupby('Department')['Base Salary (INR)'].mean().sort_values()
            fig1 = px.bar(x=dept_salary.values, y=dept_salary.index, orientation='h',
                         title='Average Salary by Department',
                         color=dept_salary.values, color_continuous_scale='Viridis')
            st.plotly_chart(fig1, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                dept_count = employee_df['Department'].value_counts()
                fig2 = px.pie(values=dept_count.values, names=dept_count.index, title='Employee Distribution')
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                fig3 = px.histogram(employee_df, x='Base Salary (INR)', nbins=30,
                                   title='Salary Distribution', color_discrete_sequence=['#3b82f6'])
                st.plotly_chart(fig3, use_container_width=True)
            
            st.subheader("🏆 Top 10 Earners")
            top_earners = employee_df.nlargest(10, 'Base Salary (INR)')[['Employee Name', 'Department', 'Base Salary (INR)']]
            st.dataframe(top_earners, use_container_width=True)
        
        # Tab 3: Data View
        with tab3:
            st.subheader("Employee Master Data")
            st.dataframe(employee_df, use_container_width=True)
            st.subheader("Attendance Records")
            st.dataframe(attendance_df, use_container_width=True)
            
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
        st.info("Please check CSV file format")

else:
    st.info("""
    ### 📌 Getting Started
    
    1. Upload **Employee CSV** with columns:
       - Employee ID, Employee Name, Department, Designation, Base Salary (INR)
    
    2. Upload **Attendance CSV** with columns:
       - Employee ID, Leave Days, Overtime Hours
    
    3. Configure payroll settings in sidebar
    
    4. Process salaries and download payslips
    """)