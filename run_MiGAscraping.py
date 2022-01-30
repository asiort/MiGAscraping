"""
Scrapes all the results of every genome analysis performed with MiGA (Microbial Genomes Atlas) Online 
web tool from your MiGA account and write them in a file.

@Dependencies Selenium and ChromeDrive  
@Author Asier Ortega Legarreta
@Date 2022/01/30
@email asierortega20@gmail.com
@github github.com/asiort
"""

import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException 
from myFunctions.functions import arguments, logging, surfing_web, write_dic, delete_dic, read_dic, write_output, test_path

def main():
    """
    We get the arguments
    """
    args, password = arguments()

    ## Selenium Driver path
    if args.driverpath:
        driver_path = args.driverpath
    else:
        driver_path = "/usr/bin/chromedriver" ## Default path

    """
    Information and paths
    """   
    username = args.username

    if args.out_path:
        out_path = args.out_path
    else:
        out_path = ""
    
    if args.pvalue:
        p_value = float(args.pvalue)
    else:
        p_value = 0.05 ## Default p_value

    if args.hide:
        hide = args.hide
    else:
        hide = "no"

    """
    Test outputh path
    """
    test_path(out_path)

    """
    Opening the browser and Log in
    """
    try:
        driver_options = Options()
        if hide == "yes":
            driver_options.add_argument("--headless")
        
        driver = webdriver.Chrome(driver_path, options=driver_options)
        driver.get('http://microbial-genomes.org/login') ## MiGA url
    
    except WebDriverException: ## Could not find the ChromeDriver
        print("\n\nYou must include the Google Chrome Driver path. \nMake sure that you have a compatible driver for your Google Chrome browser:  https://sites.google.com/a/chromium.org/chromedriver/home")
        sys.exit()

    driver = logging(driver, username, password)

    """
    Moving to the menu
    """
    driver.find_element(By.XPATH, '//*[@id="logo"]').click()    
    driver.find_element(By.XPATH,'/html/body/div/div[2]/div[1]/div/div/a[2]').click()
    driver.find_element(By.XPATH, '/html/body/div/div[1]/aside/section[2]/ul/li[4]/a').click()

    """
    Moving into every uploaded genome
    """
    list_low_quality = [] ## List to store the genomes with low quality
    del_genome = [] ## List to store the genomes whisch closest genome have been deleted from the database and recalculate distance analysis required (manually)
    result_dic = {} ## Dictionary with all the successfully classified genomes

    """
    We calculate how many pages are taking into account the total amount of genomes and every page display 10 of them
    """
    n_genomes_page = 10
    tot_gen = driver.find_element(By.XPATH, '/html/body/div/div[1]/aside/section[2]/ul/li[4]/a/span').text
    n_pages = (int(tot_gen) // n_genomes_page) + 1
    n_gen_last_page = int(tot_gen) % n_genomes_page

    """
    Scrapping every page from the loaded genomes
    """
    for page in range(n_pages):
        print("\nPAGE:", str(page+1))
        if page == (n_pages-1): ## if it is last page
            n_genomes_page = n_gen_last_page
            driver, result_dic, list_low_quality, del_genome = surfing_web(driver, result_dic, p_value, list_low_quality, n_genomes_page, del_genome)
            n_genomes_page = 1
            driver, result_dic, list_low_quality, del_genome = surfing_web(driver, result_dic, p_value, list_low_quality, n_genomes_page, del_genome)

        else: 
            try:
                driver, result_dic, list_low_quality, del_genome = surfing_web(driver, result_dic, p_value, list_low_quality, n_genomes_page, del_genome)
            
            except NoSuchElementException:
                driver, result_dic, list_low_quality, del_genome = surfing_web(driver, result_dic, p_value, list_low_quality, n_genomes_page, del_genome)

            """
            Depending on the page and the remaining pages the XPATH of the 'NEXT button' changes.
            The XPATH of the button to past the next page ("NEXT") change depending on the remaining 
            number of pages and the actual page where the browser is. 
            """
            if n_pages >= 12:
                if page in [0, 1, 2, 3, 4, n_pages-5, n_pages-4, n_pages-3, n_pages-2, n_pages-1]:
                    driver.find_element(By.XPATH,'/html/body/div/div[1]/div/div[2]/ul/li[14]/a').click()
                elif page == 5:
                    driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/ul/li[15]/a').click()
                elif page == 6:
                    driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/ul/li[16]/a').click()
                elif page == (n_pages-7):
                    driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/ul/li[16]/a').click()
                elif page == (n_pages-6):
                    driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/ul/li[15]/a').click()
                else:
                    driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/ul/li[17]/a').click()
            else:
                driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/ul/li['+str(n_pages+2)+']/a').click()


    write_dic(out_path, result_dic) ## Every page write results

    """
    Closing the driver
    """
    driver.quit()

    """
    Write the final dictionary in a json file and read it.
    In order to do not repeat the analysis once you run successfully the script.
    """
    write_dic(out_path, result_dic)

    result_dic = read_dic(out_path)

    """
    Writing the final csv output.
    """
    write_output(out_path, result_dic, list_low_quality, p_value)

    """
    Delete previously created dictionary. 
    """
    try:
        delete_dic(out_path)
    
    except:
        pass

    print("\n ---Finished---") 
    

if __name__ == "__main__":
    main()