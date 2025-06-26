from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import requests
from flask import jsonify
from bs4 import BeautifulSoup
import time
from collections import OrderedDict
import traceback
import os,sys
import json, csv

def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized") 
    chrome_options.add_argument("--disable-extensions") 
    chrome_options.add_argument("--disable-infobars") 
    chrome_options.add_argument("--disable-notifications") 

    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options
    
def find_matches_with_both_teams_to_score():
    """
    Reads a JSON file containing match data and filters for matches where
    'both teams to score' appears in either the 'Team streaks' or
    'Head-to-head streaks' with num_teams equal to 2.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        list: A list of match dictionaries that meet the criteria.
    """

    matches = []
    try:
        with open('scrapper/src/ss26_Apr.json', 'r') as f:
            data = json.load(f)

            # If the data is a single match, wrap it in a list for consistent processing
            if isinstance(data, dict):
                data = [data]

            count = 0

            for match in data:
                elegible = True
                count += 1
                team_streaks = match.get('Team streaks', [])
                head_to_head_streaks = match.get('Head-to-head streaks', [])

                matched_criteria = 0
                # Check Team streaks
                #for streak in team_streaks:
                #     if streak.get('streak_description') == 'No clean sheet' and streak.get('num_teams') == 1:
                #         matched_criteria += 1
                #     if streak.get('streak_description') == 'No clean sheet' and streak.get('num_teams') == 2:
                #         matched_criteria += 2
                #     if streak.get('streak_description') == 'Both teams to score' and streak.get('num_teams') == 1:
                #         matched_criteria += 1
                #     if streak.get('streak_description') == 'Over 2 goals' and streak.get('num_teams') == 1:
                #         matched_criteria += 1
                #     if streak.get('streak_description') == 'Both teams to score' and streak.get('num_teams') == 2:
                #         matched_criteria += 2
                #     if streak.get('streak_description') == 'Over 2 goals' and streak.get('num_teams') == 2:
                #         matched_criteria += 2
                    # if streak.get('streak_description') == 'Under 2 goals':
                    #     elegible = False
                    #     break

                # Check Head-to-head streaks only if not already found in Team streaks
                if match not in matches and elegible:
                    for streak in head_to_head_streaks:
                        # if streak.get('streak_description') == 'No clean sheet' and streak.get('num_teams') == 1:
                        #     print(streak)
                        #     matched_criteria += 1
                        # if streak.get('streak_description') == 'No clean sheet' and streak.get('num_teams') == 2:
                        #     print(streak)
                        #     matched_criteria += 2
                        if streak.get('streak_description') == 'Both teams to score':
                            sValue0 = int(streak.get('streak_value').split('/')[0])
                            sValue1 = int(streak.get('streak_value').split('/')[1])
                            if (sValue1 - sValue0) <= 1:
                                matched_criteria += 1
                        if streak.get('streak_description') == 'Over 2 goals':
                            sValue0 = int(streak.get('streak_value').split('/')[0])
                            sValue1 = int(streak.get('streak_value').split('/')[1])
                            if (sValue1 - sValue0) <= 1:
                                matched_criteria += 1
                        # if streak.get('streak_description') == 'Both teams to score' and streak.get('num_teams') == 1:
                        #     matched_criteria += 1
                        # if streak.get('streak_description') == 'Over 2 goals' and streak.get('num_teams') == 1:
                        #     matched_criteria += 1
                        if streak.get('streak_description') == 'Under 2 goals':
                            matched_criteria = 0
                            break

                if matched_criteria > 1:
                    print('criteria score: ' + str(matched_criteria))
                    # Create a copy of the match to avoid modifying the original data
                    match_copy = match.copy()

                    # Remove the streaks lists
                    if 'Team streaks' in match_copy:
                        del match_copy['Team streaks']
                    if 'Head-to-head streaks' in match_copy:
                        del match_copy['Head-to-head streaks']

                    matches.append(match_copy)

    except FileNotFoundError:
        print(f"Error: File not found ")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    print('total matches: ' + str(count))
    print('filtered matches: ' + str(len(matches)))
    return matches


