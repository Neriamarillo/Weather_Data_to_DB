from selenium import webdriver
import pandas as pd

chrome_driver_path = "/Users/neriamarillo/Documents/Development/Python/chromedriver"
driver = webdriver.Chrome(executable_path=chrome_driver_path)
driver.get('https://www.latlong.net/category/states-236-14.html')

us_states_geo_locations = {
    'State': [],
    'Lat': [],
    'Lon': []
}


def fetch_states():
    # state = driver.find_element_by_css_selector("a title")
    for index in range(2, 52):
        state = driver.find_element_by_xpath("/html/body/main/table/tbody/tr[{}]/td[1]".format(index))
        lat = driver.find_element_by_xpath("/html/body/main/table/tbody/tr[{}]/td[2]".format(index))
        lon = driver.find_element_by_xpath("/html/body/main/table/tbody/tr[{}]/td[3]".format(index))

        us_states_geo_locations['State'].append(state.text.split(',')[0])
        us_states_geo_locations['Lat'].append(lat.text)
        us_states_geo_locations['Lon'].append(lon.text)

    pd.DataFrame(us_states_geo_locations).to_csv('US_States.csv', index=False)

    driver.close()
