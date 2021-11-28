

import time
import json
from datetime import date,timedelta,datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from mongo_client import get_client

site = 'passagenspromo' 
flt_od = 'CGHSDU' #origem_destino
flt_date_date  = date.today() + timedelta(days=int(14)) #Dias de Antecedencia do voo / data_ida
flt_date = str(flt_date_date)

passagenspromo = f"https://www.passagenspromo.com.br/air/search/{flt_od.upper()}{flt_date_date.strftime('%y%m%d')}/1/0/0/Y/"

def save_on_mongo(flight_json):
    try:
        for flight in flight_json['flights']:
            mongo_client = get_client()
            flights_collection = mongo_client.flights
            flights_collection.insert_one(flight)
    except Exception as e:
        print(e)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(chrome_options=options, executable_path="chromedriver")

    return driver
    
def run_passagenspromo(driver):

    for loading in range(60):
        time.sleep(0.1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        progress_bar = soup.find_all('div',{'class':'searchloadingbar'})
        if len(progress_bar)==0:
            break

    for more_fts in range(5):
        try:
            show_more_flts = driver.find_element_by_xpath("//button[@class='moreresultsbutton']")
            show_more_flts.click()
        except Exception as e:
            print(e)
            pass

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    containers = soup.findAll("div", {"class":"flightcard"})
    for container in containers:
        cia_raw = container.find("div", {"class":"logo_cia"})
        bag_allowance_find = container.find("div", {"class":"luggage_option"})
        fare_raw = container.find("span", {"class":"value_passenger"})
        dep_hours_raw = container.findAll("div", {"class":"depart_hour"})
        arv_hour_raw = container.findAll("div", {"class":"arrive_hour"})
        stops_raw = container.findAll(class_="text_conex")
        bag_raw = bag_allowance_find.img["src"][39:]
        
        for count,dep_hour in enumerate(dep_hours_raw):
            cia = (cia_raw.get_text()).strip()
            fare = ((fare_raw.get_text()).strip()).replace("R$ ","").replace(".","")
            dep_time = (dep_hour.get_text()).strip()
            arv_time = (arv_hour_raw[count].get_text()).strip()
            stops = (stops_raw[count].get_text()).strip()
            if ((bag_raw).strip()) == 'rey.svg':
                bag = "Sem bagagem"
            elif ((bag_raw).strip()) == 'vg':
                bag = "Com bagagem"
            
            print(cia,' ',flt_od,' ',flt_date,' ',dep_time,' ',arv_time,' ',stops,' ',fare,' ',site,' ',bag,' ',datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            save_on_mongo({
                'cia': cia,
                'origin': flt_od[:3],
                'destiny': flt_od[3:],
                'flight_date': flt_date,
                'departure_time': dep_time,
                'arrive_time': arv_time,
                'stop_by': stops,
                'price': fare #,
                #'site': 'decolar'
                #'crawlertime':  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                #'bag': bags
            })
        
    print("Voos cadastrados no sistema!")

def main():
    driver = get_driver()
    driver.get(passagenspromo)
    driver.maximize_window()
    attempts = 0
    while attempts < 10 :
        try:
            driver.find_elements_by_class_name("value_passenger")
            run_passagenspromo(driver)
            break
        except Exception as e:
            attempts += 1
            time.sleep(0.5)
            print(attempts,' ',e)

    if attempts == 10: 
        print('nothing done, good bye!')
    else:
        print('everything done, good bye!')
        driver.close()

if __name__ == "__main__":
    main()