def testSofaScore():
    driver = webdriver.Remote("http://172.17.0.4:4444", options=webdriver.ChromeOptions())
    date = "2024-10-05"
    url = "http://www.sofascore.com/football/2024-10-05"
    driver.get(url)
    driver.maximize_window()
    #delete the cookies  
    driver.delete_all_cookies()  

    return_matches_list = []
    
    ### consent cookies
    try:
        button = driver.find_element(By.CLASS_NAME, "fc-primary-button")
        button.click()
        time.sleep(1)
        driver.get(url)
    except Exception as e:
        print(f"Error finding or clicking button by CLASS_NAME: {e}")

    # --- Configuration ---
    max_matches_to_collect = 300  # Example value
    batch_size = 10  # Example value
    scroll_offset = 150  # Example value (adjust as needed)
    bottom_scroll_threshold = 500  # Pixels from the bottom to stop scrolling

    # --- Main Loop ---
    total_matches_collected = 0
    return_matches_list = []
    seen_ids = OrderedDict()

    time.sleep(3)

    while total_matches_collected < max_matches_to_collect:
        matches = driver.find_elements(By.CSS_SELECTOR, 'a[data-id]')
        print(f"Found {len(matches)} matches")

        new_batch_count = 0

        for i, match in enumerate(matches):
            if new_batch_count >= batch_size or total_matches_collected >= max_matches_to_collect:
                break  # Break the inner loop if batch size or total limit reached

            match_id = match.get_attribute("data-id")

            if match_id and match_id not in seen_ids.keys():
                seen_ids[match_id] = None
                try:
                    # Scroll directly to the Y position minus offset
                    y_position = match.location['y']
                    driver.execute_script(f"window.scrollTo(0, {y_position - scroll_offset});")
                    time.sleep(1.5)  # Let scroll settle and content fully render

                    # Re-find the match element to avoid staleness
                    fresh_match = driver.find_element(By.CSS_SELECTOR, f'a[data-id="{match_id}"]')

                    # Now safe to extract
                    match_data = collect_match_data(driver, fresh_match)
                    match_data['date'] = date
                    return_matches_list.append(match_data)
                    total_matches_collected += 1
                    new_batch_count += 1
                    print(f"Collected match {total_matches_collected}: {fresh_match.text}")

                except Exception as e:
                    print(f"Error collecting match: {e}")
                    continue  # Continue to the next match

        #break
        # Check if near the bottom *before* scrolling further
        if is_near_bottom(driver, bottom_scroll_threshold):
            print("Reached the bottom (or near to it). Stopping scrolling.")
            break
            matches = driver.find_elements(By.CSS_SELECTOR, 'a[data-id]')
            print(len(matches))

            # Filter matches based on seen_ids
            # filtered_matches = []
            # for match in matches:
            #     match_id = match.get_attribute("data-id")
            #     if match_id not in seen_ids:
            #         filtered_matches.append(match)
            # matches = filtered_matches  # Use the filtered list

            last_seen_id = list(seen_ids.keys())[-1]

            start_index = -1  # Initialize to -1 to indicate ID not found yet

            for i, match in enumerate(matches):
                data_id = match.get_attribute("data-id")
                if data_id == last_seen_id:
                    start_index = i
                    break  # Stop searching once the ID is found

            matches = matches[start_index:]
            print(f"Filtered matches to {len(matches)} based on seen_ids.")

            for i, match in enumerate(matches):
                # if new_batch_count >= batch_size or total_matches_collected >= max_matches_to_collect:
                #     break  # Break the inner loop if batch size or total limit reached

                print(matches[i].get_attribute('outerHtml'))
                if matches[i].get_attribute('outerHtml') is None:
                    continue
                match_id = match.get_attribute("data-id")

                if match_id and match_id not in seen_ids.keys():
                    try:
                        # Re-find the match element to avoid staleness
                        fresh_match = driver.find_element(By.CSS_SELECTOR, f'a[data-id="{match_id}"]')

                        # Now safe to extract
                        match_data = collect_match_data(driver, fresh_match)
                        return_matches_list.append(match_data)
                        total_matches_collected += 1
                        new_batch_count += 1
                        print(f"Collected match {total_matches_collected}: {fresh_match.text}")

                    except Exception as e:
                        print(f"Error collecting match: {e}")
                        continue  # Continue to the next match
            break

        # Scroll a bit further to load new items
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(1)

    print("Data collection complete.")
    
    driver.quit()
    return return_matches_list


def is_near_bottom(driver, threshold):
    """Checks if the page is scrolled within a certain threshold of the bottom."""
    total_height = driver.execute_script("return document.body.scrollHeight")
    window_height = driver.execute_script("return window.innerHeight")
    scroll_position = driver.execute_script("return window.pageYOffset")

    # Calculate the distance to the bottom
    distance_to_bottom = total_height - (scroll_position + window_height)
    return distance_to_bottom <= threshold


