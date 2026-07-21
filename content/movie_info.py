# Movie information module for Dreamcobots content display.
# Provides movie details, trending titles, and search capabilities.

import random


MOVIE_DATABASE = [
    {
        "title": "Inception",
        "year": 2010,
        "genre": ["Sci-Fi", "Thriller"],
        "director": "Christopher Nolan",
        "rating": 8.8,
        "description": "A thief who enters the dreams of others to steal secrets from their subconscious.",
    },
    {
        "title": "The Shawshank Redemption",
        "year": 1994,
        "genre": ["Drama"],
        "director": "Frank Darabont",
        "rating": 9.3,
        "description": "Two imprisoned men bond over years, finding solace and redemption.",
    },
    {
        "title": "Interstellar",
        "year": 2014,
        "genre": ["Sci-Fi", "Adventure"],
        "director": "Christopher Nolan",
        "rating": 8.6,
        "description": "A team of explorers travel through a wormhole in space to ensure humanity's survival.",
    },
    {
        "title": "The Dark Knight",
        "year": 2008,
        "genre": ["Action", "Crime", "Drama"],
        "director": "Christopher Nolan",
        "rating": 9.0,
        "description": "Batman sets out to dismantle the remaining criminal organizations in Gotham.",
    },
    {
        "title": "Forrest Gump",
        "year": 1994,
        "genre": ["Drama", "Romance"],
        "director": "Robert Zemeckis",
        "rating": 8.8,
        "description": "The story of Forrest Gump and his extraordinary life journey.",
    },
    {
        "title": "The Matrix",
        "year": 1999,
        "genre": ["Sci-Fi", "Action"],
        "director": "Lana Wachowski, Lilly Wachowski",
        "rating": 8.7,
        "description": "A hacker discovers the world is a simulation and joins a rebellion against machines.",
    },
    {
        "title": "Pulp Fiction",
        "year": 1994,
        "genre": ["Crime", "Drama"],
        "director": "Quentin Tarantino",
        "rating": 8.9,
        "description": "Interconnected stories of criminals in Los Angeles.",
    },
    {
        "title": "WALL-E",
        "year": 2008,
        "genre": ["Animation", "Sci-Fi"],
        "director": "Andrew Stanton",
        "rating": 8.4,
        "description": "A small waste-collecting robot embarks on a space adventure.",
    },
]


class MovieInfo:
    """Provides movie information and search for Dreamcobots content display."""

    def __init__(self, database=None):
        self.database = database if database is not None else MOVIE_DATABASE

    def get_random(self):
        """Return a random movie from the database."""
        return dict(random.choice(self.database))

    def search_by_title(self, query):
        """Search movies by partial title (case-insensitive)."""
        query_lower = query.lower()
        results = [m for m in self.database if query_lower in m["title"].lower()]
        return [dict(m) for m in results]

    def search_by_genre(self, genre):
        """Return all movies matching a genre."""
        genre_lower = genre.lower()
        results = [m for m in self.database if any(g.lower() == genre_lower for g in m["genre"])]
        return [dict(m) for m in results]

    def get_top_rated(self, n=5):
        """Return the top N movies sorted by rating."""
        sorted_movies = sorted(self.database, key=lambda m: m["rating"], reverse=True)
        return [dict(m) for m in sorted_movies[:n]]

    def display(self, movie):
        """Return a formatted string for displaying a movie."""
        genres = ", ".join(movie.get("genre", []))
        return (
            f"🎬 {movie['title']} ({movie['year']})\n"
            f"   Director: {movie['director']}\n"
            f"   Genre: {genres}\n"
            f"   Rating: {movie['rating']}/10\n"
            f"   {movie['description']}"
        )
