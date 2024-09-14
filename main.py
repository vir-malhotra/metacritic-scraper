import requests
from bs4 import BeautifulSoup
import time
import matplotlib.pyplot as plt

def scrape_metacritic_new_releases(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.metacritic.com/',  # Mimic coming from the homepage
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }
    
    # Send request to the page
    response = requests.get(url, headers=headers)
    
    if response.status_code == 403:
        print("Access forbidden (403). The site might be blocking your IP or user-agent.")
        return None
    elif response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # List to store the scraped data
    albums = []
    
    # Find all album entries (using <td> with class "clamp-summary-wrap")
    album_entries = soup.find_all('td', class_='clamp-summary-wrap')
    
    print(f"Found {len(album_entries)} album entries.")  # Print how many album entries found
    
    # Limit to top 10 albums
    for entry in album_entries[:10]:  # Limiting to the first 10 albums
        # Extract album title (from <h3> inside <a class="title">)
        album_title_tag = entry.find('a', class_='title')
        album_title = album_title_tag.find('h3').text.strip() if album_title_tag else "Unknown Album"
        
        # Extract artist name
        artist_name_tag = entry.find('div', class_='artist')
        artist_name = artist_name_tag.text.strip().replace('by ', '') if artist_name_tag else "Unknown Artist"
        
        # Extract release date
        release_date_tag = entry.find('div', class_='clamp-details').find('span')
        release_date = release_date_tag.text.strip() if release_date_tag else "Unknown Date"
        
        # Extract metascore (inside 'clamp-metascore')
        metascore_tag = entry.find('div', class_='clamp-metascore').find('div', class_='metascore_w')
        metascore = metascore_tag.text.strip() if metascore_tag else "No Metascore"
        
        # Extract user score (inside 'clamp-userscore')
        user_score_tag = entry.find('div', class_='clamp-userscore').find('div', class_='metascore_w')
        user_score = user_score_tag.text.strip() if user_score_tag else "tbd"

        # Extract album summary
        summary_tag = entry.find('div', class_='summary')
        summary = summary_tag.text.strip() if summary_tag else "No summary available"
        
        # Extract album link
        album_link_tag = album_title_tag['href'] if album_title_tag else "#"
        album_link = f"https://www.metacritic.com{album_link_tag}"

        # Store the scraped data
        albums.append({
            'album_title': album_title,
            'artist_name': artist_name,
            'release_date': release_date,
            'metascore': metascore,
            'user_score': user_score,
            'summary': summary,
            'link': album_link
        })
    
    return albums

# URL to scrape
url = 'https://www.metacritic.com/browse/albums/release-date/available/metascore'

def plot_user_scores(albums):
    album_titles = [album['album_title'] for album in albums]
    user_scores = []
    
    for album in albums:
        # Handle "tbd" user scores and convert to float
        try:
            user_scores.append(float(album['user_score']))
        except ValueError:
            user_scores.append(0)  # If user score is "tbd", set it to 0 for visualization
    
    # Set the figure size and adjust layout for long album titles
    plt.figure(figsize=(10, 6))
    
    # Plot the bar chart
    plt.barh(album_titles, user_scores, color='lightcoral')
    
    # Set labels and title
    plt.xlabel('User Score')
    plt.title('User Scores of Top 10 Albums')
    
    # Invert y-axis to show the top album at the top
    plt.gca().invert_yaxis()
    
    # Adjust the layout to prevent album titles from overlapping outside the plot
    plt.tight_layout()
    
    # Display the plot
    plt.show()

# Step 4: Simple Data Analysis
def analyze_data(albums):
    total_metascore = 0
    total_user_score = 0
    count_metascore = 0
    count_user_score = 0
    user_score_tbd = 0
    
    for album in albums:
        # Metascore calculation
        try:
            total_metascore += int(album['metascore'])
            count_metascore += 1
        except ValueError:
            continue
        
        # User score calculation
        if album['user_score'] != 'tbd':
            total_user_score += float(album['user_score'])
            count_user_score += 1
        else:
            user_score_tbd += 1
    
    avg_metascore = total_metascore / count_metascore if count_metascore > 0 else 0
    avg_user_score = total_user_score / count_user_score if count_user_score > 0 else 0
    
    print(f"Average Metascore: {avg_metascore:.2f}")
    print(f"Average User Score (excluding 'tbd'): {avg_user_score:.2f}")
    print(f"Albums with 'tbd' user scores: {user_score_tbd} out of {len(albums)}")

# Implement rate limiting and error handling
def scrape_with_rate_limit(url, delay=5):
    print("Scraping URL:", url)
    album_data = scrape_metacritic_new_releases(url)
    
    if album_data:
        for idx, album in enumerate(album_data, 1):
            print(f"{idx}. Album: {album['album_title']}, Artist: {album['artist_name']}, Release Date: {album['release_date']}")
            print(f"   Metascore: {album['metascore']}, User Score: {album['user_score']}")
            print(f"   Summary: {album['summary']}")
            print(f"   Link: {album['link']}")
            print("-" * 80)  # Separator between entries
    else:
        print("No data found.")
    
    print(f"Sleeping for {delay} seconds...")
    time.sleep(delay)  # Wait for `delay` seconds before the next request
    plot_user_scores(album_data)
    analyze_data(album_data)




# Example usage with rate limiting
scrape_with_rate_limit(url, delay=5)
