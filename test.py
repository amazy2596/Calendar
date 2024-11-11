# Code snippets are only available for the latest version. Current version is 1.x
from msgraph import GraphServiceClient
from msgraph.generated.models.calendar import Calendar
from azure.identity import DeviceCodeCredential

scopes = ['User.Read', 'Calendars.ReadWrite']

# Multi-tenant apps can use "common",
# single-tenant apps must use the tenant ID from the Azure portal
tenant_id = '03beee63-53d9-4f8f-a232-cc2bad9cbb49'

# Values from app registration
client_id = 'e11948df-58d2-4c45-9ca4-ecacdbf6b32a'
client_secret = 'a5518ab5-4268-4c5f-853a-c55cb5ef6bca'

# azure.identity
credential = DeviceCodeCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

graph_client = GraphServiceClient(credential, scopes) # type: ignore

# To initialize your graph_client, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=python
request_body = Calendar(
	name = "Volunteer",
)

import asyncio

async def main():
    result = await graph_client.me.calendars.post(request_body)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())