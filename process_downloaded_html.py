import pandas as pd
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

def parse_power_html(html_path):
    print(f"Processing {html_path}...")
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    data = []
    # Find all tables with class 'history_view_table'
    tables = soup.find_all('table', class_='history_view_table')
    
    for table in tables:
        # Check rows. The structure is customized. 
        # Usually checking the span with style for Draw Term
        rows = table.find_all('tr')
        # Filter for rows that contain data. 
        # Based on analysis: First row has Date, Second row has Numbers
        # Actually it seems nested.
        # Let's look for the span with specific color for Draw ID
        
        # New approach based on inspection:
        # Identify the date cell
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        
        # Iterate through all tds to find dates
        tds = table.find_all('td')
        for i, td in enumerate(tds):
            text = td.get_text(separator=' ', strip=True)
            date_match = date_pattern.search(text)
            if date_match:
                date_str = date_match.group(0)
                
                # Verify if this is February 2026
                if not date_str.startswith('2026-02'):
                    continue
                
                # Winning numbers are usually in a ul/li structure in the same or next cell?
                # In power_source.html lines 322-334:
                # td (rowspan 2) contains Date
                # next td contains ul.history_ball
                # next td contains zone2
                
                # Use parent tr to find siblings
                parent_tr = td.find_parent('tr')
                if not parent_tr:
                    continue
                
                # Find ul class="history_ball"
                ball_ul = parent_tr.find('ul', class_='history_ball')
                if not ball_ul:
                    continue
                
                # Find '大小順序' section
                sorted_li = None
                for li in ball_ul.find_all('li'):
                    if '大小順序' in li.get_text():
                        sorted_li = li
                        break
                
                if not sorted_li:
                   # Fallback to just taking all links in the ul if '大小順序' not found
                   # But usually it is there.
                   links = ball_ul.find_all('a', class_='history_ball_link')
                   # If we take all, we might get duplicates (Order vs Size). 
                   # First 6 are order, Next 6 are size.
                   if len(links) >= 12:
                       nums = [int(link.get_text(strip=True)) for link in links[6:12]]
                   elif len(links) >= 6:
                       nums = [int(link.get_text(strip=True)) for link in links[:6]]
                   else:
                       continue
                else:
                    links = sorted_li.find_all('a', class_='history_ball_link')
                    nums = [int(link.get_text(strip=True)) for link in links]
                
                # Zone 2
                # usually the td after the ball td
                # The ball td is the second td in the tr (index 1) if date is index 0
                # Let's find the td with specific style for special number
                special_td = parent_tr.find('td', style=lambda x: x and 'color:#005aff' in x and 'font-size:48px' in x)
                if special_td:
                    special = special_td.get_text(strip=True)
                else:
                    # Fallback: finding simple number
                    # It is the 3rd td in the row
                    cells = parent_tr.find_all('td', recursive=False)
                    if len(cells) >= 3:
                        special = cells[2].get_text(strip=True)
                    else:
                        special = None
                
                if nums and special:
                    # Create record
                    # 539/Lotto/Power CSV format usually: date, num1, num2, num3, num4, num5, num6, special
                    # For Power: date, 1, 2, 3, 4, 5, 6, zone2
                    row_data = {
                        'date': date_str,
                        '1': nums[0],
                        '2': nums[1],
                        '3': nums[2],
                        '4': nums[3],
                        '5': nums[4],
                        '6': nums[5],
                        'zone2': special  # Corrected key for Power
                    }
                    data.append(row_data)
                    print(f"Parsed Power {date_str}: {nums} + {special}")

    return pd.DataFrame(data)

def parse_lotto_html(html_path):
    print(f"Processing {html_path}...")
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    data = []
    tables = soup.find_all('table', class_='history_view_table')
    
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    
    for table in tables:
        tds = table.find_all('td')
        for td in tds:
            text = td.get_text(separator=' ', strip=True)
            date_match = date_pattern.search(text)
            if date_match:
                date_str = date_match.group(0)
                if not date_str.startswith('2026-02'):
                    continue
                
                parent_tr = td.find_parent('tr')
                if not parent_tr: continue
                
                ball_ul = parent_tr.find('ul', class_='history_ball')
                if not ball_ul: continue
                
                sorted_li = None
                for li in ball_ul.find_all('li'):
                    if '大小順序' in li.get_text():
                        sorted_li = li
                        break
                
                if sorted_li:
                   links = sorted_li.find_all('a', class_='history_ball_link')
                   nums = [int(link.get_text(strip=True)) for link in links]
                else:
                   links = ball_ul.find_all('a', class_='history_ball_link')
                   if len(links) >= 12: nums = [int(t.get_text()) for t in links[6:12]]
                   else: nums = [int(t.get_text()) for t in links[:6]]
                
                special_td = parent_tr.find('td', style=lambda x: x and 'color:#005aff' in x)
                special = special_td.get_text(strip=True) if special_td else "0"
                
                if nums:
                    row_data = {
                        'date': date_str,
                        '1': nums[0], '2': nums[1], '3': nums[2],
                        '4': nums[3], '5': nums[4], '6': nums[5],
                        'special': special
                    }
                    data.append(row_data)
                    print(f"Parsed Lotto {date_str}: {nums} + {special}")
    
    return pd.DataFrame(data)

