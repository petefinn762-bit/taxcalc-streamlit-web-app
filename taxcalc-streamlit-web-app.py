import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

#Set input variables at 0 (to avoid contamination from previous calculations)
salary_sacrifice = 0
benefits = 0
interest = 0
property_ = 0
pension_gross = 0
pension_net = 0
pension_net_grossed_up = 0
excess_pension = 0
gift_aid_grossed_up = 0
no_income = 0
psa = 0
taxable_interest = 0

#Define HMRC thresholds (which can change from year to year)
lower_threshold = 12570
secondary_threshold = 50270
tertiary_threshold = 100000
higher_threshold = 125140

st.title(":pound: :red[TAX] :rainbow[SELF-ASSESSMENT CALCULATOR] :green[for PAYE employees]")
st.subheader("*Please submit the following information*")
####################################################################################################
#Collect input data
salary = st.number_input("What is your salary?", step=10000, icon=":material/currency_pound:")
interest = st.number_input("What income do you receive from bank interest?", step=10, icon=":material/currency_pound:")
property_ = st.number_input("What taxable income do you receive from property?", step=1000, icon=":material/currency_pound:")
benefits = st.number_input("What benefits in kind do you receive? (e.g. health insurance)", step=100, icon=":material/currency_pound:")
gift_aid = st.number_input("How much have you contributed to charity?", step=10, icon=":material/currency_pound:")
gift_aid_grossed_up = gift_aid * 1.25

####################################################################################################
#Establish if pension contributions are net or gross

salary_sacrifice = st.number_input("How much do you contribute to your pension via salary sacrifice each month? (type 0 if nothing)", step=100, icon=":material/currency_pound:" )
pension_type = st.radio("What other method do you use to contribute to your pension?", 
                        ["Gross Contribution", "Net contribution", "None"],
                        captions = "(without tax relief)", "(with 20% tax relief)", "")
if pension_type == "Gross Contribution":
    pension_gross_pc = st.number_input("What percentage of your salary do you contribute?", icon=":material/percent:")
    pension_gross = pension_gross_pc/100 * salary

elif pension_type == "Net contribution":
    pension_net_monthly = st.number_input("How much do you contribute each month?", step=100, icon=":material/currency_pound:")
    pension_net = pension_net_monthly * 12
    pension_net_grossed_up = pension_net * 1.25
    
####################################################################################################
#Calculate Employer pension contribution
employer_pension_pc= st.number_input("What percentage of your salary does your employer contribute?", icon=":material/percent:")
employer_pension = employer_pension_pc/100 * salary
pension_total = (salary_sacrifice*12) + pension_gross + pension_net_grossed_up + employer_pension

####################################################################################################
#Calculate net income and adjusted net income  
net_income = salary - (salary_sacrifice*12) + benefits + interest + property_- pension_gross
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
    inc_tax = round((taxable_income - lower_threshold) * .2,2)
elif secondary_threshold < taxable_income <= higher_threshold:
    inc_tax = round(7540 + ((taxable_income - secondary_threshold) * .4),2)
    if tertiary_threshold < adjusted_net_income <= higher_threshold:
        reduced_allowance = (adjusted_net_income - tertiary_threshold) / 2
        inc_tax = inc_tax + (reduced_allowance * .4)
    if pension_type == 2:
        if taxable_income - pension_net_grossed_up <= secondary_threshold:
            tax_relief_claim = (taxable_income + pension_net_grossed_up - secondary_threshold)*.2
        elif taxable_income - pension_net_grossed_up > secondary_threshold:
            tax_relief_claim = pension_net_grossed_up *.2
elif higher_threshold < taxable_income:
    inc_tax = round(7540+19892+15084+((taxable_income - higher_threshold) * .45),2)
    if pension_type == 2:
        if taxable_income - pension_net_grossed_up <= higher_threshold:
            tax_relief_claim = (pension_net_grossed_up - (higher_threshold - (taxable_income - pension_net_grossed_up)))*.25 + (higher_threshold - (taxable_income - pension_net_grossed_up))*.2
        elif taxable_income - pension_net_grossed_up > higher_threshold:
            tax_relief_claim = pension_net_grossed_up *.25
############################################################################################################
#National Insurance calculation
salary_for_ni = salary - (salary_sacrifice * 12)
if lower_threshold < salary_for_ni <= secondary_threshold:
    national_insurance = round((salary_for_ni-lower_threshold) * .08,2)
elif secondary_threshold < salary_for_ni:
    national_insurance = round(3016 + ((salary_for_ni-secondary_threshold) * .02),2)
elif no_income <= salary_for_ni <= lower_threshold:
    national_insurance = 0
    
money_received = net_income - benefits - pension_net - inc_tax - national_insurance
money_received_monthly = round(money_received / 12,2)
pension = pension_net + pension_gross + (salary_sacrifice * 12)
pension_rate = pension / salary * 100
effective_tax_rate = (net_income - money_received + pension) / (net_income + pension) *100
employer_ni = (salary_for_ni - 5000) * 0.15
employer_costs = salary + employer_ni + employer_pension + benefits
employer_costs_pc = ((employer_costs / salary) -1) * 100

####################################################################################################
#Tax Report

st.header("**TAX REPORT**", divider=True)
st.header("1. Take-home pay", divider=True)
st.write("With an annual net income of £", net_income,", you would receive £", money_received_monthly," each month.")
st.write("The total you would receive for the year is £", money_received)

