## Here I was playing with functionality of Jupyter Notebook, trying to run it online

As a first step, you would like to open you NB in **NBviewer**: https://nbviewer.jupyter.org/. Afterwards you could press **Binder** button in the top write corner. This will open you NB on a separate Python server.

Afterwards I realized that you could even do `pip install` inside the NB. For example:
```
import sys
!{sys.executable} -m pip install yfinance
!{sys.executable} -m pip install matplotlib
```
If you would like to surpress not-needed messages , when installing the packages, add `%%capture` to the 1st row of a the cell

You could also read files (e.g. csv), which are located on Github. For this you need use URL to raw file (if you open a file on Github, press "raw" button there and copy URL)
```
url = 'https://raw.githubusercontent.com/alexanu/Data_analysis_snippets/main/tickers.csv'
df = pd.read_csv(url)
```
You could also run your scripts inside the NB using `%load` and `%run`. For `%load` you should also use the URL to raw file:
```
%load https://raw.githubusercontent.com/alexanu/Data_analysis_snippets/main/test_jup2.py
%run test_jup2.py
```