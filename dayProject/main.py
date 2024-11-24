import flet as ft
import requests

# Defining the API key and URL links
TMDB_API_KEY = "ecf6cd370743e8905b3d7440dc3527cc"
TMDB_SEARCH_URL_MULTI = "https://api.themoviedb.org/3/search/multi"
TMDB_SEARCH_URL_MOVIES = "https://api.themoviedb.org/3/search/movie"
TMDB_SEARCH_URL_TVSHOWS = "https://api.themoviedb.org/3/search/tv"
TMDB_DETAIL_URL_MOVIE = "https://api.themoviedb.org/3/movie"
TMDB_DETAIL_URL_TVSHOW = "https://api.themoviedb.org/3/tv"
TMDB_TOP_RATED_MOVIES = "https://api.themoviedb.org/3/trending/all/day"

# Function to choose the URL based on search type
def choose_url(route):
    if route == "Movies":
        return TMDB_SEARCH_URL_MOVIES
    elif route == "TV Shows":
        return TMDB_SEARCH_URL_TVSHOWS
    return TMDB_SEARCH_URL_MULTI

# Function to get details of a movie or TV show
def get_details(item_id, route):
    url = TMDB_DETAIL_URL_MOVIE if route == "Movies" else TMDB_DETAIL_URL_TVSHOW
    response = requests.get(f"{url}/{item_id}", params={"api_key": TMDB_API_KEY, "language": "en-US"})
    if response.status_code == 200:
        return response.json()
    return None


# Function to fetch trending movies and TV shows
def fetch_trending():
    response = requests.get(TMDB_TOP_RATED_MOVIES, params={"api_key": TMDB_API_KEY, "language": "en-US"})
    if response.status_code == 200:
        return response.json().get("results", [])
    return []


# Function to perform the search
def search(query, route):
    response = requests.get(
        choose_url(route),
        params={"api_key": TMDB_API_KEY, "query": query, "language": "en-US"},
    )
    if response.status_code == 200:
        return response.json().get("results", [])
    return []