st.header("2. Tax paid", divider=True)
if tertiary_threshold < adjusted_net_income <= higher_threshold:
    print("\nYour Adjusted Net Income is £{:,.2f}".format(adjusted_net_income))
    print("(for more information about how this was calculated, see below)")
    print("As this is between £100,000 and £125,140, I'm afraid you're in the 60% trap!")
    print("This means that you lose £1 of your personal allowance for every £2 over £100,000")
    print("You could avoid this by increasing your pension contributions or giving more to charity.")
print("\nIncome Tax: £{:,.2f}".format(inc_tax)+"\nNational Insurance: £{:,.2f}".format(national_insurance))
print("\n{:.2f}".format(effective_tax_rate)+"% of your total income is paid in tax.")

st.header("3. Pension contributions", divider=True)
print("{:.2f}".format(pension_rate)+"% of your salary (£{:,.2f}".format(pension)+") has been put into your pension fund.")
print("Your employer has contributed a further £{:,.2f}".format(employer_pension))
print("Therefore, £{:,.2f}".format(pension_total),"will be put into your pension pot this year.")
if pension_total > 60000:
    print("\nHowever, only £60,000 can be contributed to your pension pot tax-free, so an additional £{:,.2f}".format(excess_pension),"was added to your taxable income and included in the calculations above.")
if secondary_threshold < taxable_income <= higher_threshold:
    if pension_type == 2:
        print("\nAs you paid pension contributions with 20% tax deducted, but should have had 40% deducted for some or all of it, you are eligible to claim some more tax relief.")
        if taxable_income - pension_net_grossed_up <= secondary_threshold:
            tax_relief_claim = (taxable_income + pension_net_grossed_up - secondary_threshold)*.2
        elif taxable_income - pension_net_grossed_up > secondary_threshold:
            tax_relief_claim = pension_net_grossed_up *.2
        print("You can claim £{:,.2f}".format(tax_relief_claim))
elif higher_threshold < taxable_income:
    inc_tax = round(7540+19892+15084+((taxable_income - higher_threshold) * .45),2)
    if pension_type == 2:
        print("\nAs you paid pension contributions with 20% tax deducted, but should have had 40 or 45% deducted for some or all of it, you are eligible to claim some more tax relief.")
        if taxable_income - pension_net_grossed_up <= higher_threshold:
            tax_relief_claim = (pension_net_grossed_up - (higher_threshold - (taxable_income - pension_net_grossed_up)))*.25 + (higher_threshold - (taxable_income - pension_net_grossed_up))*.2
        elif taxable_income - pension_net_grossed_up > higher_threshold:
            tax_relief_claim = pension_net_grossed_up *.25
        print("You can claim £{:,.2f}".format(tax_relief_claim))
st.header("4. Employer contributions", divider=True)
print("Pension contribution: £{:,.2f}".format(employer_pension))
print("National Insurance contribution: £{:,.2f}".format(employer_ni))
print("Employer benefits: £{:,.2f}".format(benefits))
print("\nTherefore, your employer has spent £{:,.2f}".format(employer_costs))
print("This is {:.2f}".format(employer_costs_pc)+"% more than your salary alone")

print("\nNB Your Adjusted Net Income takes into account pension contributions and charitable giving to achieve the following:")
print(" - if you earn just over £50,270, it preserves your £1000 Personal Savings Allowance")
print(" - if you earn between £100,000 and £125,140, it helps to preserve your Personal Tax Allowance of £12570")
print(" - if you earn between £60,000 and £80,000, it helps to maximise the amount of Child Benefit you can claim")
####################################################################################################
#Calculate Child Benefit
HICBC_lower_threshold = 60000
HICBC_upper_threshold = 80000

if adjusted_net_income > HICBC_upper_threshold:
    print("\nYou are not eligible for Child Benefit payments.")
    print("\nThank you for using this calculator!")

if adjusted_net_income <= HICBC_upper_threshold:
    while True: 
        query = input("\nYou are eligible for Child benefit payments if you have children. Do you wish to claim? (Y/N)")
        if query not in ("Y","y","N","n"):
            print("Please type Y or N")
            continue
        else:
            break
    if query in ("N","n"):
        print("\nThank you for using this calculator!")
    elif query in ("Y","y"):
        while True:
            children = int(input("\nHow many children do you have?\n"))
            if children not in (1,2,3,4,5):
                print("Please enter a number between 1 and 5")
                continue
            else:
                break
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
            print("You will also receive 13 payments of £{:.2f}".format(monthly_cb)+", which amounts to £{:.2f}".format(monthly_cb * 13),"per year.")
            print("\nThank you for using this calculator!")
        if HICBC_lower_threshold < adjusted_net_income <= HICBC_upper_threshold:
            HICBC = (adjusted_net_income - HICBC_lower_threshold) // 200
            child_benefit_repayment = (monthly_cb * 13) * HICBC / 100
            print("Although you will receive 13 payments of £{:.2f}".format(monthly_cb)+", which amounts to £{:.2f}".format(monthly_cb * 13),"per year, you will have to pay back {:.2f}".format(HICBC)+"% per year of your child benefit (£{:,.2f}".format(child_benefit_repayment)+"), leaving you with £{:.2f}".format((monthly_cb * 13) - child_benefit_repayment),"for the year or £{:.2f}".format(((monthly_cb * 13) - child_benefit_repayment)/13),"every 4 weeks.")
            print("\nThank you for using this calculator!")
    
    

        





