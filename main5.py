import requests
from bs4 import BeautifulSoup
import pandas as pd
# import time
from datetime import datetime, time
import re

import pathlib
import os

from tkinter import *
import mysql.connector
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog as fd
from PIL import Image, ImageDraw

file_path = pathlib.Path(__file__).parent.resolve()
path = str(file_path) + "\\Dependencies\\"
passer = input("Enter Your MySQL pasword: ")
MainScreen_location = str(file_path) + "\\Dependencies\\Images\\MainScreen\\"

live_score = ""
Live_Score_Label = None  

start_time = time(7, 30)
end_time = time(11, 0)

# target_datetime = datetime(2024, 4, 25, 18, 30)
current_datetime = datetime.now().time()

username = 'root'
password = passer
host = 'localhost'
port = '3306'
database = 'IPL'

def get_link():
    today_date = datetime.now()
    todays_date = today_date.strftime("%b %d")


    try:
        connection = mysql.connector.connect(
            user=username,
            password=password,
            host=host,
            port=port,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor()

            command = f"SELECT * FROM IPL_SCHEDULE WHERE DATE = '{todays_date}'"
            cursor.execute(command)
            result = cursor.fetchone()
            print(result)

            if result == None:
                command = f"SELECT * FROM IPL_SCHEDULE WHERE DATE = 'Unknown'"
                cursor.execute(command)
                result = cursor.fetchone()
                print(result)

            try: 
                link = result[-1]
                return link
            except:
                return None
            

    except mysql.connector.Error as error:
        print("Failed to insert DataFrame into MySQL table {}".format(error))
        return None

    finally:
        # Close MySQL connection
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


def first_time_run():
    def batting_insert():
        url = "https://www.espncricinfo.com/records/trophy/batting-highest-career-batting-average/indian-premier-league-117"

        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")


        table = soup.find('table')
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all(['th', 'td'])
            cols = [col.text.strip() for col in cols]
            data.append(cols)

        df = pd.DataFrame(data)
        df = df.drop([1], axis=1)
        df = df.iloc[1:]
        df = df.replace("-", 0)
        try:
            connection = mysql.connector.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=database
            )

            if connection.is_connected():
                cursor = connection.cursor()

                # Create table
                create_table_query = '''
                CREATE TABLE IF NOT EXISTS batting_records (
                        Player VARCHAR(255),
                        Matches VARCHAR(255),
                        Inns VARCHAR(255),
                        NO VARCHAR(255),
                        Runs VARCHAR(255),
                        HS VARCHAR(255),
                        Ave VARCHAR(255),
                        BF VARCHAR(255),
                        SR VARCHAR(255),
                        `100` VARCHAR(255),
                        `50` VARCHAR(255),
                        `0` VARCHAR(255),
                        `4s` VARCHAR(255),
                        `6s` VARCHAR(255)
                    );
                '''
                cursor.execute(create_table_query)

                # Insert DataFrame into MySQL table
                for index, row in df.iterrows():
                    insert_query = '''
                    INSERT INTO batting_records (Player, Matches, Inns, NO, Runs, HS, Ave, BF, SR, `100`, `50`, `0`, `4s`, `6s`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    cursor.execute(insert_query, tuple(row))
                    

                # Commit changes
                connection.commit()

        except mysql.connector.Error as error:
            print("Failed to insert DataFrame into MySQL table {}".format(error))

        finally:
            # Close MySQL connection
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def bowling_insert():
        url = "https://www.espncricinfo.com/records/trophy/bowling-most-wickets-career/indian-premier-league-117"

        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")


        table = soup.find('table')
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all(['th', 'td'])
            cols = [col.text.strip() for col in cols]
            data.append(cols)

        # # Create DataFrame
        df = pd.DataFrame(data)
        df = df.drop([1], axis=1)
        df = df.iloc[1:]
        df = df.replace("-", 0)
        
        try:
            connection = mysql.connector.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=database
            )

            if connection.is_connected():
                cursor = connection.cursor()

                # Create table
                create_table_query = '''
                CREATE TABLE IF NOT EXISTS bowling_records (
                        Player VARCHAR(255),
                            Matches VARCHAR(255),
                            Inns VARCHAR(255),
                            Balls VARCHAR(255),
                            Overs VARCHAR(255),
                            Mdns VARCHAR(255),
                            Runs VARCHAR(255),
                            Wkts VARCHAR(255),
                            BBI VARCHAR(255),
                            Ave VARCHAR(255),
                            Econ VARCHAR(255),
                            SR VARCHAR(255),
                            `4` VARCHAR(255),
                            `5` VARCHAR(255)
                    );
                '''
                cursor.execute(create_table_query)

                # Insert DataFrame into MySQL table
                for index, row in df.iterrows():
                    insert_query = '''
                    INSERT INTO bowling_records (Player, Matches, Inns, Balls, Overs, Mdns, Runs, Wkts, BBI, Ave, Econ, SR, `4`, `5`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    cursor.execute(insert_query, tuple(row))
                    

                # Commit changes
                connection.commit()

        except mysql.connector.Error as error:
            print("Failed to insert DataFrame into MySQL table {}".format(error))

        finally:
            # Close MySQL connection
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def schedule_insert():
        url = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = soup.find_all(class_="cb-series-matches")
        date_pattern = r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b)"

        match_insert = []
        for match in matches:
            match_details_element = match.find(class_="cb-srs-mtchs-tm")
            match_details = match_details_element.get_text(strip=True)
            venue = match.find(class_="text-gray").get_text(strip=True)
            match_href = match_details_element.find("a")["href"]
            match_details2 = match_details.split(",")[0]
            match_href = match_href.replace("live-cricket-scores", "live-cricket-scorecard")
            # Extract match result
            result = match.find("a", class_="cb-text-complete")
            if result is not None:
                continue  # Skip this match if result is available (i.e., match has been played)
            
            # Extract match date
            date = re.search(date_pattern, match_details)
            if date:
                match_date = date.group(0)
            else:
                match_date = "Unknown"


            match_info = [match_details2, venue, match_date, match_href]
            match_insert.append(match_info)
        
        try:
            connection = mysql.connector.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=database
            )

            if connection.is_connected():
                cursor = connection.cursor()

                # Create table
                create_table_query = '''
                CREATE TABLE IF NOT EXISTS ipl_schedule (Matches VARCHAR(255),Venue VARCHAR(255),Date VARCHAR(255),Link VARCHAR(255));
                '''
                print(create_table_query)
                cursor.execute(create_table_query)

                for match in match_insert:
                    insert_query = '''
                    INSERT INTO ipl_schedule (Matches, Venue, Date, Link)
                    VALUES (%s, %s, %s, %s)
                    '''
                    cursor.execute(insert_query, tuple(match))
                    
                connection.commit()

        except mysql.connector.Error as error:
            print("Failed to insert DataFrame into MySQL table {}".format(error))

        finally:
            # Close MySQL connection
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    mydatabase = mysql.connector.connect(
        host="localhost",
        user="root",
        password="harsh3304"
    )
    mycursor = mydatabase.cursor()
    command = "CREATE DATABASE IF NOT EXISTS IPL"
    mycursor.execute(command)
    mydatabase.close()

    schedule_insert()
    batting_insert()
    bowling_insert()


