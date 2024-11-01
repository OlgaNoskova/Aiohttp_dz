import asyncio
import aiohttp


async def main():
    session = aiohttp.ClientSession()
    # response = await session.post("http://127.0.0.1:8080/advertisement/",
    #                               json={"title": "куплю книгу", "description": "Гарри Поттер"})
    # response = await session.get("http://127.0.0.1:8080/advertisement/2")
    # print(response.status)
    # print(await response.text())
    # await session.close()
    response = await session.delete("http://127.0.0.1:8080/advertisement/3")
    print(response.status)
    print(await response.text())
    response = await session.get("http://127.0.0.1:8080/advertisement/3")
    print(response.status)
    print(await response.text())
    await session.close()

asyncio.run(main())