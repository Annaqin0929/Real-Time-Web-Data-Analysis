from fake_useragent import UserAgent
import csv
import time
import random
import requests
from lxml import etree
import re
import pandas as pd
import folium
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Boxplot
from pyecharts.charts import Pie


def get_weblink():
    """define file for No, SN, Location, Weblinks"""
    with open('weblink.csv', 'w') as csvfile:
        fieldnames = ['No.', 'SN', 'Location', 'Weblink', 'Page']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    result = []
    # define the page number in each area, range should be ~ (1, 31) for one-month data
    for page in range(1, 3):
        url = f'https://www.trademe.co.nz/a/property/residential/rent/canterbury/christchurch-city?page={page}'
        try:
            time.sleep(random.uniform(1, 3))
            #response = requests.get(url, headers=headers, timeout=5)
            response = requests.get(url, headers=headers, timeout=25)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            print("Timeout error, website took too long to respond.")
        except requests.exceptions.RequestException as e:
            print("Error: ", e)
        else:
            html = response.text

            root = etree.HTML(html)

            for i in range(3, 25):
                href_string = ''.join(root.xpath(f'/html/body/tm-root/div[1]/main/div/tm-property-search-component/div/div[1]/tm-property-search-results/div/div[3]/tm-search-results/div/div[2]/tg-row/tg-col[{i}]/tm-search-card-switcher/tm-property-premium-listing-card/div/a/@href'))
                print(href_string)
                print(type(href_string))
                pattern = r"/([^/]+)/listing/(\d+)\?"
                matches = re.findall(pattern, href_string)

                if matches:
                    suburb, listing_id = matches[0]
                    print(suburb)
                    print(listing_id)
                    href = f'https://www.trademe.co.nz/a/property/residential/rent/canterbury/christchurch-city/{suburb}/listing/{listing_id}'
                    print(href)
                    result.append(href)
                    # write link info to weblink.csv file
                    with open('weblink.csv', 'a', encoding='utf_8_sig', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([i - 2, listing_id, suburb, href, page])
                else:
                    print("No matches found.")
    print(result)
    return result


def get_detail(hrefs):
    """get the tier2 href link and generate the master data csv file"""
    # define file for data.cvs, including date, address, price, number of bedrooms and description
    with open('data.csv', 'w') as csvfile:
        fieldnames = ['No.', 'Date', 'Address', 'Price per Week', 'Bedroom', 'Description', 'Weblink']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    i = 1
    for href in hrefs:
        try:
            url = href
            time.sleep(random.uniform(5, 10))
            response = requests.get(url, timeout=8)
            response.raise_for_status()

        except requests.exceptions.Timeout:
            print("Timeout error, website took too long to respond.")

        except requests.exceptions.RequestException as e:
            print("Error: ", e)

        else:
            html = response.text
            root = etree.HTML(html)
            try:
                date_string = ''.join(root.xpath('/html/body/tm-root/div[1]/main/div/tm-property-listing/div/div[3]/tg-row[1]/tg-col/tm-property-listing-body/div/section[1]/div/text()')).strip()
            except:
                date_string = None
                print("no info for date")

            try:
                price_string = ''.join(root.xpath('/html/body/tm-root/div[1]/main/div/tm-property-listing/div/div[3]/tg-row[1]/tg-col/tm-property-listing-body/div/section[1]/h2[2]/strong/text()')).strip()
            except:
                price_string = None
                print("no info for price")

            try:
                address_string = ''.join(root.xpath('/html/body/tm-root/div[1]/main/div/tm-property-listing/div/div[3]/tg-row[1]/tg-col/tm-property-listing-body/div/section[1]/h1/text()')).strip()
            except:
                address_string = None
                print("no info for address")

            try:
                bedroom_string = ''.join(root.xpath('/html/body/tm-root/div[1]/main/div/tm-property-listing/div/div[3]/tg-row[1]/tg-col/tm-property-listing-body/div/section[1]/tm-property-listing-attributes/section/ul[1]/li[1]/tm-property-listing-attribute-tag/tg-tag/span/div/text()')).strip()
            except:
                bedroom_string = None
                print("no info for bedrooms")

            try:
                des_string = ''.join(root.xpath('/html/body/tm-root/div[1]/main/div/tm-property-listing/div/div[3]/tg-row[1]/tg-col/tm-property-listing-body/div/section[2]/tm-property-listing-description/tm-markdown/div/p/text()')).strip()
            except:
                des_string = None
                print("no info for description")

            with open('data.csv', 'a', encoding='utf_8_sig', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([i, date_string, address_string, price_string, bedroom_string, des_string, href])

        i = i+1
    file_name = 'data.csv'
    return file_name

def data_clean():
    # combine file list
    file_names = ['data.csv']
    # combine all data
    all_data = pd.concat([pd.read_csv(file) for file in file_names], ignore_index=True)
    # delete all blank rows
    all_data.dropna(inplace=True)

    # create a new file with all data
    all_data.to_csv('data_clean.csv', index=False)
    df = pd.read_csv("data_clean.csv")

    # add ID and Suburb
    df['ID'] = df['Weblink'].str.split('/listing/').str[1]
    df['Suburb'] = df['Weblink'].str.split('/listing/').str[0].str.split('/').str[-1]
    print(df['Suburb'])
    # save to csv file
    df.to_csv('data_clean.csv', index=False)

    # re-arrange No. value
    df['No.'] = range(1, len(df) + 1)

    # export address to the heatmap_tm.csv file
    df['Address'] = df['Address'].str.replace(' ', '')
    df.Address.dropna().to_csv("heatmap_tm.csv", index=False)
    print(df['Address'])
    # deal with price column
    df['Price per Week'] = df['Price per Week'].apply(lambda x: re.sub(r'[^\d.]', '', x)).astype(int)
    df = df.rename(columns={'Price per Week': 'Weekly Rent $'})

    # deal with bedroom info
    df['Bedroom'] = df['Bedroom'].apply(lambda x: re.sub(r'[^\d.]', '', x)).astype(int)
    print(df['Bedroom'])
    # add new column with rent per Bedroom
    df['Rent per Bedroom'] = (df['Weekly Rent $'] / df['Bedroom']).astype(int)
    df.to_csv('data_clean.csv', index=False)
    heatmap_tm = pd.read_csv('heatmap_tm.csv')
    heatmap_tm.loc[:, 'Rent per Bedroom'] = df['Rent per Bedroom']
    heatmap_tm.to_csv('heatmap_tm.csv', index=False, mode='w')

    # update the date format
    df['Date'] = pd.to_datetime(df['Date'].str.extract(r'(\d+ \w+)')[0] + ' 2023')
    print(df['Date'])
    # display headers
    print("headers：")
    print(df.columns.tolist())

    # show columns and rows
    num_rows = len(df)
    num_cols = len(df.columns)
    print(f"Rows：{num_rows}")
    print(f"Columns：{num_cols}")

    # Get data ready in one file for visualization
    df.to_csv("data_analysis.csv", index=False)


def create_heatmap():
    # Replace YOUR_API_KEY with your actual API key
    API_KEY = 'Please input your GoogleMaps API KEY Here'

    # Load data into a pandas DataFrame
    data = pd.read_csv('heatmap_tm.csv')
    print(data.head(10))
    print("Rows：", data.shape[0])
    print("Columns：", data.shape[1])

    # Get the latitude and longitude coordinates for each property using the Google Maps Geocoding API
    latitudes = []
    longitudes = []
    for address in data['Address']:
        url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}'
        response = requests.get(url).json()
        location = response['results'][0]['geometry']['location']
        latitudes.append(location['lat'])
        longitudes.append(location['lng'])
        print(f"Address: {address}, Latitude: {location['lat']}, Longitude: {location['lng']}")
    data['latitude'] = latitudes
    data['longitude'] = longitudes

    # Add the latitudes and longitudes to the CSV file
    data.to_csv('heatmap_tm.csv', index=False)

    print("Latitude and longitude data saved to heatmap_tm.csv")

    #Create a map centered at Christchurch, New Zealand
    m = folium.Map(location=[-43.5321, 172.6362], zoom_start=12)

    # Create a map centered at Christchurch, New Zealand
    map_center = [-43.5321, 172.6362]
    zoom_level = 13
    m = folium.Map(location=map_center, zoom_start=zoom_level)

    # Define color scale for the markers
    colors = ['green', 'yellow', 'orange', 'red', 'purple']
    price_ranges = pd.qcut(data['Rent per Bedroom'], q=5)
    color_dict = {str(price_range): color for price_range, color in zip(price_ranges.unique(), colors)}

    # Add a circle marker for each property, with color based on price
    for i, row in data.iterrows():
        folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=5,
                            color=color_dict[str(price_ranges[i])], fill=True, fill_opacity=0.7).add_to(m)

    # Save the map as an HTML file
    m.save('heatmap.html')


