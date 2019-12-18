import giphy_client
from giphy_client.rest import ApiException
from pprint import pprint
from random import sample

# create an instance of the API class
api_instance = giphy_client.DefaultApi()
api_key = '31mzCxv2Wzk0LY9m3zfscDLvA7x7hheg' # str | Giphy API Key.
q = 'cheeseburgers' # str | Search query term or prhase.
limit = 50 # int | The maximum number of records to return. (optional) (default to 25)
# offset = 0 int | An optional results offset. Defaults to 0. (optional) (default to 0)
rating = 'g' # str | Filters results by specified rating. (optional)
lang = 'en' # str | Specify default country for regional content; use a 2-letter ISO 639-1 country code. See list of supported languages <a href = \"../language-support\">here</a>. (optional)
fmt = 'json' # str | Used to indicate the expected response format. Default is Json. (optional) (default to json)

def getGIFs(interest):
    q = interest
    try: 
        # Search Endpoint
        api_response = api_instance.gifs_search_get(api_key, q, limit=limit, rating=rating, lang=lang, fmt=fmt)
        
    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)
    
    randomIndices = set()
    ourRange = range(0, len(api_response.data)) # What if len(api_response.data) is less than 3? Deal with issue here.

    if len(ourRange) < 4:
        randomIndices = {i for i in ourRange}
    
    else:
        while len(randomIndices) < 4:
            ourSample = sample(ourRange, 1)[0]
            randomIndices.add(ourSample)
    
    retVal = []
    for i in randomIndices:
        retVal.append(api_response.data[i].images.fixed_height.url)
    
    return retVal

def getRandomGIF():
    try: 
        # Search Endpoint
        api_response = api_instance.gifs_random_get(api_key, rating=rating, fmt=fmt)
        
    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)

    return api_response.data.image_original_url