def collect_match_data(driver, match):
    try:
        match.click()

        widget = driver.find_elements(By.CLASS_NAME, "widget")[0]

        match_data = {}
        try:
            # Extract match info from each element
            match_data = extract_match_info(driver, widget)
            # Extract team names
            left_team_element = match.find_element(By.CSS_SELECTOR, "div[data-testid='left_team'] bdi.Text")
            left_team_name = left_team_element.text
            right_team_element = match.find_element(By.CSS_SELECTOR, "div[data-testid='right_team'] bdi.Text")
            right_team_name = right_team_element.text
            match_data['home_team'] = left_team_name
            match_data['away_team'] = right_team_name

        except Exception as e:
            print(f"Error processing a match element: {e}")
        #return match_data
        time.sleep(1)
        matches_button = widget.find_element(By.CSS_SELECTOR, "h2[data-tabid^=matches]")
        scrollable_container = widget.find_element(By.CLASS_NAME, "Scrollable.gnFCJf")
        driver.execute_script("""arguments[0].scrollLeft = arguments[1].offsetLeft;""", scrollable_container, matches_button)
        matches_button.click()
        time.sleep(1)
        # Find all elements with the data-testid "team_streaks"
        team_streaks_elements = widget.find_elements(By.CSS_SELECTOR, "div[data-testid='team_streaks']")
        print("streaks: " + str(len(team_streaks_elements)))

        for team_streaks_element in team_streaks_elements:
            try:
                # Extract the heading to determine the type of streaks
                heading_element = team_streaks_element.find_element(By.CSS_SELECTOR, "h3.textStyle_display\\.medium")
                heading_text = heading_element.text

                # Extract the streaks data
                streaks_data = extract_team_streaks_data(team_streaks_element)

                match_data[heading_text] = streaks_data

            except Exception as e:
                print(f"Error processing a team_streaks element: {e}")

        return match_data
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def is_scroll_bottom(driver):
    """
    Checks if the scrollbar is at the bottom of the page.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        True if the scrollbar is at the bottom, False otherwise.
    """
    return driver.execute_script(
        "return (window.innerHeight + window.pageYOffset) >= document.documentElement.scrollHeight;"
    )

def extract_match_info(driver, html_element):
    """
    Extracts team names, HT result, and FT result from the given HTML element.

    Args:
        driver: The Selenium WebDriver instance.
        html_element: The WebElement representing the main div containing match info.

    Returns:
        A dictionary containing the team names, HT result, and FT result.
        Returns None if any of the required elements are not found.
    """

    try:
        # Extract competition
        competition = html_element.find_element(By.CSS_SELECTOR, "div[class='Box Flex fjeRum iZIMiI']").text

        # Extract FT result
        ft_result_element = html_element.find_element(By.CSS_SELECTOR, "span[data-testid='left_score']")
        right_score_element = html_element.find_element(By.CSS_SELECTOR, "span[data-testid='right_score']")
        ft_result = f"{ft_result_element.text} - {right_score_element.text}".replace(' ', '')

        # Extract HT result
        ht_result_element = html_element.find_element(By.XPATH, ".//div[contains(text(), 'HT')]")
        ht_result = ht_result_element.text.replace("HT ", "").replace(' ', '')  # Remove "HT " prefix

        return {
            "competition": competition,
            "ft_result": ft_result,
            "ht_result": ht_result,
        }

    except Exception as e:
        print(f"Error extracting match info: {e}")
        return None



def extract_team_streaks_data(team_streaks_element):
    """
    Extracts data from a single 'team_streaks' element.

    Args:
        driver: The Selenium WebDriver instance.
        team_streaks_element: The WebElement representing the 'team_streaks' div.

    Returns:
        A list of dictionaries, where each dictionary represents a streak
        and contains the team image URL, streak description, and streak value.
        Returns an empty list if no streaks are found.
    """

    streaks_data = []
    try:
        # Find all the streak rows within the team_streaks element
        streak_rows = team_streaks_element.find_elements(By.CSS_SELECTOR, "div[display='flex'].cgesZG.MHPeY")

        for row in streak_rows:
            try:
                # Extract team image URL
                img_elements = len(row.find_elements(By.CSS_SELECTOR, "img"))
                #team_image_url = img_element.get_attribute("src")

                # Extract streak description
                description_element = row.find_element(By.CSS_SELECTOR, "span[color='onSurface.nLv1'].Text.hEeLIF")
                streak_description = description_element.text

                # Extract streak value
                value_element = row.find_element(By.CSS_SELECTOR, "span[color='onSurface.nLv1'].Text.imquCm")
                streak_value = value_element.text

                streaks_data.append({
                    "num_teams": img_elements,
                    "streak_description": streak_description,
                    "streak_value": streak_value,
                })

            except Exception as e:
                print(f"Error extracting data from a streak row: {e}")

    except Exception as e:
        print(f"Error finding streak rows: {e}")

    return streaks_data