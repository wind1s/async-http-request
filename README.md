# Asynchronous Http Requests
Single file which makes it easy to create limited asynchronous http requests. This limit is not implemented using semaphores from aiohttp as they can consume alot of memory when. A helper class to create requests is provided but is not mandatory.
You can manually call an async request using the aiohttp ```ClientSession.request```  or alias request methods such as ```ClientSession.get```.

### Example usage:

#### Standard use case
```
# ProcessRequest function type.
def parse_request(session, async_request):
    response = async_request.send(session)

    # do something with response...

requests = [AsyncRequest("GET", "/api"), AsyncRequest("GET", "/admin")]

run_async_requests(requests, parse_request, "https://mywebsite.com", 100)
```

#### Storing inside a database
```
import diskcache
import json

async def get_ip_info(session: ClientSession, ip_address: str) -> dict[str, str]:
    """"""
    base_url = "https://ipinfo.io"
    request = AsyncRequest(
        "GET", "/".join((base_url, ip_address)), headers={"Accept": "application/json"}
    )
    response = json.loads(await request.send(session))

    return response


def parse_ip_info_wrapper(ip_database):
    async def parse_ip_info(session, ip_address) -> None:
        ip_info = await get_ip_info(session, ip_address)
        ip_database.set(ip_address, ip_info)

    return parse_ip_info


def ip_info(ip_addresses, output_path) -> None:
    with diskcache.Cache(output_path) as database:
        run_async_requests(ip_addresses, parse_ip_info_wrapper(database))
```

#### Adding header data
```
def database_wrapper(database):
    def parse_request(session, async_request):
        response = async_request.send(session)
        key = response["day"]
        database.store(key, response)

    return parse_request

requests = [
    AsyncRequest("GET", "https://weather.com/api/monday", header={"Accept": "application/json"}),
    AsyncRequest("GET", "https://weather.com/api/tuesday", header={"Accept": "application/json"}),
    AsyncRequest("GET", "https://weather.com/api/wednesday", header={"Accept": "application/json"})
]

run_async_requests(requests, database_wrapper(database))
```

## Sources and inspiration
The core functionality, the function ```limited_as_completed``` is inspired from here:
https://www.artificialworlds.net/blog/2017/06/12/making-100-million-requests-with-python-aiohttp/