import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

#Set input variables at 0 (to avoid contamination from previous calculations)
salary = 0
salary_sacrifice = 0
benefits = 0
interest = 0
property_ = 0
pension_gross = 0
pension_gross_pc = 0
pension_net = 0
pension_net_grossed_up = 0
pension_net_monthly = 0
excess_pension = 0
employer_pension = 0
employer_pension_pc = 0
employer_total = 0
gift_aid = 0
gift_aid_grossed_up = 0
net_income = 0
adjusted_net_income = 0
no_income = 0
psa = 0
taxable_interest = 0
taxable_income = 0
inc_tax = 0
reduced_allowance = 0
tax_relief_claim = 0
salary_for_ni = 0
national_insurance = 0
money_received = 0
money_received_monthly = 0
pension = 0
pension_rate = 0
effective_tax_rate = 0
employer_ni = 0
employer_costs = 0
employer_costs_pc = 0

#Define HMRC thresholds (which can change from year to year)
lower_threshold = 12570
secondary_threshold = 50270
tertiary_threshold = 100000
higher_threshold = 125140

st.title(":pound: :red[TAX] :rainbow[SELF-ASSESSMENT CALCULATOR] :green[for PAYE employees]")
st.subheader("*Please submit the following information\:*")
####################################################################################################
#Collect input data
salary = st.number_input("What is your salary?", step=10000.00, icon=":material/currency_pound:")
interest = st.number_input("What income do you receive from bank interest?", step=10.00, icon=":material/currency_pound:")
property_ = st.number_input("What taxable income do you receive from property?", step=1000.00, icon=":material/currency_pound:")
benefits = st.number_input("What benefits in kind do you receive? (e.g. health insurance)", step=100.00, icon=":material/currency_pound:")
gift_aid = st.number_input("How much have you contributed to charity?", step=10.00, icon=":material/currency_pound:")
gift_aid_grossed_up = gift_aid * 1.25

####################################################################################################
#Establish if pension contributions are net or gross

salary_sacrifice = st.number_input("How much do you contribute to your pension via salary sacrifice each month? (type 0 if nothing)", step=100.00, icon=":material/currency_pound:" )
pension_type = st.radio("What other method do you use to contribute to your pension?", 
                        ["Gross Contribution", "Net contribution", "None"],
                        captions = ["(without tax relief)", "(with 20% tax relief)", "",])
if pension_type == "Gross Contribution":
    pension_gross_pc = st.number_input("What percentage of your salary do you contribute?", step=1.0, icon=":material/percent:")
    pension_gross = pension_gross_pc/100 * salary

elif pension_type == "Net contribution":
    pension_net_monthly = st.number_input("How much do you contribute each month?", step=100.00, icon=":material/currency_pound:")
    pension_net = pension_net_monthly * 12
    pension_net_grossed_up = pension_net * 1.25
    
####################################################################################################
#Calculate Employer pension contribution
employer_pension_pc= st.number_input("What percentage of your salary does your employer contribute?", step=1.0, icon=":material/percent:")
employer_pension = employer_pension_pc/100 * salary
pension_total = (salary_sacrifice*12) + pension_gross + pension_net_grossed_up + employer_pension

####################################################################################################
#Calculate net income and adjusted net income  
net_income = round(salary - (salary_sacrifice*12) + benefits + interest + property_- pension_gross,2)
adjusted_net_income = round(net_income - pension_net_grossed_up - gift_aid_grossed_up,2)

####################################################################################################
#Calculate Pension Savings Allowance (dependent on adjusted net income)
if secondary_threshold < adjusted_net_income <= higher_threshold:
    psa = 500
elif adjusted_net_income <= secondary_threshold:
    psa = 1000
    
if interest <= psa:
    taxable_interest = 0
elif interest > psa:
    taxable_interest = interest-psa

#Calculate any additional tax due on pension contributions over £60,000
if pension_total > 60000:
    excess_pension = pension_total - 60000
taxable_income = net_income - interest + taxable_interest + excess_pension

####################################################################################################
#Income Tax calculation
if no_income <= taxable_income <= lower_threshold:
    inc_tax = 0
elif lower_threshold < taxable_income <= secondary_threshold:
    inc_tax = (taxable_income - lower_threshold) * .2