def visual_chart_tm():
    # read file in pandas
    df = pd.read_csv('data_analysis.csv')

    # group by suburb and calculate the average price in the past 4 weeks
    avg_prices = {}
    for region in df['Suburb'].unique():
        avg_price = df[df['Suburb'] == region]['Rent per Bedroom'].mean()
        avg_prices[region] = round(avg_price)

    # print(avg_prices)

    # generate list of dict
    x_axis = list(avg_prices.keys())
    y_axis = list(avg_prices.values())

    # Use Pyecharts to generate the bar chart
    bar = (
        Bar()
        .add_xaxis(x_axis)
        .add_yaxis("Average Price", y_axis)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Average Price by Suburbs in Christchurch"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90, font_size=10, interval=0)),
            yaxis_opts=opts.AxisOpts(name="Price per each bedroom ($NZ)"),
        )
    )

    # save to html
    bar.render("avg_price_tm.html")

    # statistic Results of each suburb by Boxplot
    grouped = df.groupby('Suburb')['Rent per Bedroom'].agg(['max', 'min', 'mean']).reset_index()
    grouped = grouped.round(0)
    q1 = df.groupby('Suburb')['Rent per Bedroom'].quantile(0.25).reset_index()
    q2 = df.groupby('Suburb')['Rent per Bedroom'].quantile(0.5).reset_index()
    q3 = df.groupby('Suburb')['Rent per Bedroom'].quantile(0.75).reset_index()
    q1 = q1.round(0)
    q3 = q3.round(0)
    q1.columns = ['Suburb', 'q1']
    q3.columns = ['Suburb', 'q3']
    grouped = pd.merge(grouped, q1, on='Suburb', how='left')
    grouped = pd.merge(grouped, q2, on='Suburb', how='left')
    grouped = pd.merge(grouped, q3, on='Suburb', how='left')

    # Create Boxplot Chart
    boxplot = (
        Boxplot()
        .add_xaxis(grouped['Suburb'].tolist())
        .add_yaxis("", grouped[['min', 'q1', 'mean', 'q3', 'max']].values.tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Price Boxplot by Suburb in Christchurch"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90, font_size=10, interval=0)),
            yaxis_opts=opts.AxisOpts(name='Rent per Bedroom'),
        )
    )
    # save boxplot to html
    boxplot.render('boxplot_tm.html')

    # start to create pie chart
    df0_1 = df[(df['Rent per Bedroom'] >= 100) & (df['Rent per Bedroom'] <= 150)].shape[0]
    df1_2 = df[(df['Rent per Bedroom'] > 150) & (df['Rent per Bedroom'] <= 200)].shape[0]
    df2_3 = df[(df['Rent per Bedroom'] > 200) & (df['Rent per Bedroom'] <= 250)].shape[0]
    df3_4 = df[(df['Rent per Bedroom'] > 250) & (df['Rent per Bedroom'] <= 300)].shape[0]
    df4_5 = df[(df['Rent per Bedroom'] > 300) & (df['Rent per Bedroom'] <= 350)].shape[0]
    df5 = df[(df['Rent per Bedroom'] > 350)].shape[0]
    labels = ['$100-$150', '$150-$200', '$200-$250', '$250-$300', '$300-$350', ' >$350']
    values = [df0_1, df1_2, df2_3, df3_4, df4_5, df5]

    c = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(labels, values)],
            radius=["40%", "55%"],
            label_opts=opts.LabelOpts(
                position="outside",
                formatter="{b|{b}: }{c}  {per|{d}%}  ",
                background_color="#eee",
                border_color="#aaa",
                border_width=1,
                border_radius=4,
                rich={
                    "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                    "abg": {
                        "backgroundColor": "#e3e3e3",
                        "width": "100%",
                        "align": "right",
                        "height": 22,
                        "borderRadius": [4, 4, 0, 0],
                    },
                    "hr": {
                        "borderColor": "#aaa",
                        "width": "100%",
                        "borderWidth": 0.5,
                        "height": 0,
                    },
                    "b": {"fontSize": 16, "lineHeight": 33},
                    "per": {
                        "color": "#eee",
                        "backgroundColor": "#334455",
                        "padding": [2, 4],
                        "borderRadius": 2,
                    },
                },
            ),
        )

        .set_global_opts(title_opts=opts.TitleOpts(title="Pie Chart of each price range",
                                                   subtitle='          TradeMe.com---2023.April',
                                                   pos_left='center', pos_top='bottom'))
        .render("Pie_Price_tm.html")
    )

def main():
    """define the main function
    including get_weblink(), get_detail(href), data_clean(), create_heatmap(), visual chart()"""
    hrefs = get_weblink()
    #get_detail(hrefs)
    data_clean()
    create_heatmap()
    visual_chart_tm()


if __name__ == '__main__':
    ua = UserAgent(verify_ssl=False)
    headers = {
        'User-Agent': "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 96.0.4664 .93 Safari / 537.36",
    }
    time.sleep(random.uniform(1, 2))
    main()