def parse_star3_html(html_path):
    print(f"Processing {html_path}...")
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    data = []
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    
    rows = soup.find_all('tr', class_='history_view_star')
    for row in rows:
        tds = row.find_all('td')
        if len(tds) < 3: continue
        
        # Date is in 3rd td: <em>2026-02-10</em> (星期二)
        date_text = tds[2].get_text()
        date_match = date_pattern.search(date_text)
        if not date_match: continue
        date_str = date_match.group(1)
        
        if not date_str.startswith('2026-02'): continue
        
        # Numbers in 2nd td: <td class="history_view_star_ball"><span>7</span>...
        ball_td = tds[1]
        spans = ball_td.find_all('span')
        nums = [s.get_text(strip=True) for s in spans]
        
        if len(nums) == 3:
            row_data = {
                'date': date_str,
                '1': nums[0], '2': nums[1], '3': nums[2]
            }
            data.append(row_data)
            print(f"Parsed Star3 {date_str}: {nums}")
            
    return pd.DataFrame(data)

def parse_star4_html(html_path):
    print(f"Processing {html_path}...")
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    data = []
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    
    rows = soup.find_all('tr', class_='history_view_star')
    for row in rows:
        tds = row.find_all('td')
        if len(tds) < 3: continue
        
        date_text = tds[2].get_text()
        date_match = date_pattern.search(date_text)
        if not date_match: continue
        date_str = date_match.group(1)
        
        if not date_str.startswith('2026-02'): continue
        
        ball_td = tds[1]
        spans = ball_td.find_all('span')
        nums = [s.get_text(strip=True) for s in spans]
        
        if len(nums) == 4:
            row_data = {
                'date': date_str,
                '1': nums[0], '2': nums[1], '3': nums[2], '4': nums[3]
            }
            data.append(row_data)
            print(f"Parsed Star4 {date_str}: {nums}")
            
    return pd.DataFrame(data)

def update_csv(file_path, new_df, sort_keys=['date']):
    if new_df.empty:
        print(f"No new data for {file_path}")
        return

    if os.path.exists(file_path):
        try:
            old_df = pd.read_csv(file_path)
            # Ensure columns match
            # If columns are named 0,1,2... in old csv, we might need to adjust
            # Assume headers exist or use consistent names.
            # My parser uses 'date', '1', '2' etc. 
            # Let's check old_df columns
            print(f"Current columns in {file_path}: {old_df.columns.tolist()}")
            
            # Unify column names if necessary. 
            # Usually for lottos it is date, n1...n6, special.
            # Let's align new_df to old_df's columns if they are reasonably close
            
            combined_df = pd.concat([old_df, new_df], ignore_index=True)
            combined_df.drop_duplicates(subset=['date'], keep='last', inplace=True)
            combined_df.sort_values(by=sort_keys, ascending=False, inplace=True) # Descending for latest first? Or Ascending?
            # User usually wants ascending for Training, but display might be descending.
            # Let's check typical format. usually ascending in CSV for time series.
            combined_df.sort_values(by=sort_keys, ascending=True, inplace=True)
            
            combined_df.to_csv(file_path, index=False)
            print(f"Updated {file_path}. Total records: {len(combined_df)}")
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
    else:
        new_df.sort_values(by=sort_keys, ascending=True, inplace=True)
        new_df.to_csv(file_path, index=False)
        print(f"Created {file_path}. Total records: {len(new_df)}")

def main():
    # Power
    df_power = parse_power_html('d:\\539\\power_source.html')
    update_csv('d:\\539\\data\\power\\power_history.csv', df_power)
    
    # Lotto
    df_lotto = parse_lotto_html('d:\\539\\lotto_source.html')
    update_csv('d:\\539\\data\\lotto\\lotto_history.csv', df_lotto)
    
    # Star3
    df_star3 = parse_star3_html('d:\\539\\star3_source.html')
    update_csv('d:\\539\\data\\star3\\star3_history.csv', df_star3)
    
    # Star4
    df_star4 = parse_star4_html('d:\\539\\star4_source.html')
    update_csv('d:\\539\\data\\star4\\star4_history.csv', df_star4)

if __name__ == "__main__":
    main()
