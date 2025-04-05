from sharkiq.auth0 import auth_flow_complete

import asyncio
import aiohttp

async def main():
    # Initialize the session
    async with aiohttp.ClientSession() as session:
        # Perform the authentication flow
        # Change is_eu to True or False based on your region
        try:
            token = await auth_flow_complete(session, is_eu=True, username=input("Enter Shark Username: "), password=input("Enter Shark Password: "))
            print("Authentication successful, token:", token)
        except Exception as e:
            print("Authentication failed:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
# This code snippet demonstrates how to use the auth_flow_complete function
