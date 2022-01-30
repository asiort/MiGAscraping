# MiGAscraping
Scrapes all the results of every genome analysis performed with MiGA (Microbial Genomes Atlas) Online web tool from your MiGA account and write them in a file. [MiGA Online](http://microbial-genomes.org).

- You must have a MiGA account where you uploaded your genomes.
- Works using Selenium and ChromeDriver. 

## Requeriments:
 - Python Installed (Recommended version 3.8 or above)
 - [MiGA account](http://microbial-genomes.org/signup). 
 - Selenium library (use `pip install selenium`)
 - Driver for launching the automation (chromedriver)
   - Be sure to match the version of Chrome you have
   - [Download URL](https://sites.google.com/chromium.org/driver/downloads?authuser=0)
  
 ## Script options:
```bash
python3 run_MiGAscraping.py -d <driver-path> -o <out-path-dir> -p <float> -u <username 'email'> -hi <hide_Option:'yes'or'no'>
```

- `-d --driverpath DRIVERPATH`
  - The ChromeDriver path (Optional). Default path: usr/bin/chromedrive.
- `-o --outdir OUTPUTDIRECTORY`
  - Output directory (Optional). Default path: current directory.
- `-p --pvalue PVALUE`
  - p_value to asses the genome taxonomy (Optional). Default value: 0.05.
- `-u --username USERNAME`
  - Username of the MiGA Online account.
- `-hi --hide HIDEOPTION`
  - Hide the browser. Options: 'yes' or 'no'. Default option: 'no'. 

Once you execute the script you will be asked to introduce the password of MiGA Online account. 
 
Example of bash execution:
```bash
python3 onlineMultiBLASTqueries.py -p driverpath/chromedriver -d myFastas/multiFasta.fa -t 4 -o myResults.txt -f nucletotide
```
### Move the chromedriver to the default path 
```bash
sudo mv path/to/chromedriver usr/bin
```