first_run = open("./Dependencies/first_run.txt", 'r+')
if first_run.read() == "":
    first_run.write("Done")
    first_run.close()
    first_time_run()
else:
    pass


if start_time <= current_datetime <= end_time :
    print("Its time")
    link = get_link()
    live_match_URL = f"https://www.cricbuzz.com{link}"
    print(live_match_URL)

else:
    print("no time")
    live_match_URL = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches"

def update_match_schedule():
    global live_score
    global Live_Score_Label
    global Schedule_Text
    
    url = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    matches = soup.find_all(class_="cb-series-matches")
    date_pattern = r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b)"

    schedule_text = ""
    for match in matches:
        match_details_element = match.find(class_="cb-srs-mtchs-tm")
        match_details = match_details_element.get_text(strip=True)
        venue = match.find(class_="text-gray").get_text(strip=True)
        match_href = match_details_element.find("a")["href"]
        match_details2 = match_details.split(",")[0]
        
        # Extract match result
        result = match.find("a", class_="cb-text-complete")
        if result is not None:
            continue  # Skip this match if result is available (i.e., match has been played)
        
        # Extract match date
        date = re.search(date_pattern, match_details)
        if date:
            match_date = date.group(0)
        else:
            match_date = "Unknown"

        
        match_info = f"Match Details: {match_details2}\nVenue: {venue}\nMatch Date: {match_date}\n\n"
        schedule_text += match_info
    
    Schedule_Text.insert(END, schedule_text)
    Schedule_Text.configure(state="disabled")  # Insert schedule text into Text widget


