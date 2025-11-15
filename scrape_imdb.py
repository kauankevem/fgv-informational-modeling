import sys
from tqdm import tqdm
import os
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
from dataclasses import dataclass

DATA_PATH = "data"

movies_to_scrape = [
    # Clássicos Aclamados e Vencedores do Oscar
    "tt0111161",  # The Shawshank Redemption (Um Sonho de Liberdade)
    "tt0068646",  # The Godfather (O Poderoso Chefão)
    "tt0071562",  # The Godfather Part II (O Poderoso Chefão: Parte II)
    "tt0468569",  # The Dark Knight (Batman: O Cavaleiro das Trevas)
    "tt0050083",  # 12 Angry Men (12 Homens e uma Sentença)
    "tt0108052",  # Schindler's List (A Lista de Schindler)
    "tt0167260",  # The Lord of the Rings: The Return of the King (O Senhor dos Anéis: O Retorno do Rei)
    "tt0110912",  # Pulp Fiction (Pulp Fiction: Tempo de Violência)
    "tt0060196",  # The Good, the Bad and the Ugly (Três Homens em Conflito)
    "tt0109830",  # Forrest Gump (Forrest Gump: O Contador de Histórias)
    "tt0038650",  # It's a Wonderful Life (A Felicidade Não Se Compra)
    "tt0047478",  # Seven Samurai (Os Sete Samurais)
    "tt0099685",  # Goodfellas (Os Bons Companheiros)
    "tt0080684",  # Star Wars: Episode V - The Empire Strikes Back (Star Wars: Episódio V - O Império Contra-Ataca)
    "tt0073486",  # One Flew Over the Cuckoo's Nest (Um Estranho no Ninho)
    "tt0027977",  # Modern Times (Tempos Modernos)
    "tt0043014",  # Sunset Boulevard (Crepúsculo dos Deuses)
    "tt0034583",  # Casablanca (Casablanca)
    "tt0021749",  # City Lights (Luzes da Cidade)
    "tt0056058",  # Lawrence of Arabia (Lawrence da Arábia)
    # Blockbusters e Franquias Populares
    "tt0076759",  # Star Wars: Episode IV - A New Hope (Star Wars: Episódio IV - Uma Nova Esperança)
    "tt0120737",  # The Lord of the Rings: The Fellowship of the Ring (O Senhor dos Anéis: A Sociedade do Anel)
    "tt0103064",  # Terminator 2: Judgment Day (O Exterminador do Futuro 2: O Julgamento Final)
    "tt0088763",  # Back to the Future (De Volta para o Futuro)
    "tt0107290",  # Jurassic Park (Jurassic Park: O Parque dos Dinossauros)
    "tt0133093",  # The Matrix (Matrix)
    "tt0816692",  # Interstellar (Interestelar)
    "tt1375666",  # Inception (A Origem)
    "tt0993846",  # The Wolf of Wall Street (O Lobo de Wall Street)
    "tt0114369",  # Se7en (Seven: Os Sete Crimes Capitais)
    "tt0137523",  # Fight Club (Clube da Luta)
    "tt0120815",  # Saving Private Ryan (O Resgate do Soldado Ryan)
    "tt0114814",  # The Usual Suspects (Os Suspeitos)
    "tt0082971",  # Raiders of the Lost Ark (Os Caçadores da Arca Perdida)
    "tt0120382",  # The Truman Show (O Show de Truman)
    "tt0102926",  # The Silence of the Lambs (O Silêncio dos Inocentes)
    "tt0083658",  # Blade Runner (Blade Runner, o Caçador de Androides)
    "tt0062622",  # 2001: A Space Odyssey (2001: Uma Odisseia no Espaço)
    "tt0045152",  # Singin' in the Rain (Cantando na Chuva)
    "tt0033467",  # Citizen Kane (Cidadão Kane)
    # Animações e Filmes para a Família
    "tt0110357",  # The Lion King (O Rei Leão)
    "tt0245429",  # Spirited Away (A Viagem de Chihiro)
    "tt0095327",  # Grave of the Fireflies (O Túmulo dos Vagalumes)
    "tt0435761",  # Toy Story 3 (Toy Story 3)
    "tt0111095",  # The Professional (O Profissional)
    "tt0317248",  # City of God (Cidade de Deus)
    "tt0054215",  # Psycho (Psicose)
    "tt0118799",  # Life Is Beautiful (A Vida é Bela)
    "tt0078748",  # Alien (Alien, o Oitavo Passageiro)
    "tt0082096",  # The Shining (O Iluminado)
]

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.7",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "referer": "https://search.brave.com/",
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Brave";v="140"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
}


