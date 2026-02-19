import os 
import pandas as pd
import sqlite3
import matplotlib as matplot
import matplotlib.pyplot as plt
path = r"C:\Users\Charl\Downloads\Apple Media Services Information Part 1 of 2(1)\Apple Media Services Information Part 1 of 2\Apple_Media_Services\Apple_Media_Services\Apple Music Activity"

#found that Apple Music Play Activity.csv is the one with the most useful and full features 
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
df=pd.read_csv(rf"{path}\Apple Music Play Activity.csv")
print(df.head().T)

#You can see we have a lot of columns so we need to get rid of useless ones based on systematic rules 
nulls = df.isna().mean().sort_values(ascending=False)
unique = df.nunique().sort_values()

# Step 1 — identify columns to drop // drop  where: null percentage is greater than or equal to 90% and where there is only no or 1 unique value
drop_cols = nulls[(nulls >= 0.9) | (unique == 0) | (unique == 1)].index

# Step 2 — drop them
newdf = df.drop(columns=drop_cols)

# Drop all columns that have keywords in their name
keywords_to_drop = ["Milliseconds Since Play","Event Received Timestamp","Event Timestamp","Event Post Date","Evaluation Variant","Source Type","ID", "Client","Version","Device","Offline","IP","User's","Provided","Siri","Display","Use Listening", "Subscription", "Session Is", "Personalized","Ownership","Media Type","Media Bundle","Item Type","Vocal","Event Reason Hint","Repeat Play" ]
newdf = newdf.drop(columns=[col for col in newdf.columns if any(k in col for k in keywords_to_drop)])

#drop rows with no song name 
newdf = newdf.dropna(subset=["Song Name"])

# --- Convert timestamps to datetime objects ---
newdf['Event Start Timestamp'] = pd.to_datetime(newdf['Event Start Timestamp'], utc=True, format="ISO8601")
newdf['Event End Timestamp'] = pd.to_datetime(newdf['Event End Timestamp'], utc=True, format="ISO8601")

# --- Convert durations to seconds ---
newdf['Media Duration Sec'] = newdf['Media Duration In Milliseconds'] / 1000
newdf['Play Duration Sec'] = newdf['Play Duration Milliseconds'] / 1000
newdf['Start Position Sec'] = newdf['Start Position In Milliseconds'] / 1000
newdf['End Position Sec'] = newdf['End Position In Milliseconds'] / 1000

# --- Calculate percent of song played ---
newdf['Percent Played'] = newdf['Play Duration Sec'] / newdf['Media Duration Sec']

# --- Extract hour of day and day of week from start timestamp ---
newdf['Hour of Day'] = newdf['Event Start Timestamp'].dt.hour
newdf['Day of Week'] = newdf['Event Start Timestamp'].dt.day_name()

# Optional: flag skipped vs finished (e.g., <80% = skipped)
newdf['Skipped'] = newdf['Percent Played'] < 0.8

newdf = newdf.drop(columns=[col for col in newdf.columns if any(k in col for k in ["Milliseconds"])])

print(newdf.info())
conn = sqlite3.connect("data.db")
newdf.to_sql("editedMusicData", conn, if_exists="replace", index=False)
conn.close()