def update_live_score():
    global live_score
    global Live_Score_Label
    global live_match_URL
    
    url = live_match_URL

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    details = soup.select('.cb-col .cb-col-100 .cb-scrd-hdr-rw')

    if details:
        pattern = r"(.+?) Innings (\d+-\d+) \((\d+\.?\d*) Ov\)"
        text = details[0].getText().strip()
        match = re.match(pattern, text)

        if match:
            team_name = match.group(1)
            live_score = match.group(2)
            overs = match.group(3)

            # Print the extracted information
            print("Team Name:", team_name)
            print("Score:", live_score)
            print("Overs:", overs)

        display = f"{team_name}\nScore: {live_score}\nOvers: {overs}"
    else:
        live_score = "No match being played currently"
        overs = ""

    Live_Score_Label.config(text=display)
    main_window.after(5000, update_live_score)

def most_wickets():
    try:
        main_window.destroy()
    except:
        pass

    global Most_Wickets_BG_image
    global Most_Wickets_Back_image


    global Most_Wickets_BGLabel

    most_wickets_window = Tk()
    most_wickets_window.title("SixSense --Most Wickets")
    most_wickets_window.geometry('1100x600')
    most_wickets_window.maxsize(1100, 600)
    most_wickets_window.minsize(1100, 600)

    def back():
        most_wickets_window.destroy()
        mainscreen()

    def scrape_bowling_stats():
        url = "https://www.espncricinfo.com/records/tournament/bowling-most-wickets-career/indian-premier-league-2024-15940"

        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find('table')
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all(['th', 'td'])
            cols = [col.text.strip() for col in cols]
            data.append(cols)

        df = pd.DataFrame(data)
        df = df.drop([4,6,7], axis=1)
        return df

    player_stats_df = scrape_bowling_stats()

    Most_Wickets_BG_image = PhotoImage(file= MainScreen_location+"Most_Wickets_BG.png")
    Most_Wickets_Back_image = PhotoImage(file= MainScreen_location+"back_bt.png")

    Most_Wickets_BGLabel = Label(most_wickets_window, image=Most_Wickets_BG_image, bd=0)
    Most_Wickets_BGLabel.place(x=0, y=0)

    back_bt = Button(most_wickets_window, image=Most_Wickets_Back_image, relief=FLAT, bd=0, bg="#B4DBD7", activebackground="#B4DBD7", command=back)
    back_bt.place(x=1000, y=27)

    wrapper1 = LabelFrame(most_wickets_window, width="1500", height="100", background="#4A6161", bd=0)
    mycanvas = Canvas(wrapper1, background="#4A6161", borderwidth=0, highlightthickness=0, width=1000, height=450)
    mycanvas.pack(side=LEFT, expand=False, padx=0)

    mycanvas.bind('<Configure>', lambda e: mycanvas.configure(scrollregion=mycanvas.bbox("all")))
    myframe = Frame(mycanvas)
    myframe.config(bg="#4A6161")
    mycanvas.create_window((0, 0), window=myframe, anchor="n")

    wrapper1.place(x=45, y=132)
   

    # Create table
    table_headers = list(player_stats_df.columns)
    # for col_index, col_name in enumerate(table_headers):
    #     header_label = Label(myframe, text=col_name, background="#4A6161", fg="#F4F9F9", font=("Avenir Next LT Pro Light", 15), bd=1, relief="solid")
    #     header_label.grid(row=0, column=col_index, sticky="nsew")

    # Create columns with weight 1 to allow them to spread evenly
    myframe.grid_columnconfigure(len(table_headers), weight=1)

    for row_index, row_data in enumerate(player_stats_df.values):
        for col_index, cell_data in enumerate(row_data):
            cell_label = Label(myframe, text=cell_data, background="#B4DBD7", fg="#408080", font=("Avenir Next LT Pro Light", 19), bd=1, highlightcolor="#408080", relief="solid")
            cell_label.grid(row=row_index + 1, column=col_index, sticky="nsew")  # Adjust row index to start from 1


    most_wickets_window.mainloop()


