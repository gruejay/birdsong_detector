import asyncio
from curses import meta
import json
import os
import shutil
import sys
import time
import pandas as pd
import numpy as np
from urllib import request, error

import aiofiles
import aiohttp

def metadata(filt):
    page = 1
    page_num = 1
    filt_path = list()
    filt_url = list()
    print("Retrieving metadata...")

    # Scrubbing input for file name and url
    for f in filt:
        filt_url.append(f.replace(' ', '%20'))
        filt_path.append((f.replace(' ', '')).replace(':', '_')
                         .replace('\"', ''))

    path = 'dataset/metadata/' + ''.join(filt_path)

    # Create a metadata folder if it does not exist already
    if not os.path.exists(path):
        os.makedirs(path)

    # Input parameters are separated by %20 for use in URL
    query = ('%20'.join(filt_url))

    # Save all pages of the JSON response
    while page < (page_num + 1):
        url = ('https://www.xeno-canto.org/api/2/recordings?'
               'query={0}&page={1}'.format(query, page))
        try:
            r = request.urlopen(url)
        except error.HTTPError as e:
            print("An error has occurred: " + str(e))
            exit()
        print("Downloading metadata page " + str(page) + "...")
        data = json.loads(r.read().decode('UTF-8'))
        filename = path + '/page' + str(page) + '.json'
        with open(filename, 'w') as saved:
            json.dump(data, saved)
        page_num = data['numPages']
        page += 1

        # Rate limit of one request per second
        time.sleep(1)

    # Return the path to the folder containing downloaded metadata
    print("Metadata retrieval complete.")
    return path


# Client that processes the list of track information concurrently
def chunked_http_client(num_chunks):

    # Semaphore used to limit the number of requests with num_chunks
    semaphore = asyncio.Semaphore(num_chunks)

    # Processes a tuple from the url_list using the aiohttp client_session
    async def http_get(track_tuple, species_path, client_session):

        # Work with semaphore located outside the function
        nonlocal semaphore
        async with semaphore:

            # Pull relevant info from tuple
            track_id = str(track_tuple[0])
            url = track_tuple[1]

            # Set up the paths required for saving the audio file
            
            file_path = species_path + track_id + '.mp3'

            # Create an audio folder for the species if it does not exist
            if not os.path.exists(species_path):
                print("Creating recording folder at " + str(species_path))
                os.makedirs(species_path)

            # If the file exists in the directory, we will skip it
            if os.path.exists(file_path):
                print(track_id + ".mp3 is already present. Skipping...")
                return

            # Use the aiohttp client to retrieve the audio file asynchronously
            async with client_session.get(url) as response:
                if response.status == 200:
                    f = await aiofiles.open((file_path), mode='wb')
                    await f.write(await response.content.read())
                    await f.close()
                elif response.status == 503:
                    print("Error 503 occurred when downloading " + track_id +
                          ".mp3. Please try using a lower value for "
                          "num_chunks. Consult the README for more "
                          "information.")
                else:
                    print("Error " + str(response.status) + " occurred "
                          "when downloading " + track_id + ".mp3.")

    return http_get

async def download(url_list, path, num_chunks=4):
    """ takes in a dict contianing "name": str, "quality": char, and 
    "urls": list

    downloads the mp3 files from the urls and stores them in the path
    designated by the base_path/species_name/quality
    """


    # Setup the aiohttp client with the desired semaphore limit
    http_client = chunked_http_client(num_chunks)
    async with aiohttp.ClientSession() as client_session:

        # Collect tasks and await futures to ensure concurrent processing
        tasks = [http_client(track_tuple, path,  client_session) for track_tuple in
                 url_list]
        for future in asyncio.as_completed(tasks):
            data = await future
    print("Download complete.")
    return path





