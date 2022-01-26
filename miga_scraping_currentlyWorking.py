"""
Este script entra en la herramienta MiGA online y extrae la información. 
"""
#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import argparse
import os
import sys

import json

def arguments():
    """
    Obtain the required arguments. 

    Returns
    -------
    args 
    """
    parser = argparse.ArgumentParser(description = "Automatic NCBI BLAST searches from a multiFASTA file. \
                             MultiFASTA can contain either nucleotide sequence or protein sequence. \
                            ./multiBLAST.py -p <driver-path> -d <in-path> -t <int> -o <out-path> -f nucletotide|protein \
                             Example of bash execution: \
                             ./multiBLAST.py -p driverpath/chromedriver -d myFastas/multiFasta.fa -t 4 -o myResults.txt -f nucletotide")
    parser.add_argument('-p', '--driverpath', dest='driverpath', 
                           action = 'store', required=False , 
                           help='The ChromeDriver path (Optional) Default path: chromedriver/chromedriver.')
    parser.add_argument('-d', '--dir', dest='in_file', 
                           action = 'store', required=True , 
                           help='MultiFASTA file.')
    parser.add_argument('-o', '--outpath', dest='out_path',
                       action = 'store', required=True,
                       help = 'Output path')
    parser.add_argument('-v', '--pvalue', dest='pvalue',
                       action = 'store', required=False,
                       help = 'The p_value that will use to asses the taxonomy. Default p_value = 0.05.')
    parser.add_argument('-us', '--username', dest='username',
                       action = 'store', required=False,
                       help = 'The username of the MiGA Online personal account. Needed for the logging')
    parser.add_argument('-pw', '--passsword', dest='password',
                       action = 'store', required=False,
                       help = 'The password of the MiGA Online personal account. Needed for the loggin.')
    parser.add_argument('-lg', '--logging_file', dest='logging_file',
                       action = 'store', required=False,
                       help = 'The file with the username and password of the MiGA Online personal account. Needed for the loggin.')

    try:
        args = parser.parse_args()

        return args

    except:
        print("\nPlease, include the required arguments!")
        sys.exit()


def logging(driver, username, password):
    """
    Log in function
    """

    login = driver.find_element(By.NAME, "commit")
    username_driver = driver.find_element(By.XPATH, '//*[@id="session_email"]')
    password_driver = driver.find_element(By.XPATH, '//*[@id="session_password"]')

    username_driver.send_keys(username)
    password_driver.send_keys(password)
    login.click()
    driver.implicitly_wait(5)

    return driver


def surfing_web(driver, result_dic, p_value, list_low_quality, n_genomes_page, del_genome):
    """
    This function goes into every genome result.
    """

    timeout = 10
    for i in range(n_genomes_page):
        xpath_gen = '/html/body/div/div[1]/div/ol/li['+str(i+1)+']/div/span[1]/b/a' ## Go into every of the genomes

        """
        Go into each genome classification
        """
        driver.find_element(By.XPATH, xpath_gen).click()
        gen_name = driver.find_element(By.XPATH, '/html/body/div/div[1]/aside/section[1]/div/span[1]/b/a').text ## The genome name, will be the key in the dictionary
        gen_name = gen_name.replace(" ", "_")

        ## We add the arguments for EC.presence_of_element_located as a tupla
        element_present = EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/aside/section[2]/div/div/div[1]/div[1]/h4/a'))
        ## Wait until the following element appeare
        WebDriverWait(driver, timeout).until(element_present)

        ## Before scraping the results we make sure that the genome have been successfully classified
        if driver.find_element(By.XPATH, '/html/body/div/div[1]/aside/section[2]/div/div/div[1]/div[1]/h4/a').text == 'Taxonomy':
            if driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/h4[1]').text == "Taxonomic classification": ## Sometimes happend that the closest genome have been deleted from the database
                result_dic[gen_name] = []
                result_dic = scrap(driver, result_dic, gen_name)
                res_rank = assess_novelty(result_dic[gen_name], p_value)
                result_dic[gen_name].append(res_rank)

            else:
                print("##\tWARNING! Check the following genome -----------> " + gen_name)
                del_genome.append(gen_name) 

        else:
            print("-> Low quality genome -----------> " + gen_name)
            list_low_quality.append(gen_name) 

        driver.execute_script("window.history.go(-1)") ## To go back (to the previous page)

    return driver, result_dic, list_low_quality, del_genome


