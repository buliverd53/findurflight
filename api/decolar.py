
import time
import json
from datetime import date,timedelta,datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# from mongo_client import get_client

site = 'decolar' 
flt_od = 'VCPCNF' #origem_destino
flt_date  = str(date.today() + timedelta(days=int(14))) #Dias de Antecedencia do voo / data_ida

decolar = 'https://www.decolar.com/shop/flights/results/oneway/'+ flt_od[:3].upper()+'/'+flt_od[-3:].upper()+'/'+flt_date+'/1/0/0/NA/NA/NA/NA/?from=SB&di=1-0'

# def save_on_mongo(flight_json):
#     try:
#         for flight in flight_json['flights']:
#             mongo_client = get_client()
#             flights_collection = mongo_client.flights
#             flights_collection.insert_one(flight)
#     except Exception as e:
#         print(e)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(chrome_options=options, executable_path="/Users/Luiz Eduardo/Documents/Python/chromedriver")

    return driver

def run_decolar(driver):
    for a in range(4):
        driver.execute_script("window.scrollTo(0, 120000)")
        time.sleep(0.1)
        driver.execute_script("window.scrollTo(0, 0)")

    try:                                           
        more_flights = driver.find_elements_by_xpath("//button[@class='eva-3-btn -md -link button-show-itineraries']")
        for i,show in enumerate(more_flights):
            more_flights[i].click()
            break
    except:
        pass

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    containers = soup.findAll("div", {"class": "cluster-container COMMON"})
    for c in range(len(containers)):
        cia_raw = containers[c].find("span", {"class": "name"})
        dep_time_raw = containers[c].findAll("itinerary-element", {"class": "leave"})
        arv_time_raw = containers[c].findAll("itinerary-element", {"class": "arrive"})
        stops_raw = containers[c].findAll("span", {"data-sfa-id":"stops-text"})
        bags_raw = containers[c].findAll("span", {"class":"baggages-icons"})[0]
        bags = (bags_raw.select('span[class*="bag-image baggage-icon"]')[1])['class'][2]
        fare_raw = containers[c].find("span", {"class":"fare main-fare-big"}).get_text()
        for d in range(len(dep_time_raw)):
            cia = cia_raw.get_text().replace(" ", "")
            fare = fare_raw[2:].replace(".","")
            dep_time = dep_time_raw[d].get_text()
            arv_time = (arv_time_raw[d].get_text())[:5]
            stops = stops_raw[d].get_text().strip()
            if (bags) == 'NOT-INCLUDED':
                bags = "Sem bagagem"
            elif (bags) == '-INCLUDED':
                bags = "Com bagagem"

            print(cia,' ',flt_od,' ',flt_date,' ',dep_time,' ',arv_time,' ',stops,' ',fare,' ',site,' ',bags,' ',datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            # save_on_mongo({
            #     'cia': cia,
            #     'origin': flt_od[:3],
            #     'destiny': flt_od[3:],
            #     'flight_date': flt_date,
            #     'departure_time': dep_time,
            #     'arrive_time': arv_time,
            #     'stop_by': stops,
            #     'price': fare #,
            #     #'site': 'decolar'
            #     #'crawlertime':  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #     #'bag': bags
            # })
            
    print("Voos cadastrados no sistema!")


def main():
    driver = get_driver()
    driver.get(decolar)
    driver.maximize_window()
    attempts = 0
    while attempts < 10 :
        try:
            driver.find_element_by_class_name("main-fare-big")
            run_decolar(driver)
            break
        except:
            attempts += 1
            time.sleep(0.5)
            print(attempts)

    if attempts == 10: 
        print('nothing done, good bye!')
    else:
        print('everything done, good bye!')
        driver.close()

if __name__ == "__main__":
    main()