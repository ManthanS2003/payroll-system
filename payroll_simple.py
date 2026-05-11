import pandas as pd
from datetime import datetime

def calculate_salary(employee, attendance, working_days=26, ot_rate=1.5, tax_rate=10):
    """Calculate salary based on attendance"""
    
    base = employee['Base Salary (INR)']
    leaves = attendance['Leave Days']
    overtime = attendance.get('Overtime Hours', 0)
    
    per_day = base / working_days
    leave_ded = per_day * leaves
    hourly_rate = base / (working_days * 8)
    ot_pay = hourly_rate * overtime * ot_rate
    gross = base - leave_ded + ot_pay
    tax = gross * (tax_rate / 100)
    pf = base * 0.12
    net = gross - tax - pf
    
    return {
        'name': employee['Employee Name'],
        'id': employee['Employee ID'],
        'dept': employee['Department'],
        'base': base,
        'leaves': leaves,
        'overtime': overtime,
        'leave_ded': leave_ded,
        'ot_pay': ot_pay,
        'gross': gross,
        'tax': tax,
        'pf': pf,
        'net': net
    }

def main():
    print("=" * 60)
    print("SAP ERP PAYROLL MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Load CSV files
    emp_file = input("\nEnter Employee CSV file path: ").strip()
    att_file = input("Enter Attendance CSV file path: ").strip()
    
    try:
        employee_df = pd.read_csv(emp_file)
        attendance_df = pd.read_csv(att_file)
        
        print(f"\n✅ Loaded {len(employee_df)} employees and {len(attendance_df)} attendance records")
        
        while True:
            print("\n" + "=" * 60)
            print("OPTIONS:")
            print("1. Process single employee")
            print("2. Process all employees")
            print("3. Show department statistics")
            print("4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                emp_id = input("Enter Employee ID: ").strip()
                emp = employee_df[employee_df['Employee ID'].astype(str) == emp_id]
                
                if len(emp) > 0:
                    att = attendance_df[attendance_df['Employee ID'].astype(str) == emp_id]
                    if len(att) > 0:
                        result = calculate_salary(emp.iloc[0], att.iloc[0])
                        
                        print("\n" + "=" * 60)
                        print(f"PAYSLIP - {result['name']}")
                        print("=" * 60)
                        print(f"Employee ID: {result['id']}")
                        print(f"Department: {result['dept']}")
                        print(f"\nEARNINGS:")
                        print(f"  Base Salary:     ₹{result['base']:>10,.2f}")
                        print(f"  Overtime Pay:    ₹{result['ot_pay']:>10,.2f}")
                        print(f"  Gross Salary:    ₹{result['gross']:>10,.2f}")
                        print(f"\nDEDUCTIONS:")
                        print(f"  Leave Deduction: ₹{result['leave_ded']:>10,.2f}")
                        print(f"  Tax (10%):       ₹{result['tax']:>10,.2f}")
                        print(f"  PF (12%):        ₹{result['pf']:>10,.2f}")
                        print(f"\nNET SALARY:       ₹{result['net']:>10,.2f}")
                        print("=" * 60)
                        
                        save = input("\nSave payslip? (y/n): ").lower()
                        if save == 'y':
                            with open(f"payslip_{emp_id}.txt", 'w') as f:
                                f.write(f"PAYSLIP - {result['name']}\n")
                                f.write(f"Net Salary: ₹{result['net']:,.2f}\n")
                            print("✅ Payslip saved!")
                    else:
                        print("❌ No attendance record found!")
                else:
                    print("❌ Employee not found!")
            
            elif choice == '2':
                print("\nProcessing all employees...")
                results = []
                
                for _, emp in employee_df.iterrows():
                    att = attendance_df[attendance_df['Employee ID'].astype(str) == str(emp['Employee ID'])]
                    if len(att) > 0:
                        result = calculate_salary(emp, att.iloc[0])
                        results.append(result)
                        print(f"  {result['name']}: ₹{result['net']:,.2f}")
                
                # Save to CSV
                df = pd.DataFrame(results)
                df.to_csv("all_salaries.csv", index=False)
                print(f"\n✅ Saved {len(results)} salary records to 'all_salaries.csv'")
            
            elif choice == '3':
                dept_stats = employee_df.groupby('Department').agg({
                    'Base Salary (INR)': ['mean', 'count']
                }).round(2)
                print("\nDepartment Statistics:")
                print(dept_stats)
            
            elif choice == '4':
                print("\nThank you for using SAP ERP Payroll System!")
                break
            
            else:
                print("Invalid choice!")
                
    except FileNotFoundError:
        print("❌ File not found! Please check the file path.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()