def player_stats():
    try:
        main_window.destroy()
    except:
        pass

    global player_stats_BG_image
    global player_stats_Back_image
    global Search_bt_image

    global player_stats_BGLabel

    player_stats_window = Tk()
    player_stats_window.title("SixSense --Player Stats")
    player_stats_window.geometry('1100x600')
    player_stats_window.maxsize(1100, 600)
    player_stats_window.minsize(1100, 600)

    def search_result():
        search = search_name.get()
        try:
            connection = mysql.connector.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=database
            )

            if connection.is_connected():
                cursor = connection.cursor()
                see = f"SELECT * FROM BATTING_RECORDS WHERE Player LIKE \'%{search}%\'"
                cursor.execute(see)
                batting_result = cursor.fetchall()
                
                see = f"SELECT * FROM BOWLING_RECORDS WHERE Player LIKE \'%{search}%\'"
                cursor.execute(see)
                bowling_result = cursor.fetchall()

                if batting_result != [] and bowling_result != []:
                    # return batting_result+bowling_result
                    return pd.DataFrame(batting_result + bowling_result)
                elif batting_result != []:
                    # return batting_result
                    return pd.DataFrame(batting_result)
                elif bowling_result != []:
                    # return bowling_result
                    return pd.DataFrame(bowling_result)
                elif bowling_result == [] and batting_result == []:
                    return None

        except mysql.connector.Error as error:
            print("Failed to insert DataFrame into MySQL table {}".format(error))

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def search():
        wrapper1 = LabelFrame(player_stats_window, width="1000", height="100", background="#B4DBD7", bd=0)
        mycanvas = Canvas(wrapper1, background="#B4DBD7", borderwidth=0, highlightthickness=0, width=1043, height=390)
        mycanvas.pack(side=LEFT, expand=False, padx=0)

        mycanvas.bind('<Configure>', lambda e: mycanvas.configure(scrollregion=mycanvas.bbox("all")))
        myframe = Frame(mycanvas)
        myframe.config(bg="#B4DBD7")
        mycanvas.create_window((0, 0), window=myframe, anchor="n")

        wrapper1.place(x=28, y=190)
        def OnMouseWheel(event):
            mycanvas.yview_scroll(-1 * (int(event.delta / 120)), "units")

            mycanvas.bind_all("<MouseWheel>", OnMouseWheel)
        search_res = search_result()
        print(search_res)
        table_headers = list(search_res.columns)

        myframe.grid_columnconfigure(len(table_headers), weight=1)

        for row_index, row_data in enumerate(search_res.values):
            for col_index, cell_data in enumerate(row_data):
                cell_label = Label(myframe, text=cell_data, background="#B4DBD7", fg="#408080", font=("Avenir Next LT Pro Light", 14), bd=1, highlightcolor="#408080", relief="solid")
                cell_label.grid(row=row_index + 1, column=col_index, sticky="nsew")


    def back():
        player_stats_window.destroy()
        mainscreen()

    player_stats_BG_image = PhotoImage(file= MainScreen_location+"player_stats_BG.png")
    player_stats_Back_image = PhotoImage(file= MainScreen_location+"back_bt.png")
    Search_bt_image = PhotoImage(file= MainScreen_location+"search_bt.png")

    player_stats_BGLabel = Label(player_stats_window, image=player_stats_BG_image, bd=0)
    player_stats_BGLabel.place(x=0, y=0)

    search_name = Entry(player_stats_window,  relief=FLAT, width="52", font=("Century Gothic", 22), foreground="#B4DBD7", background="#5EA3A2")
    search_name.place(x=45, y=138)

    submit_button = Button(player_stats_window, relief = FLAT, image= Search_bt_image, bg="#B4DBD7", bd=0, activebackground="#B4DBD7", command=search)
    submit_button.place(x=948, y=136)

    back_bt = Button(player_stats_window, relief = FLAT, image=player_stats_Back_image, bd=0, bg="#B4DBD7", activebackground="#B4DBD7", command=back)
    back_bt.place(x=1000, y=27)


