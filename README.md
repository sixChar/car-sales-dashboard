# Car Sales Dashboard
A dashboard for looking at historical car sales data in Canada including breakdowns by province, type of vehicle, and origin of manufacture.

## Usage:
First you will need to download the data from https://open.canada.ca/data/en/dataset/0decc62b-3047-417c-81e7-d8f96fac09a9.

Then install the pip requirements with:

`pip install -r requirements.txt`

With the data downloaded and requirements installed we can run the ETL pipeline to extract the data into an sqlite database:

`python pipeline.py` 

* Note: this assumes the data is downloaded into the same directory with the relative path ./20100001-eng/20100001.csv

Now you can run the flask backend:

`python app.py`

Finally, you can view the dashboard in the browser at 127.0.0.1:5000.

## Preview
![screenshot of the dashboard](readme-img.png?raw=true "Screenshot of dashboard")
