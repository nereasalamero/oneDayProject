import flet as ft
import requests

TMDB_API_KEY = "ecf6cd370743e8905b3d7440dc3527cc"  # Replace with your TMDb API key
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/multi" #Defining the URL Key for each pages


def search_multi(query):
    response = requests.get(
        TMDB_SEARCH_URL,
        params={"api_key": TMDB_API_KEY, "query": query, "language": "en-US"},
    )
    if response.status_code == 200:
        return response.json().get("results", [])
    return []


def main(page: ft.Page):
    page.title = "Movie/TV Show Search"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20

    def on_search(e):
        query = search_input.value.strip()
        if not query:
            results_container.controls.clear()
            results_container.update()
            return

        results = search_multi(query)
        results_container.controls.clear()

        if results:
            for result in results:
                title = result.get("title") or result.get("name", "Unknown Title")
                overview = result.get("overview", "No description available.")
                poster_path = result.get("poster_path")
                poster_url = (
                    f"https://image.tmdb.org/t/p/w200{poster_path}"
                    if poster_path
                    else None
                )

                result_card = ft.Row(
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
                                ft.Text(overview, max_lines=4, overflow="ellipsis"),
                            ],
                            expand=True,
                        ),
                    ],
                    spacing=10,
                )
                results_container.controls.append(result_card)
        else:
            results_container.controls.append(ft.Text("No results found."))

        results_container.update()

    search_input = ft.TextField(label="Search Movie/TV Show", expand=True)
    search_button = ft.ElevatedButton("Search", on_click=on_search)
    results_container = ft.Column()

    page.add(
        ft.Row([search_input, search_button], spacing=10),
        results_container,
    )


ft.app(target=main)