def scrap(driver, result_dic, gen_name):
    timeout = 5
    print("-> Processing", gen_name)


    ## Sometimes appear an alert about the database have been uploaded, in order to deal with the alert we need to change the XPATH:
    if "database" in driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div[1]').text: ## The alert div XPath.
        div_number = 2

    else:
        div_number = 1

    """
    Taxonomic classification
    """
    try:
        domain = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div/div/b/i/a').text
    except:
        domain = "NA"
    try:
        phylum = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div/div/div/b/span[2]/a').text
    except:
        phylum = "NA"
    try:
        clas = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div/div/div/div/b/i/a').text
    except:
        clas = "NA"
    try:
        order = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div/div/div/div/div/b/i/a').text
    except:
        order = "NA"
    try:
        family = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div/div/div/div/div/div/b/i/a').text
    except:
        family = "NA"
    try:
        genus = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div/div/div/div/div/div/div/b/i/a').text
    except:
        genus = "NA"
    try:
        specie = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div/div/div/div/div/div/div/div/b/i/a').text
    except:
        specie = "NA"

    ## Few times there is no information about one taxonomic level, we substitute it with NA
    result_dic[gen_name].append([domain, phylum, clas, order, family, genus, specie])
    result_dic[gen_name].append([])
    
    try:
        for j in range(7):
                xpath_p = '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div/div'+str('/div'*j)+'/b'
                p_val = driver.find_element(By.XPATH, xpath_p)
                result_dic[gen_name][1].append(p_val.text.split("p-value ")[1].split("*")[0])

    except NoSuchElementException: ## When the closest genome have been deleted or changed from the database
        print("##\tWARNING! Check the following genome -----------> " + gen_name)
        result_dic[gen_name][-1] = [1, 1, 1, 1, 1, 1, 1] ## In order to have a p-value of 1.

    """
    Obtain clossest genome ANI/AAI
    """
    try: ## If there is a problem with the genome to keep running the program
        if "ANI" in driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/p[1]').text:
            ## Obtain AAI value
            if "database was updated" in driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div[1]').text:
                div_number = 4
            else:
                div_number = 3

            driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div[2]/div[1]/h4/a').click()
            
            element_present = EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div[2]/div[2]/div/table/tbody/tr[1]'))
            WebDriverWait(driver, timeout).until(element_present)        
            
            try:
                AAI_value = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/div['+str(div_number)+']/div[2]/div[2]/div/table/tbody/tr[1]/td[2]/span').text

            except NoSuchElementException:
                pass       
    
            ## Obtain ANI value from summary (easier to scrap)
            full_text = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/p[1]').text
            ANI_value = full_text.split("(")[1].split("%")[0]
            ## Obtain the closest genome depending on two other one results appear
            if "was" in full_text:
                closest_gen = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/p[1]/a/span').text

            else:
                closest_gen = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/p[1]/a[1]/span').text
            closest_gen = closest_gen.replace(" ", "_")

        else:
            ## Obtain AAI value from summary
            full_text = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/p[1]').text     
            AAI_value = full_text.split("(")[1].split("%")[0]
            ## Obtain the closest genome depending on two other one results appear
            if "was" in full_text:
                closest_gen = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/p[1]/a/span').text

            else:
                closest_gen = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[2]/div[1]/div[1]/p[1]/a[1]/span').text
            closest_gen = closest_gen.replace(" ", "_")

            ## In this case there is no ANI value
            ANI_value = "NA"


        try: ## conditional in case it enters in the recursive function
            float(AAI_value) ## Check it takes the AAI value, sometime it does not do it correcctly
            result_dic[gen_name].append(closest_gen)
            result_dic[gen_name].append(AAI_value)
            result_dic[gen_name].append(ANI_value)
            print(closest_gen, AAI_value, ANI_value)

        except UnboundLocalError:
            result_dic[gen_name] = [] ## Reset
            scrap(driver, result_dic, gen_name) 

        except ValueError: 
            result_dic[gen_name] = [] ## Reset
            scrap(driver, result_dic, gen_name) 
    
    except NoSuchElementException:
        AAI_value = "NA"
        ANI_value = "NA"
        closest_gen = "NA"
        result_dic[gen_name].append(closest_gen)
        result_dic[gen_name].append(AAI_value)
        result_dic[gen_name].append(ANI_value)


    return result_dic


def assess_novelty(res_list, p_value):
    """
    Check if the p_value is lesser than the established p_values
    """

    if len(res_list[1]) == 0:
        res_rank = "NA"

    else:
        res_rank = ""
        
        for n in range(len(res_list[1])):
            try:
                value = float(res_list[1][n])
            except ValueError:
                value = float(res_list[1][n][:-1])

            if value <= p_value:
                res_rank += res_list[0][n]+";"
            else:   
                res_rank = res_rank[:-1]
                break
        
        if res_rank[-1] == ";":
            res_rank = res_rank[:-1]

    return res_rank


def write_dic(out_path, result_dic):
    """
    Write the final dictionary with the scraping results in a file 
    """
    file_out = open(out_path+"/scraping_dic_tmp.json", "w")
    json.dump(result_dic, file_out)
    file_out.close()


def read_dic(out_path):
    """
    Read the final dictionary wrote previously
    """
    # file_in = open(out_path+"/scraping_dic.json", "r")
    # result_dic = file_in.read()
    with open(out_path+"/scraping_dic_tmp.json") as json_file:
        result_dic = json.load(json_file)

    return result_dic


