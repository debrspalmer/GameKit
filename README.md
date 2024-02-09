# Steam Web API Flask App

## Overview
This Flask web application utilizes the Steam Web API to retrieve and display information about Steam users, their friends, and owned games. The project is part of the CSC 289 capstone project for a group.

## Prerequisites
- Python 3.x
- Flask
- Steam API key (set as an environment variable named 'STEAM_KEY')

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/steam-web-api-app.git
   cd steam-web-api-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up enviroment variables:
   - Obtain a Steam API key from [Steamworks](https://steamcommunity.com/dev/apikey).
   - Set the API key as an environment variable named 'STEAM_KEY'.
   ```bash
    export STEAM_KEY="xxxx"
   ```
   - Set WEB_URL to the url of the webpage. Include http or https
   ```bash
     export WEB_URL="https://domain.com"
   ```

4. Run the application:
    - Docker:
        - docker-compose examples provided under 'docker'
        - ```bash
            docker run -e STEAM_KEY="xxx" -e WEB_URL="https://domain.com" -p <port to expose>:5000 ghcr.io/buttercheetah/gamekit:latest
            ```
    - Standalone:
        - ```bash
            python app.py
            ```

## Project Structure
- Required programing files and other necessities are under root directory. ie. Dockerfile, main application (app.py), and SteamHandler.py 
- All HTML, CSS, and JavaScript files should be placed in the "templates" directory.

## Contribution Guidelines
- **Do not push directly to the main branch.**
- Create a branch for your work
- Commit your changes to your branch.
- Create a pull request (PR) for review.


## Disclaimer
This project is developed as part of the CSC 289 capstone project and is not intended for production use. Use the Steam API responsibly and adhere to their terms of service.
