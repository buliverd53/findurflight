import time
import json
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
from chromedrive import get_driver
from mongo_client import get_client

site = 'edestinos' 
flt_od = 'CGHSDU'
flt_date  = str(date.today() + timedelta(days=int(14)))
edestinos = f'https://www.edestinos.com.br/flights/select/oneway/ap/{flt_od[:3].lower()}/ap/{flt_od[-3:].lower()}?departureDate={flt_date}&pa=1&py=0&pc=0&pi=0&sc=economy'

def run_edestinos(driver):
    try:
        for a in range(4):
            if a == 0: driver.maximize_window()
            driver.execute_script("window.scrollTo(0, 120000)")
            time.sleep(0.1)
            driver.execute_script("window.scrollTo(0, 0)")

        for i in range(60):
            time.sleep(0.1)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            progress_bar = soup.find_all('div',{'class':'header-element ng-star-inserted'})
            if len(progress_bar)==0:
                break

        show_flt_source = driver.find_elements_by_xpath("//span[@class='btn function ghost ng-star-inserted']")
        for flt_source in show_flt_source:
            flt_source.click()
    except Exception as e:
        pass
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    containers = soup.findAll("esky-flight-offer-group")
    for count_cont,container in enumerate(containers):
        fare_raw = container.find("span", {"class":"amount ng-star-inserted"})
        stops_raw = container.find("span", {"class":"connecting-info"})
        cia_raw = container.find("div", {"class":"logo-container ng-star-inserted"})
        dep_times_raw = container.findAll("span", {"class":"hour departure ng-star-inserted"})
        arv_times_raw = container.findAll("span", {"class":"hour arrival ng-star-inserted"})
        bags_raw = container.findAll("div", {"class":"leg-facilities"})

        for count_dep,dep_time_raw in enumerate(dep_times_raw):
            cia = cia_raw.find("img-fallback", {"size":"small"}).img["alt"].replace(" Airlines ","").replace("GOL","Gol")
            dep_time = (dep_time_raw.get_text()).strip()
            arv_time = (dep_time_raw.get_text()).strip()
            fare = str(fare_raw.get_text()).strip().replace(".","")
            stops = (stops_raw.get_text()).strip()

            if stops == 'voo direto':
                stops = 'Direto'
            bag_len = int(len(bags_raw[0].findAll("i")))
            bag_finds = bags_raw[0].findAll("i")

            for count_bag,bag_find in enumerate(bag_finds):
                bag = bag_finds[bag_len-1]['class']
                if (len(bag)) == 4:
                    bag = "Sem bagagem"
                else:
                    bag = "Com bagagem"

            save_on_mongo(
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
                    'crawlertime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    'bag': bags
                }
            )

    print("Voos cadastrados no sistema!")


def main():
    driver = get_driver()
    driver.get(edestinos)
    driver.maximize_window()
    attempts = 0
    while attempts < 10 :
        try:
            driver.find_elements_by_class_name("hour departure ng-star-inserted")
            run_edestinos(driver)
            break
        except Exception as e:
            attempts += 1
            time.sleep(0.5)

    if attempts == 10: 
        print('nothing done, good bye!')
    else:
        print('everything done, good bye!')
        driver.close()


if __name__ == "__main__":
    main()