def write_output(out_path, result_dic, list_low_quality):
    """
    Write the results obtained with MIGA in a csv
    """
    dic_sample = {} ## Results of each sample
    fich_out = open(out_path+"/MIGA_results_output.csv", "w")
    ## Write the header
    fich_out.write("ID \t Taxonomy novelty (p-value < 0.05) \t Taxonomy classification \t MiGA result closest specie (p-value) \t Closest genome \t AAI(%) \t ANI(%) \n")
    for id in result_dic.keys():
        tax_classification = ""
        for i in result_dic[id][0]:
            tax_classification += i+";"
        tax_classification = tax_classification[:-1]
        name = id
        tax_novelty = result_dic[id][5]
        p_value_closest_specie = str(result_dic[id][1][6])
        if p_value_closest_specie[-1] == ")":
            p_value_closest_specie = p_value_closest_specie[:-1]
        closest_genome = result_dic[id][2]
        AAI = result_dic[id][3]
        ANI = result_dic[id][4]
        fich_out.write(name+"\t"+tax_novelty+"\t"+tax_classification+"\t"+p_value_closest_specie+"\t"+closest_genome+"\t"+AAI+"\t"+ANI + "\n")

        sample = id.split("_bin_")[0]
        if sample not in dic_sample.keys():
            dic_sample[sample] = []
        dic_sample[sample].append(str(name+"\t"+tax_novelty+"\t"+tax_classification+"\t"+p_value_closest_specie+"\t"+closest_genome+"\t"+AAI+"\t"+ANI))
        write_sample_output(out_path, dic_sample)
    
    for i in list_low_quality:
        fich_out.write(i+"\tNA\tNA\tNA\tNA\tNA\tNA+\n")

    fich_out.close()


def write_sample_output(out_path, dic_sample):
    if "results" not in os.listdir(out_path):
        os.system("mkdir "+out_path+"/results")
    
    for id in dic_sample.keys():
        fich_out = open(out_path+"/results/"+id+".csv", "w")
        fich_out.write("ID \t Taxonomy novelty (p-value < 0.05) \t Taxonomy classification \t MiGA result closest specie (p-value) \t Closest genome \t AAI(%) \t ANI(%) \n")
        for linea in dic_sample[id]:
            fich_out.write(linea+"\n")

    fich_out.close()

def main():
    """
    Openning the browser (must have selenium driver according to your chrome version)
    """
    # os.environ['PATH'] += r"C:/SeleniumDrivers"
    # driver = webdriver.Chrome()
    # driver.get('http://microbial-genomes.org/login')

    driver_path = "/usr/bin/chromedriver"
    driver = webdriver.Chrome(driver_path)
    driver.get('http://microbial-genomes.org/login')

    """
    Information and paths
    """   
    username = "aortega"
    password = "margulis"
    out_path = "/home/asier/Escritorio"
    p_value = 0.05

    """
    Log in
    """

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
    RESULT DIC STRUCTURE:
    - KEY: genome name
    - VALUE: [[Taxonomic classification], [p-values of taxonomic classification], clossest relative genome, AAI value, ANI value, taxomic novelty (str)]
    """
    
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
        print("PAGE:", str(page+1))
        if page == (n_pages-1): ## if it is last page
            n_genomes_page = n_gen_last_page
            driver, result_dic, list_low_quality, del_genome = surfing_web(driver, result_dic, p_value, list_low_quality, n_genomes_page, del_genome)
            n_genomes_page = 1
            driver, result_dic, list_low_quality, del_genome = surfing_web(driver, result_dic, p_value, list_low_quality, n_genomes_page, del_genome)

        else: 
            driver, result_dic, list_low_quality, del_genome = surfing_web(driver, result_dic, p_value, list_low_quality, n_genomes_page, del_genome)

            """
            Depending on the page and the remaining pages the XPATH of the 'NEXT button' changes.
            The XPATH of the button to past the next page ("NEXT") change depending on the remaining number of pages and the actual page where the browser is. 
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
    Write the final dictionary in a json file and read it
    In order to do not repeat the analysis once you run successfully the script
    """
    write_dic(out_path, result_dic)
    write_output(out_path, result_dic, list_low_quality)
    print(del_genome)
    ###########AÑADIR LO DE QUE ESCRIBA OUTPUT DE LOS BIN QUE NO SE HAN PODIDO COMPLETAR
    result_dic = read_dic(out_path)
    fich_out_low = open(out_path+"/low_quality.txt", "w")
    for i in list_low_quality:
        fich_out_low.write(i+"\n")

    """
    Writing the final csv output
    """
    write_output(out_path, result_dic, list_low_quality)
    print(del_genome)
    """
    CLOSING THE DRIVER
    """
    driver.quit()

    print("\n ---Finished---") 
    
if __name__ == "__main__":
    main()