elif secondary_threshold < taxable_income <= higher_threshold:
    inc_tax = 7540 + ((taxable_income - secondary_threshold) * .4)
    if tertiary_threshold < adjusted_net_income <= higher_threshold:
        reduced_allowance = (adjusted_net_income - tertiary_threshold) / 2
        inc_tax = inc_tax + (reduced_allowance * .4)
    if pension_type == 2:
        if taxable_income - pension_net_grossed_up <= secondary_threshold:
            tax_relief_claim = (taxable_income + pension_net_grossed_up - secondary_threshold)*.2
        elif taxable_income - pension_net_grossed_up > secondary_threshold:
            tax_relief_claim = pension_net_grossed_up *.2
elif higher_threshold < taxable_income:
    inc_tax = 7540+19892+15084+((taxable_income - higher_threshold) * .45)
    if pension_type == 2:
        if taxable_income - pension_net_grossed_up <= higher_threshold:
            tax_relief_claim = (pension_net_grossed_up - (higher_threshold - (taxable_income - pension_net_grossed_up)))*.25 + (higher_threshold - (taxable_income - pension_net_grossed_up))*.2
        elif taxable_income - pension_net_grossed_up > higher_threshold:
            tax_relief_claim = pension_net_grossed_up *.25
############################################################################################################
#National Insurance calculation
salary_for_ni = salary - (salary_sacrifice * 12)
if lower_threshold < salary_for_ni <= secondary_threshold:
    national_insurance = (salary_for_ni-lower_threshold) * .08
elif secondary_threshold < salary_for_ni:
    national_insurance = 3016 + ((salary_for_ni-secondary_threshold) * .02)
elif no_income <= salary_for_ni <= lower_threshold:
    national_insurance = 0
    
money_received = net_income - benefits - pension_net - inc_tax - national_insurance
money_received_monthly = money_received / 12
pension = pension_net + pension_gross + (salary_sacrifice * 12)
try:
  pension_rate = pension / salary * 100
except ZeroDivisionError:
  pension_rate = 0
try:
  effective_tax_rate = (net_income - money_received + pension) / (net_income + pension) *100
except ZeroDivisionError:
  effective_tax_rate = 0
employer_ni = (salary_for_ni - 5000) * 0.15
employer_costs = salary + employer_ni + employer_pension + benefits
try:
  employer_costs_pc = ((employer_costs / salary) -1) * 100
except ZeroDivisionError:
  employer_costs_pc = 0

####################################################################################################
#Tax Report

st.header("**TAX REPORT**", divider=True)
st.header("1. Take-home pay", divider=True)
st.write(f"### With an annual net income of £{net_income:,.2f} you would receive £{money_received_monthly:,.2f} each month.")
st.write(f"### The total you would receive for the year is £{money_received:,.2f}")

st.header("2. Tax paid", divider=True)
if tertiary_threshold < adjusted_net_income <= higher_threshold:
    st.write(f"### Your Adjusted Net Income is £{adjusted_net_income:,.2f}")
    st.write("(for more information about how this was calculated, see below)")
    st.write("As this is between £100,000 and £125,140, I'm afraid you're in the 60% trap!")
    st.write("This means that you lose £1 of your personal allowance for every £2 over £100,000")
    st.write("You could avoid this by increasing your pension contributions or giving more to charity.")
st.write(f"### Income Tax: £{inc_tax:,.2f}")
st.write(f"### National Insurance: £{national_insurance:,.2f}")
st.write(f"### {effective_tax_rate:.2f}% of your total income is paid in tax.")

st.header("3. Pension contributions", divider=True)
st.write(f"### {pension_rate:.2f}% of your salary (£{pension:,.2f}) has been put into your pension fund.")
st.write(f"### Your employer has contributed a further £{employer_pension:,.2f}")
st.write(f"### Therefore, £{pension_total:,.2f} will be put into your pension pot this year.")
if pension_total > 60000:
    st.write(f"However, only £60,000 can be contributed to your pension pot tax-free, so an additional £{excess_pension:,.2f} was added to your taxable income and included in the calculations above.")
