# youtube-api-app

A simple real-time application built using the [YouTube API v3](https://developers.google.com/youtube/v3/getting-started) that searches for and displays videos related to your favourite topic.

The application fetches new data periodically and organizes it in a user-friendly Grafana dashboard that helps you to view and query your favourite videos.

<img src="img/dashboard.jpg" alt="screenshot of dashboard">

# How to use youtube-api-app

You can use the youtube-api-app by sending simple `GET` requests to the respective endpoints. For each request, you will receive corresponding video data, organised in the following key-value pairs:

| Field         	| Description                                                   	|
|---------------	|---------------------------------------------------------------	|
| `_id`           	| The unique ID of the YouTube video                            	|
| `channel_id`    	| The unique ID of the channel that posted the video            	|
| `title`         	| The title of the YouTube video                                	|
| `description`   	| The description of the YouTube video                          	|
| `video_url`     	| The URL to the YouTube video                                  	|
| `thumbnail_url` 	| The URL to the high resolution thumbnail of the YouTube video 	|
| `published_at`  	| The timestamp (ISO 8601) at which the video was posted        	|

A Postman collection has been included in the `test/` directory. You can use it to test the application's endpoints.

## Fetch Videos from Database

You can fetch paginated videos from the database by sending a `GET` request to the `/fetch` endpoint.

```bash
curl --location --request GET 'localhost:5000/fetch'
```

You can also specify a `page_id` to fetch a specific page of videos.

```bash
curl --location --request GET 'localhost:5000/fetch?page_id=1'
```

### Response

| Field        	| Description                                              	|
|--------------	|----------------------------------------------------------	|
| `items`        	| A list of key-value mappings with details for each video 	|
| `next_page_id` 	| A token to access the next page of results               	|
| `page_id`      	| The current page's token                                 	|

## Search Videos

You can search for a video by sending a `GET` request to the `/search` endpoint with a `title` and `description` query parameter.

```bash
curl --location --request GET 'localhost:5000/search?title=dogs&description=cute and friendly'
```

### Response

| Field        	| Description                                              	|
|--------------	|----------------------------------------------------------	|
| `items`        	| A list of key-value mappings with details for each video 	|

## View Dashboard

You can view the data in a Grafana dashboard by visiting `localhost:3000` and navigating to the `FamPay` dashboard.

# How to setup the application

1. The first step is to download the fastText embedding model for query retrieval. You can download the pretrained models from [here](https://drive.google.com/drive/folders/1R6HtfCD2L5OFYOLgdQatRnVJHtxvq1z8?usp=sharing). Choose any of the pretrained model folders (choose `text8` for better speed or `wiki` for better matches) and download the contents. Place both the `.bin` and `.npy` files in a folder named `model` in the root of the application.

2. Create a `.env` file with the following variables. 
    - Replace `YOUTUBE_API_KEY` with your own YouTube API key - you can follow the instructions [here](https://developers.google.com/youtube/v3/getting-started) to get one
    - Leave `GRAFANA_API_KEY` empty for now - we will replace it later
    - If you would like to use a different database connection for the application, you can replace `DATABASE_URL` with your own connection string and `DATABASE_*` variables with the corresponding credentials

    ```bash
    YOUTUBE_API_KEY=""

    DATABASE_URL="postgresql://postgres:postgres@postgres:5432/postgres"
    DATABASE_USER="postgres"
    DATABASE_PASSWORD="postgres"
    DATABASE_HOST="postgres"
    DATABASE_PORT="5432"
    DATABASE_NAME="postgres"

    GRAFANA_URL="http://localhost:3000"
    GRAFANA_API_KEY=""
    ```

4. While building the application, you can specify the following command line arguments. All of the arguments are optional and they will take their default values if no argument is provided. You can also change the default values arguments for the application in `app/app.py`
    
    | Argument    	| Description                                     	|
    |-------------	|-------------------------------------------------	|
    | `QUERY`       	| Your query                                      	|
    | `TIME`        	| Time interval in minutes to fetch results       	|
    | `MAX_RESULTS` 	| Total number of results to return during search 	|
    | `HOST`        	| Host IP on which to run the application         	|
    | `PORT`        	| Port number on which to run the application     	|

    Specify the argument as `VARIABLE=VALUE` before the docker-compose command.
    
    Examples:
    ```bash
    QUERY=dogs docker-compose --project-name youtube-api-app up -d
    ```
    ```bash
    QUERY=cats TIME=3 MAX_RESULTS=10 docker-compose --project-name youtube-api-app up -d
    ```

5. Visit `localhost:3000` in your browser to view the Grafana dashboard. Navigate to `Settings`, and then `API Keys`. Generate a new API key with the `Admin` role.

6. Access the `grafana` container using the following command:
    ```bash
    docker exec -it grafana bash
    ```
    - Open the `.env` file using the following command:
        ```bash
        vi .env
        ```
    - Move your cursor to the line containing `GRAFANA_API_KEY`. Press `I` to enter insert mode and then paste your API key here. Exit insert mode by pressing `Esc` on your keyboard. Finally save and exit using `:wq`.
    - Run the following command to setup the Grafana dashboard:
        ```bash
        ./setup/setup_grafana.sh
        ```
    - Exit the container by typing `exit`
    - Restart the `grafana` container using the following command:
        ```bash
        docker restart grafana
        ```

7. Refresh the dashboard at `localhost:3000` in your browser. You should see the dashboard with the videos that you searched for in the  `FamPay YouTube API Search` dashboard directory.
