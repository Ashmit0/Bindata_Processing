# Bindata_Processing

### Virtual Env 
Once cloned first create virtual env. To do this in the local directory 
```bash 
conda create <env_name> python=3.10
conda activate <env_name> 
```

Now install the required libraries 
```bash
conda install numpy pandas matplotlib  statsmodels
pip install -e . 
```

### Cache Folder 

Folder to store cache files for faster loading 
```bash
mkdir cache 
```

### User Input 

fill the `user_input.ipynb` with the appropriate entries to load the processed data from bindata folders. For each of`underlying` `exp` `start_date` `end_date` `strike_range` and `parent_dict`, a user us allowed to supply any number of entries to make multiple queries. 

- underlying : the underlying to look at. 

- exp : the exp that together with the underlying make a unique contract. 

- start_date , end_date : the range of dates to process the data for the given contract. 

- strike_range : strikes lying within +- strike_gap of  opening spot price of the underlying are considered. 

- dt : time window to look at. 

### Usage 

Look at the `Stationary_Test.ipynb` file for a demo on how to use the `bindata_processing` library, and also how the processed data ( stored in the form of a nested dict ) is structured.  This file aslo contains tests of stationarity conducted on orb2 data and also fits an ARIMA model to it. 