if secondary_threshold < taxable_income <= higher_threshold:
    if pension_type == 2:
        st.write("As you paid pension contributions with 20% tax deducted, but should have had 40% deducted for some or all of it, you are eligible to claim some more tax relief.")
        if taxable_income - pension_net_grossed_up <= secondary_threshold:
            tax_relief_claim = (taxable_income + pension_net_grossed_up - secondary_threshold)*.2
        elif taxable_income - pension_net_grossed_up > secondary_threshold:
            tax_relief_claim = pension_net_grossed_up *.2
        st.write(f"You can claim £{tax_relief_claim:,.2f}")
elif higher_threshold < taxable_income:
    inc_tax = 7540+19892+15084+((taxable_income - higher_threshold) * .45)
    if pension_type == 2:
        st.write("As you paid pension contributions with 20% tax deducted, but should have had 40 or 45% deducted for some or all of it, you are eligible to claim some more tax relief.")
        if taxable_income - pension_net_grossed_up <= higher_threshold:
            tax_relief_claim = (pension_net_grossed_up - (higher_threshold - (taxable_income - pension_net_grossed_up)))*.25 + (higher_threshold - (taxable_income - pension_net_grossed_up))*.2
        elif taxable_income - pension_net_grossed_up > higher_threshold:
            tax_relief_claim = pension_net_grossed_up *.25
        st.write(f"You can claim £{tax_relief_claim:,.2f}")
st.header("4. Employer contributions", divider=True)
st.write(f"### Pension contribution: £{employer_pension:,.2f}")
st.write(f"### National Insurance contribution: £{employer_ni:,.2f}")
st.write(f"### Employer benefits: £{benefits:,.2f}")
st.write(f"### Therefore, your employer has spent £{employer_costs:,.2f}")
st.write(f"### This is {employer_costs_pc:.2f}% more than your salary alone")

st.write("NB Your Adjusted Net Income takes into account pension contributions and charitable giving to achieve the following:")
st.write(" - if you earn just over £50,270, it preserves your £1000 Personal Savings Allowance")
st.write(" - if you earn between £100,000 and £125,140, it helps to preserve your Personal Tax Allowance of £12570")
st.write(" - if you earn between £60,000 and £80,000, it helps to maximise the amount of Child Benefit you can claim")
####################################################################################################
#Calculate Child Benefit
HICBC_lower_threshold = 60000
HICBC_upper_threshold = 80000

st.header("4. Child Benefit", divider=True)
if adjusted_net_income > HICBC_upper_threshold:
    st.write("### You are not eligible for Child Benefit payments.")
    st.write("### Thank you for using this calculator!")

if adjusted_net_income <= HICBC_upper_threshold:
    while True: 
        query = st.toggle("You are eligible for Child benefit payments if you have children. Activate to claim.")
        st.write("Thank you for using this calculator!")
    if query:
        children = st.selectbox("How many children do you have?",
                                ("1","2","3","4","5"),
                                index=None,
                                placeholder="Choose a number",)
        if children == 1:
            monthly_cb = 108.20
        elif children == 2: 
            monthly_cb = 179.80
        elif children == 3: 
            monthly_cb = 251.40
        elif children == 4: 
            monthly_cb = 323.00
        elif children == 5: 
            monthly_cb = 394.60
        if adjusted_net_income < HICBC_lower_threshold:
            st.write(f"You will also receive 13 payments of £{monthly_cb:.2f}, which amounts to £{(monthly_cb * 13):.2f}")
            st.write("Thank you for using this calculator!")
        if HICBC_lower_threshold < adjusted_net_income <= HICBC_upper_threshold:
            HICBC = (adjusted_net_income - HICBC_lower_threshold) // 200
            child_benefit_repayment = (monthly_cb * 13) * HICBC / 100
            st.write(f"Although you will receive 13 payments of £{monthly_cb:.2f}, which amounts to £{(monthly_cb * 13):.2f} per year, you will have to pay back {HICBC:.2f}% per year of your child benefit (£{child_benefit_repayment:,.2f}, leaving you with £{((monthly_cb * 13) - child_benefit_repayment):.2f} for the year or £{(((monthly_cb * 13) - child_benefit_repayment)/13):.2f} every 4 weeks.")
            st.write("Thank you for using this calculator!")
    else: 
        st.write("Thank you for using this calculator!")


        