@dataclass
class Genre:
    id: str
    name: str


@dataclass
class ProductionCompany:
    id: str
    name: str


@dataclass
class Person:
    id: str
    name: str
    img_url: str | None = None


@dataclass
class Movie:
    id: str
    name: str
    duration: int
    release_year: int
    rating: float
    rating_count: int
    genres: list[Genre]
    production_companies: list[ProductionCompany]
    img_url: str | None = None
    directors: list[Person] = None
    actors: list[Person] = None
    similar_movies: list[str] = None


def get_movie_data(movie_id: str) -> dict:
    response = requests.get(f"https://www.imdb.com/title/{movie_id}/", headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    raw_data = json.loads(
        soup.find("script", {"type": "application/json", "id": "__NEXT_DATA__"}).text
    )
    data = {
        "id": movie_id,
        "name": raw_data["props"]["pageProps"]["aboveTheFoldData"]["titleText"]["text"],
        "duration": raw_data["props"]["pageProps"]["aboveTheFoldData"]["runtime"][
            "seconds"
        ]
        // 60,
        "release_year": raw_data["props"]["pageProps"]["aboveTheFoldData"][
            "releaseDate"
        ]["year"],
        "rating": raw_data["props"]["pageProps"]["aboveTheFoldData"]["ratingsSummary"][
            "aggregateRating"
        ],
        "rating_count": raw_data["props"]["pageProps"]["aboveTheFoldData"][
            "ratingsSummary"
        ]["voteCount"],
        "genres": [
            {"name": x["genre"]["text"]}
            for x in raw_data["props"]["pageProps"]["aboveTheFoldData"]["titleGenres"][
                "genres"
            ]
        ],
        "production_companies": [
            {
                "id": x["node"]["company"]["id"],
                "name": x["node"]["company"]["companyText"]["text"],
            }
            for x in raw_data["props"]["pageProps"]["aboveTheFoldData"]["production"][
                "edges"
            ]
        ],
        "img_url": raw_data["props"]["pageProps"]["aboveTheFoldData"]["primaryImage"][
            "url"
        ],
        "directors": [
            {"id": y["name"]["id"], "name": y["name"]["nameText"]["text"]}
            for y in [
                x["credits"]
                for x in raw_data["props"]["pageProps"]["aboveTheFoldData"]["principalCredits"]
                if "Director" in x["category"]["text"]
            ][0]
        ],
        "actors": [
            {
                "id": x["node"]["name"]["id"],
                "name": x["node"]["name"]["nameText"]["text"],
            }
            for x in raw_data["props"]["pageProps"]["mainColumnData"]["cast"]["edges"]
        ],
        "similar_movies": [
            x["node"]["id"]
            for x in raw_data["props"]["pageProps"]["mainColumnData"][
                "moreLikeThisTitles"
            ]["edges"]
        ],
    }

    return data


def load_data() -> dict[str, pd.DataFrame]:
    if not os.path.exists(os.path.join(DATA_PATH, "movies.parquet")):
        return {
            "movies": pd.DataFrame(
                columns=[
                    "id",
                    "name",
                    "duration",
                    "release_year",
                    "rating",
                    "rating_count",
                    "genres",
                    "production_companies",
                    "img_url",
                    "directors",
                    "actors",
                    "similar_movies",
                ]
            ).set_index("id"),
            "people": pd.DataFrame(columns=["id", "name", "img_url"]).set_index("id"),
            "companies": pd.DataFrame(columns=["id", "name"]).set_index("id"),
            "genres": pd.DataFrame(columns=["id", "name"]).set_index("id"),
        }
    return {
        "movies": pd.read_parquet(os.path.join(DATA_PATH, "movies.parquet")).set_index("id"),
        "people": pd.read_parquet(os.path.join(DATA_PATH, "people.parquet")).set_index("id"),
        "companies": pd.read_parquet(os.path.join(DATA_PATH, "companies.parquet")).set_index("id"),
        "genres": pd.read_parquet(os.path.join(DATA_PATH, "genres.parquet")).set_index("id"),
    }


def save_data(data: dict[str, pd.DataFrame]) -> None:
    os.makedirs(DATA_PATH, exist_ok=True)
    for name, df in data.items():
        df.reset_index().to_parquet(os.path.join(DATA_PATH, f"{name}.parquet"), index=False)


def append_data(data: dict[str, pd.DataFrame], movie_data: dict) -> None:
    # Genres
    new_genres = pd.DataFrame(movie_data["genres"])
    new_genres["id"] = new_genres["name"].apply(lambda x: x.lower())
    new_genres = new_genres.set_index("id")
    if data['genres'].empty:
        data['genres'] = new_genres
    else:
        data["genres"] = pd.concat([data["genres"], new_genres]).drop_duplicates()
    movie_genres = new_genres.index

    # Companies
    new_companies = pd.DataFrame(movie_data["production_companies"]).set_index("id")
    if data['companies'].empty:
        data['companies'] = new_companies
    else:
        data["companies"] = pd.concat([data["companies"], new_companies]).drop_duplicates()
    movie_companies = new_companies.index

    # People
    new_people = pd.DataFrame(movie_data["directors"] + movie_data["actors"]).set_index("id")
    if data['people'].empty:
        data['people'] = new_people
    else:
        data["people"] = pd.concat([data["people"], new_people]).drop_duplicates()
    movie_directors = [x["id"] for x in movie_data["directors"]]
    movie_actors = [x["id"] for x in movie_data["actors"]]

    # Movie
    new_movie = pd.DataFrame({
        "id": movie_data["id"],
        "name": movie_data["name"],
        "duration": movie_data["duration"],
        "release_year": movie_data["release_year"],
        "rating": movie_data["rating"],
        "rating_count": movie_data["rating_count"],
        "genres": [movie_genres.tolist()],
        "production_companies": [movie_companies.tolist()],
        "img_url": movie_data["img_url"],
        "directors": [movie_directors],
        "actors": [movie_actors],
        "similar_movies": [movie_data["similar_movies"]],
    }).set_index("id")
    if data['movies'].empty:
        data['movies'] = new_movie
    else:
        data["movies"] = pd.concat([data["movies"], new_movie])


def main(n_movies: int) -> None:
    data = load_data()

    if len(data["movies"]) >= n_movies:
        print(f"Already have {len(data['movies'])} movies, which is >= {n_movies}. Exiting.")
        return

    new_movies_to_scrape: set[str] = set(movies_to_scrape) | set(data["movies"].explode('similar_movies').dropna()['similar_movies'].to_list())

    print(f"Starting scraping until we have {n_movies} movies.")
    error_count = 0
    while new_movies_to_scrape and data["movies"].shape[0] < n_movies and error_count < 10:
        movie_id = new_movies_to_scrape.pop()
        if movie_id in data["movies"].index:
            continue
        try:
            movie_data = get_movie_data(movie_id)
        except Exception as e:
            print(f"Error fetching movie {movie_id}: {e}")
            continue
        for movie in movie_data["similar_movies"]:
            if movie not in data["movies"].index:
                new_movies_to_scrape.add(movie)
        append_data(data, movie_data)
        print(f'Adding: {movie_data["name"]}')
        print(f"Have {len(data['movies'])} movies, need {n_movies}. Still have {len(new_movies_to_scrape)} to scrape.")

    save_data(data)


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    main(N)