# Main layout
def main(page: ft.Page):
    page.title = "Movie / TV Show Search App"
    page.bgcolor = "#E5FFC0"
    page.padding = 20
    last_category = "All"

    # Create search input and button
    search_input = ft.TextField(label="Search Movie/TV Show", expand=True)
    search_button = ft.ElevatedButton("Search", on_click=lambda e: on_search("All"))

    # Results container
    results_container = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10, height=450)

    # Function to display trending results on the main page
    def show_trending():
        trending_items = fetch_trending()
        results_container.controls.clear()

        for item in trending_items:
            title = item.get("title") or item.get("name", "No Title Available")
            overview = item.get("overview", "No description available.")
            poster_path = item.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w200{poster_path}" if poster_path else None

            result_card = ft.Container(
                content=ft.Row(
                    [
                        ft.Image(
                            src=poster_url,
                            width=100,
                            height=150,
                            fit="cover",
                        ) if poster_url else ft.Container(width=100, height=150, bgcolor="gray"),
                        ft.Column(
                            [
                                ft.Text(title, weight="bold", size=16),
                                ft.Text(f"Rating: {item.get('vote_average', 'N/A'):.1f}/10", size=14),
                                ft.Text(overview, max_lines=4, overflow="ellipsis"),
                            ],
                            expand=True,
                        ),
                    ],
                    spacing=10,
                )
            )
            results_container.controls.append(result_card)
        results_container.update()

    # Function to search and display results
    def on_search(route):
        nonlocal last_category
        query = search_input.value.strip()
        last_category = route
        if not query:
            show_trending()
            results_container.controls.clear()
            results_container.update()
            return

        # Get the results from the API
        results = search(query, route)
        results_container.controls.clear()

        if results:
            # Filter results by the first letter
            first_letter = query[0].upper()  # Extract the first letter of the query

            # Filter results to include only those that start with the first letter
            filtered_results = [result for result in results if result.get("title", "").upper().startswith(first_letter) or result.get("name", "").upper().startswith(first_letter)]

            # Sort the results by rating in descending order
            sorted_results = sorted(filtered_results, key=lambda x: x.get("vote_average", 0), reverse=True)

            # Create result cards for each sorted result
            for result in sorted_results:
                title = result.get("title") or result.get("name", "No Title Available")
                overview = result.get("overview", "No description available.")
                poster_path = result.get("poster_path")
                poster_url = (
                    f"https://image.tmdb.org/t/p/w200{poster_path}"
                    if poster_path
                    else None
                )

                # Determine if it's a movie or TV show
                is_movie = 'title' in result
                route = "Movies" if is_movie else "TV Shows"

                # Result card with click event handler using GestureDetector
                def on_click_card(e, item_id, route):
                    # Get details of the selected movie/TV show
                    details = get_details(item_id, route)
                    if details:
                        show_details(details)
                    page.remove(search_button)
                    page.remove(search_input)
                    page.add(ft.ElevatedButton("Back", on_click=lambda e: main(page)))

                result_card = ft.Container(content=
                    ft.GestureDetector(
                        on_tap=lambda e, item_id=result["id"], route=route: on_click_card(e, item_id, route),
                        content=ft.Row(
                            [
                                ft.Image(
                                    src=poster_url,
                                    width=100,
                                    height=150,
                                    fit="cover",
                                ) if poster_url else ft.Container(width=100, height=150, bgcolor="gray"),
                                ft.Column(
                                    [
                                        ft.Text(title, weight="bold", size=16),
                                        ft.Text(f"Rating: {result.get('vote_average', 'N/A'):.1f}/10", size=14),
                                        ft.Text(overview, max_lines=4, overflow="ellipsis"),
                                    ],
                                    expand=True,
                                ),
                            ],
                            spacing=10,
                        )
                    ),
                )
                results_container.controls.append(result_card)
        else:
            results_container.controls.append(ft.Text("No results found."))

        results_container.update()
    
    # Function to display detailed information
    def show_details(details):
        title = details.get("title") or details.get("name", "No Title Available")
        genres = ", ".join([genre["name"] for genre in details.get("genres", [])])
        rating = details.get("vote_average", "N/A")
        overview = details.get("overview", "No description available.")
        poster_path = details.get("poster_path")
        poster_url = (
            f"https://image.tmdb.org/t/p/w200{poster_path}"
            if poster_path
            else None
        )
        
        # Display details in a new column or replace existing content
        details_column = ft.Column(
            controls=[
                ft.Row([
                    ft.Column([ # Title and image of the movie/tv show
                        ft.Text(title, weight="bold", size=18),
                        ft.Image(src=poster_url, width=100, height=150, fit="cover"),],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                ft.Row([
                    ft.Text("Genres:", weight="bold", size=16),
                    ft.Text(f"{genres}", size=14),
                ],
                    expand=True,
                ),
                ft.Row([
                    ft.Text("Rating:", weight="bold", size=16),
                    ft.Text(f"{rating:.1f}/10", size=14),
                ],expand=True,),
                ft.Row([
                    ft.Text("Description:", weight="bold", size=16),
                    ft.Text(f"{overview}", size=14, width=1000),
                ],expand=True,),
                ft.ElevatedButton("Back", on_click=lambda e: on_search(f"{last_category}")),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # Clear the previous results and show details
        results_container.controls.clear()
        results_container.controls.append(details_column)
        results_container.update()

    # Button to switch between search categories
    def on_category_change(category):
        on_search(category)

    # Create buttons for switching between "All", "Movies", and "TV Shows"
    all_button = ft.ElevatedButton("All", on_click=lambda e: on_category_change("All"))
    movies_button = ft.ElevatedButton("Movies", on_click=lambda e: on_category_change("Movies"))
    tvshows_button = ft.ElevatedButton("TV Shows", on_click=lambda e: on_category_change("TV Shows"))


    # Set up the layout of the page
    page.add(
        ft.Column(
            [
                ft.Row([all_button, movies_button, tvshows_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([search_input, search_button], spacing=10),
                results_container,
            ]
        ),
    )
    show_trending()
ft.app(target=main, view=ft.AppView.WEB_BROWSER)
