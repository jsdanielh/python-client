from nimiqclient import *
import asyncio


async def run_client():
    async with NimiqClient(
        scheme="ws", host="127.0.0.1", port=9201
    ) as client:
        try:
            # Get consensus
            consensus = await client.consensus()
            print("Consensus: {0}".format(consensus))

            if consensus:
                # Get accounts
                print("Getting basic accounts:")
                for address in await client.accounts():
                    account = await client.get_account_by_address(address)
                    if account.type == AccountType.BASIC:
                        # Show basic account address
                        print(account.address)

        except InternalErrorException as error:
            print("Got error when trying to connect to the RPC server: {0}"
                  .format(str(error)))


def main():
    asyncio.get_event_loop().run_until_complete(run_client())


if __name__ == "__main__":
    main()