def standings():
    try:
        main_window.destroy()
    except:
        pass

    global standings_BG_image
    global standings_Back_image


    global standings_BGLabel

    standings_window = Tk()
    standings_window.title("SixSense --Standings")
    standings_window.geometry('1100x600')
    standings_window.maxsize(1100, 600)
    standings_window.minsize(1100, 600)

    def back():
        standings_window.destroy()
        mainscreen()

    def scrape_points_table():
        url = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/points-table"
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")


        table = soup.find('table')
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all(['th', 'td'])
            cols = [col.text.strip() for col in cols]
            if len(cols) == 9:
                cols = cols[0:8]    
                data.append(cols)
        
        return pd.DataFrame(data)

    points_table_df = scrape_points_table()

    standings_BG_image = PhotoImage(file= MainScreen_location+"Standings_BG.png")
    standings_Back_image = PhotoImage(file= MainScreen_location+"back_bt.png")

    standings_BGLabel = Label(standings_window, image=standings_BG_image, bd=0)
    standings_BGLabel.place(x=0, y=0)

    back_bt = Button(standings_window, image=standings_Back_image, relief=FLAT, bd=0, bg="#B4DBD7", activebackground="#B4DBD7", command=back)
    back_bt.place(x=1000, y=27)

    wrapper1 = LabelFrame(standings_window, width="1000", height="100", background="#4A6161", bd=0)
    mycanvas = Canvas(wrapper1, background="#4A6161", borderwidth=0, highlightthickness=0, width=704, height=353)
    mycanvas.pack(side=LEFT, expand=False, padx=0)

    mycanvas.bind('<Configure>', lambda e: mycanvas.configure(scrollregion=mycanvas.bbox("all")))
    myframe = Frame(mycanvas)
    myframe.config(bg="#4A6161")
    mycanvas.create_window((0, 0), window=myframe, anchor="n")

    wrapper1.place(x=190, y=168)
    def OnMouseWheel(event):
        mycanvas.yview_scroll(-1 * (int(event.delta / 120)), "units")

        mycanvas.bind_all("<MouseWheel>", OnMouseWheel)
    
    # Create table
    table_headers = list(points_table_df.columns)
    # for col_index, col_name in enumerate(table_headers):
    #     header_label = Label(myframe, text=col_name, background="#4A6161", fg="#F4F9F9", font=("Avenir Next LT Pro Light", 15), bd=1, relief="solid")
    #     header_label.grid(row=0, column=col_index, sticky="nsew")

    # Create columns with weight 1 to allow them to spread evenly
    myframe.grid_columnconfigure(len(table_headers), weight=1)

    for row_index, row_data in enumerate(points_table_df.values):
        for col_index, cell_data in enumerate(row_data):
            cell_label = Label(myframe, text=cell_data, background="#B4DBD7", fg="#408080", font=("Avenir Next LT Pro Light", 19), bd=1, highlightcolor="#408080", relief="solid")
            cell_label.grid(row=row_index + 1, column=col_index, sticky="nsew")  # Adjust row index to start from 1

    standings_window.mainloop()


def scrape_player_stats():
        url = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/stats"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find('table', class_='cb-series-stats')
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all(['th', 'td'])
            cols = [col.text.strip() for col in cols]
            data.append(cols)

        return pd.DataFrame(data)


def most_runs():
    try:
        main_window.destroy()
    except:
        pass

    def back():
        most_runs_window.destroy()
        mainscreen()

    def scrape_player_stats():
        url = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/stats"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find('table', class_='cb-series-stats')
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all(['th', 'td'])
            cols = [col.text.strip() for col in cols]
            data.append(cols)

        return pd.DataFrame(data)

    player_stats_df = scrape_player_stats()

    most_runs_window = Tk()
    most_runs_window.title("SixSense --Most Runs")
    most_runs_window.geometry('1100x600')
    most_runs_window.maxsize(1100, 600)
    most_runs_window.minsize(1100, 600)

    def back():
        most_runs_window.destroy()
        mainscreen()

    most_runs_BG_image = PhotoImage(file= MainScreen_location+"most_runs_BG.png")
    most_runs_Back_image = PhotoImage(file= MainScreen_location+"back_bt.png")

    most_runs_BGLabel = Label(most_runs_window, image=most_runs_BG_image, bd=0)
    most_runs_BGLabel.place(x=0, y=0)

    back_bt = Button(most_runs_window, image=most_runs_Back_image, relief=FLAT, bd=0, bg="#B4DBD7", activebackground="#B4DBD7", command=back)
    back_bt.place(x=1000, y=27)

    style = ttk.Style()
    style.theme_use('clam')

    wrapper1 = LabelFrame(most_runs_window, width="1000", height="100", background="#4A6161", bd=0)
    mycanvas = Canvas(wrapper1, background="#4A6161", borderwidth=0, highlightthickness=0, width=655, height=448)
    mycanvas.pack(side=LEFT, expand=False, padx=0)

    mycanvas.bind('<Configure>', lambda e: mycanvas.configure(scrollregion=mycanvas.bbox("all")))
    myframe = Frame(mycanvas)
    myframe.config(bg="#4A6161")
    mycanvas.create_window((0, 0), window=myframe, anchor="n")

    wrapper1.place(x=210, y=136)
    def OnMouseWheel(event):
        mycanvas.yview_scroll(-1 * (int(event.delta / 120)), "units")

        mycanvas.bind_all("<MouseWheel>", OnMouseWheel)

    # Create table
    table_headers = list(player_stats_df.columns)
    # for col_index, col_name in enumerate(table_headers):
    #     header_label = Label(myframe, text=col_name, background="#4A6161", fg="#F4F9F9", font=("Avenir Next LT Pro Light", 15), bd=1, relief="solid")
    #     header_label.grid(row=0, column=col_index, sticky="nsew")

    # Create columns with weight 1 to allow them to spread evenly
    myframe.grid_columnconfigure(len(table_headers), weight=1)

    for row_index, row_data in enumerate(player_stats_df.values):
        for col_index, cell_data in enumerate(row_data):
            cell_label = Label(myframe, text=cell_data, background="#B4DBD7", fg="#408080", font=("Avenir Next LT Pro Light", 19), bd=1, highlightcolor="#408080", relief="solid")
            cell_label.grid(row=row_index + 1, column=col_index, sticky="nsew")  # Adjust row index to start from 1
    most_runs_window.mainloop()

   
