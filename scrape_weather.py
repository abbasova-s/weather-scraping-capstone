# Initialization
import pandas as pd
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# Driver configurations
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    options=options
)


# Fetch the web page
driver.get("https://www.timeanddate.com/weather/")


# Give the page time to load
time.sleep(10)


# Find the weather table
weather_table = driver.find_element(
    By.CSS_SELECTOR,
    "table"
)


# Find all rows in the table
rows = weather_table.find_elements(
    By.TAG_NAME,
    "tr"
)


# Create an empty list for the results
results = []


# Main loop
for row in rows:

    cells = row.find_elements(By.TAG_NAME, "td")

    # Each city has City, Local Time, Weather, Temperature

    for i in range(0, len(cells), 4):

        if i + 3 < len(cells):

            # Check if the city cell contains a link
            city_links = cells[i].find_elements(By.TAG_NAME, "a")

            # Skip cells that do not contain a city link
            if not city_links:
                continue

            # Find city
            city = city_links[0].text.strip()

            # Find local time
            local_time = cells[i + 1].text.strip()

            # Find weather description
            weather_images = cells[i + 2].find_elements(By.TAG_NAME, "img")

            if weather_images:
                weather_description = (weather_images[0].get_attribute("alt"))
            else:
                weather_description = cells[i + 2].text.strip()

            # Find temperature
            temperature = cells[i + 3].text.strip()

            # Create a dictionary
            result = {
                "City": city,
                "Local time": local_time,
                "Weather description": weather_description,
                "Temperature": temperature
            }

            # Add dictionary to results
            results.append(result)


# Create a DataFrame
weather_df = pd.DataFrame(results)


# Show the raw data
print("Raw data:")
print(weather_df)

print("\nNumber of rows before cleaning:")
print(len(weather_df))


# Save the raw data
weather_df.to_csv("weather_raw.csv", index=False)


""" Data Cleaning """

# Make a copy for cleaning
clean_df = weather_df.copy()


# Remove duplicate rows
clean_df = clean_df.drop_duplicates()


# Remove extra spaces from text columns
clean_df["City"] = clean_df["City"].str.strip()

clean_df["Local time"] = (clean_df["Local time"].str.strip())

clean_df["Weather description"] = (clean_df["Weather description"].str.strip())


# Clean the temperature column
clean_df["Temperature"] = (clean_df["Temperature"].str.replace(" °F", "", regex=False).str.strip())
clean_df["Temperature"] = pd.to_numeric(clean_df["Temperature"], errors="coerce")


# Remove rows with missing values
clean_df = clean_df.dropna()


# Reset the index
clean_df = clean_df.reset_index(drop=True)


""" Show Before / After Cleaning """

print("\nRows before cleaning:")
print(len(weather_df))

print("\nRows after cleaning:")
print(len(clean_df))

print("\nClean data:")
print(clean_df)


# Save the clean data to a CSV file
clean_df.to_csv("weather_clean.csv", index=False)


# Close the browser
driver.quit()

# Save data to SQLite database
with sqlite3.connect("weather.db") as conn:
    weather_df.to_sql("weather_raw", conn, if_exists="replace", index=False)
    clean_df.to_sql("weather_clean", conn, if_exists="replace", index=False)

print("Data saved to SQLite database")



