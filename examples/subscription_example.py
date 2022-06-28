from nimiqclient import *
import asyncio


async def process_block(client, hash):
    block = await client.get_block_by_hash(hash, False)
    # Nothing to do when the block is a micro block
    if block.type == "micro":
        print("Received micro block #{}: {}".format(block.number, hash))
    else:
        print("Received macro block #{}: {}".format(block.number, hash))


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
                print("Subscribing to new blocks ...")
                await client.head_subscribe(process_block)

        except InternalErrorException as error:
            print("Got error when trying to connect to the RPC server: {0}"
                  .format(str(error)))

        while True:
            await asyncio.sleep(1)


def main():
    asyncio.get_event_loop().run_until_complete(run_client())


if __name__ == "__main__":
    main()