def mainscreen():
    global main_window
    global Main_BG_image
    global Most_Runs_bt_image
    global Most_Wickets_bt_image
    global Player_Stats_bt_image
    global Standings_bt_image
    global Live_Score_Label
    global Schedule_Text
    global Most_Wickets_bt
    global Player_Stats_bt
    global Standings_bt
    global Most_Runs_bt

    main_window = Tk()
    main_window.title("SixSense")
    main_window.geometry('1100x600')
    main_window.maxsize(1100, 600)
    main_window.minsize(1100, 600)

    Main_BG_image = PhotoImage(file= MainScreen_location+"Main_BG.png")
    Most_Runs_bt_image = PhotoImage(file= MainScreen_location+"Most_Runs_bt.png")
    Most_Wickets_bt_image = PhotoImage(file= MainScreen_location+"Most_Wickets_bt.png")
    Player_Stats_bt_image = PhotoImage(file= MainScreen_location+"Player_Stats_bt.png")
    Standings_bt_image = PhotoImage(file= MainScreen_location+"Standings_bt.png")

    Main_BGLabel = Label(main_window, image=Main_BG_image, bd=0)
    Main_BGLabel.place(x=0, y=0)

    Live_Score_Label = Label(main_window, text="", background="#408080", fg="#F4F9F9",font=("Avenir Next LT Pro Light", 21))
    Live_Score_Label.place(x=40, y=200)

    scrollbar = Scrollbar(main_window)
    scrollbar.pack(side=RIGHT, fill=Y)

    Schedule_Text = Text(main_window, relief=FLAT, background="#4A6161", fg="#F4F9F9",font=("Avenir Next LT Pro Light", 9, 'bold'), wrap=WORD, yscrollcommand=scrollbar.set)
    Schedule_Text.place(x=712, y=190, width=340, height=372)

    Most_Wickets_bt = Button(main_window,image=Most_Wickets_bt_image, relief=FLAT, bd=0, bg="#B4DBD7", activebackground="#B4DBD7", command=most_wickets)
    Most_Wickets_bt.place(x=480, y=142)

    Player_Stats_bt = Button(main_window,image=Player_Stats_bt_image, relief=FLAT, bd=0, bg="#B4DBD7", activebackground="#B4DBD7", command=player_stats)
    Player_Stats_bt.place(x=30, y=366)

    Standings_bt = Button(main_window,image=Standings_bt_image, relief=FLAT, bd=0, bg="#B4DBD7", activebackground="#B4DBD7", command=standings)
    Standings_bt.place(x=255, y=366)

    Most_Runs_bt = Button(main_window,image=Most_Runs_bt_image, relief=FLAT, bd=0, bg="#B4DBD7", activebackground="#B4DBD7", command=most_runs)
    Most_Runs_bt.place(x=480, y=366)

    update_match_schedule() 
    if start_time <= current_datetime <= end_time:
        update_live_score() 
    else:
        Live_Score_Label.config(text="No match being played currently")
    main_window.mainloop()


mainscreen()
mainloop()
