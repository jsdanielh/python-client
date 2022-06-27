from nimiqclient import *


def main():
    # Create Nimiq RPC client
    client = NimiqClient(
        scheme="http", user="luna", password="moon", host="127.0.0.1",
        port=8648
    )

    try:
        # Get consensus
        consensus = client.consensus()
        print("Consensus: {0}".format(consensus))

        if consensus:
            # Get accounts
            print("Getting basic accounts:")
            for address in client.accounts():
                account = client.get_account_by_address(address)
                if account.type == AccountType.BASIC:
                    # Show basic account address
                    print(account.address)

    except InternalErrorException as error:
        print(
            "Got error when trying to connect to the RPC server: {0}".format(
                str(error)))


if __name__ == "__main__":
    main()
