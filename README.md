# HTMX FastAPI Service

A modern web application built with FastAPI and HTMX, demonstrating server-side rendering with dynamic interactions.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **HTMX**: Dynamic HTML interactions without writing JavaScript
- **Jinja2 Templates**: Server-side templating engine
- **Tailwind CSS**: Utility-first CSS framework for styling
- **uv**: Fast Python package manager and project manager

## Project Structure

```
htmx-fastapi-service/
├── main.py                 # FastAPI application
├── pyproject.toml          # Project configuration and dependencies
├── templates/              # Jinja2 HTML templates
│   ├── index.html         # Main page template
│   ├── message_partial.html # Message partial template
│   └── messages_list.html  # Messages list template
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
└── README.md              # This file
```

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. Clone or navigate to the project directory:
   ```bash
   cd htmx-fastapi-service
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the development server:
   ```bash
   uv run python main.py
   ```

   Or alternatively:
   ```bash
   uv run uvicorn main:app --reload
   ```

4. Open your browser and visit: http://localhost:8000

## Development

### Adding Dependencies

To add new dependencies:
```bash
uv add package-name
```

To add development dependencies:
```bash
uv add --dev package-name
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run isort .
```

## API Endpoints

- `GET /` - Home page with HTMX demo
- `POST /api/message` - Create a new message (HTMX endpoint)
- `GET /api/messages` - Get all messages (HTMX endpoint)

## HTMX Features Demonstrated

- **Form Submission**: Adding messages without page refresh
- **Dynamic Content Loading**: Refreshing messages list
- **Partial Updates**: Updating specific parts of the page
- **Server-Side Rendering**: Templates rendered on the server

## Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [HTMX](https://htmx.org/) - Dynamic HTML
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [uv](https://docs.astral.sh/uv/) - Python package manager
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

## License

This project is open source and available under the [MIT License](LICENSE).
