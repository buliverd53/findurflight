import time
import json
from datetime import date, timedelta
from bs4 import BeautifulSoup
from chromedrive import get_driver
from mongo_client import save_data, get_data

site = 'zupper'
flt_od = 'VCPCNF' #origem_destino
flt_date  = str(date.today() + timedelta(days=int(14))) #Dias de Antecedencia do voo / data_ida
website_to_scraper = f'https://www.zupper.com.br/resultados?type=oneWay&adultQty=1&childrenQty=0&infantQty=0&slices=%5B%7B%22originAirport%22:%22{flt_od[:3]}%22,%22departureDate%22:%22{flt_date}%22,%22destinationAirport%22:%22{flt_od[3:]}%22%7D%5D'

def run_zupper(driver):
    for a in range(4):
        driver.execute_script("window.scrollTo(0, 120000)")
        time.sleep(0.1)
    driver.execute_script("window.scrollTo(0, 0)")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    contaniers = soup.findAll("section",{"class":"list-container"})

    for count,container in enumerate(contaniers):
        inner_containers = contaniers[count].findAll("label",{"class","flight-option"})
        for d in range(int(len(inner_containers)/2)):
            cia_raw = contaniers[count].findAll("img",{"class":"airline-logo"})
            cia = cia_raw[0].get('src')[38:40].replace("AD","Azul").replace("G3","Gol").replace("LA","LATAM")
            dep_time = inner_containers[d].find("div",{"class":"departure-wrapper"}).get_text().replace("Saída","")
            arv_time = inner_containers[d].find("div",{"class":"arrival-wrapper"}).get_text().replace("Chegada","")[1:6]
            stops = inner_containers[d].find("div",{"class":"stops-wrapper"}).get_text().replace("Voo Direto","Direto")
            fare = contaniers[count].find("div",{"class":"price-info"}).findAll("p")[0].get_text().replace("Tarifa por Adulto R$","").replace(".","").replace(",",".").replace(u'\xa0', u' ')

            save_data(
                site,
                {
                    'cia': cia,
                    'origin': flt_od[:3],
                    'destiny': flt_od[3:],
                    'flight_date': flt_date,
                    'departure_time': dep_time,
                    'arrive_time': arv_time,
                    'stop_by': stops,
                    'price': fare,
                    'site': site,
                    'crawlertime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'bag': bags
                }
            )

    print("Voos cadastrados no sistema!")

def get_flights():
    data = get_data(site)
    return { site: data }

def main():
    driver = get_driver()
    driver.get(website_to_scraper)
    driver.maximize_window()
    attempts = 0
    while attempts < 10 :
        try:
            driver.find_element_by_class_name("list-container")
            run_zupper(driver)
            break
        except:
            attempts += 1
            time.sleep(0.5)

    if attempts == 10: 
        print('nothing done, good bye!')
    else:
        print('everything done, good bye!')
        driver.close()

if __name__ =='__main__':
    main()
