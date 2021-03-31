from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import pandas as pd
import numpy as np
import csv
import os

app = Flask(__name__)

def fun():
    # datetime object containing current date and time
    now = datetime.now()
    print("now =", now)

    print('I am Here IN FUN')
    mc_url = "https://www.moneycontrol.com/stocks/marketstats/nse-mostactive-stocks/nifty-500-7/"
    mc_data = urlopen(mc_url)
    mc_html = mc_data.read()

    # Parsing the Data
    mc_soup = soup(mc_html, 'html.parser')
    print('parsed')
    # Start Extracting the data
    headers = mc_soup.findAll('th')

    column_titles = [ct.text for ct in headers]
    column_titles = column_titles[:6]
    # column_titles[6] = column_titles[6][0:17]
    ## Upto Done with Headers

    # List out the all company name
    span = mc_soup.find_all('span', class_='gld13')
    company_span_list = [spani.text[:-37] for spani in span]

    with open('static/mc_NIFTY_500_company.csv', 'w', encoding='utf-8', newline='') as f:
        company_name = '\n'.join(company_span_list)
        f.write(company_name)
        f.close()
    print('company done')    
    ## Upto Company_name list Done here
    ## Now It's time for Valuable Digits
    # First of all we extract the elements which is not neccessory for final data

    ##### Removing the tags
    # Remove p elements
    tdrs = mc_soup.find_all('p')
    for re in tdrs:
        re.decompose()
    # Remove strongs elements
    tdrst = mc_soup.find_all('strong')
    for re in tdrs:
        re.decompose()
    tws = mc_soup.find_all('div', {'class': 'title2'})
    for re in tws:
        re.decompose()
    tws = mc_soup.find_all('td', {'class': 'vol'})
    for re in tws:
        re.decompose()
    tws = mc_soup.find_all('td', {'class': 'del'})
    for re in tws:
        re.decompose()
    twsas = mc_soup.find_all('td', {'width': '300'})
    for re in twsas:
        re.decompose()

    # final Digits
    ## td_data is Our final Valuable Data
    td_data = mc_soup.find_all('td', {'align': 'right'})

    # Final digit List
    ## Little bit of data cleansing :)
    digit_list = []
    for tt in td_data[0:2505]:
        x = tt.text
        x = x.replace(",", "")
        digit_list.append(x)

    ############################## Done with This

    # data setup in CSV
    with open('static/mc_NIFTY_digits.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        #      writer.writerow(column_titles[1:])
        for i in range(0, 2505, 5):
            writer.writerow([digit_list[i], digit_list[i + 1], digit_list[i + 2], digit_list[i + 3], digit_list[i + 4]])
        f.close()
    print('digits done')
    ############33 All done with CSV Table partition

    # Clear entire csv file
    with open('static/final_mc_NIFTY_list.csv', 'w+', encoding='utf-8') as f:
        f.truncate()
        f.close

    with open('static/mc_NIFTY_digits.csv', 'r', encoding='utf-8') as read_temp, open('static/mc_NIFTY_500_company.csv', 'r',encoding='utf-8') as header, open(
            'static/final_mc_NIFTY_list.csv', 'a', encoding='utf-8', newline='') as final_list:
        reader = csv.reader(read_temp)
        writer = csv.reader(header)
        final_obj = csv.writer(final_list)

        final_obj.writerow(column_titles)  # Put Headings on top of list
        for a, b in zip(writer, reader):
            final_obj.writerow(a + b)  # write 50 rows (Company_name+ value)
        read_temp.close()
        header.close()
        final_list.close()

    print('final list done')
    
    ## Generate Excel file
    csv_list = pd.read_csv('static/final_mc_NIFTY_list.csv')

    NIFTY_500_sheet = pd.ExcelWriter('static/NIFTY_500_sheet.xlsx')
    csv_list.to_excel(NIFTY_500_sheet, index=False)
    NIFTY_500_sheet.save()

    ### Now remove the unnnecessory CSV files
    # os.remove('static/mc_NIFTY_500_company.csv')
    # os.remove('static/mc_NIFTY_digits.csv')

    print('SpreadSheet is Ready for U!')


@app.route('/')
def home():
    fun()
    return render_template('index.html')

# @app.route('/')
# def home():
#     print('web page 2 load')
#     return render_template('2.html')    

# fun()        


if __name__ == '__main__':
    app.run()