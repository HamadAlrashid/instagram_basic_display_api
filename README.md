## What is this
This project was part of my 2024 Summer internship at an AI startup based in the Bay Area. As an ML/AI Intern, I worked on multiple projects and one of them is a vertical implementation of robust data pipeline for adding Instagram as a new data source in the company's main app. This project contains a robust data pipeline that starts with handling user authentication with Instagram, performs data fetching & normalization, and ends with all the processed and compressed data saved in the database, enriching the overall application. Under the hood, this project uses the Instagram Basic Display API, which is the offical API used to authorize with Instagram and fetch user posts.  

This repository does not contain the full implementation of the data pipeline I wrote.

## Files 
- `social_media_processor.py`: Abstract base class for implementing a social media processor, consisting of the following essential functions: authorize(), fetch_data(), extract_and_preprocess(), save_data_to_db(), and enrich()
- `instagram_processor.py`:  The full implementation of an Instagram Processor class. 
- `basic_display_api.py`: Contains the API call functions to interact with the Instagram Basic Display API 
- `auth_endpoint.py`: A flask endpoint (development server) for redirecting the user to the instagram login page and handling callback redirection to capture the authorization code after the user authorize
- `json_validation.py`: A pydantic json validator for validating all data models and types. 
- `crud/`: A folder that contains crud functions and unit tests for interacting with the database 
- `models/`: A folder that contains all the data models, objects, and types
- `prompts/`: A folder that contains all LLM prompts used in the processor

## Instagram API requirements
- Create a Facebook developer account and create an App: https://developers.facebook.com
- Add Instagram Basic Display as a product in your App
- Fill in all requirements for the Instagram Basic Display API. This includes providing the OAuth Redirect URI
- Create a .env file, and add all required environment variables that are listed at the start of `instagram_processor.py` and `auth_endpoint.py`


## Integration & Deployment requirements
The following components are not present this repository:
- UI & UX: Instagram authentication flow and design assests such as icons and buttons...etc
- Setting up a production API endpoint for receiving the authorization code from Instagram 
    
