import json

import typer
from time import sleep
from pysui import SyncClient, handle_result
from pysui.sui.sui_builders.get_builders import GetObjectsOwnedByAddress
from pysui.sui.sui_txn.sync_transaction import SuiTransaction
from pysui.sui.sui_txresults.complex_tx import TxResponse
from pysui.sui.sui_txresults.single_tx import ObjectRead, ObjectReadPage
from pysui.sui.sui_types import ObjectID, SuiAddress
from rich import print

from suilend_capsule_cli import ROOT_DIR
from suilend_capsule_cli.sui import Sui

app = typer.Typer()

SUILEND_CAPSULE_OBJECT_TYPE = "0x008a7e85138643db888096f2db04766d549ca496583e41c3a683c6e1539a64ac::suilend_capsule::SuilendCapsule"


def get_suilend_capsule_ids(
    address: SuiAddress,
    rarity: str,
    sui_client: SyncClient,
) -> list[ObjectID]:
    capsule_ids: list[ObjectID] = []

    query = {
        "filter": {
            "StructType": SUILEND_CAPSULE_OBJECT_TYPE,
        },
        "options": {
            "showType": False,
            "showOwner": False,
            "showPreviousTransaction": False,
            "showDisplay": False,
            "showContent": True,
            "showBcs": False,
            "showStorageRebate": False,
        },
    }
    cursor = None
    while True:
        builder = GetObjectsOwnedByAddress(
            address=address,
            query=query,
            limit=50,
            cursor=cursor,
        )
        result = handle_result(
            sui_client.execute(builder),
        )
        if isinstance(result, ObjectReadPage):
            objs: list[ObjectRead] = result.data
            for obj in objs:
                if obj.content.fields["rarity"] == rarity:
                    capsule_ids.append(obj.object_id)
            if not result.has_next_page:
                break
            cursor = result.next_cursor
            sleep(0.2)
    return capsule_ids


@app.command()
def airdrop(
    rarity: str = typer.Argument(
        ...,
        help="Rarity of the capsules to airdrop.",
    ),
):
    # Open JSON file with addresses.
    with open(ROOT_DIR / "addresses.json", "r") as f:
        addresses: list[str] = json.load(f)

    if len(addresses) > 500:
        raise typer.Exit("Airdrop limit is 500 addresses.")

    # Verify address char length.
    for address in addresses:
        if not address.startswith("0x") or len(address) != 66:
            raise typer.Exit(f"Invalid address detected: {address}")

    # Find all capsule IDs with the given rarity.
    sui = Sui()
    capsule_ids: list[ObjectID] = get_suilend_capsule_ids(
        sui.config.active_address,
        "common",
        sui.client,
    )
    if len(capsule_ids) < 1:
        raise typer.Exit(f"Not enough {rarity} capsules to fulfill the airdrop.")

    airdrop = {
        capsule_id: address
        for capsule_id, address in zip(capsule_ids[: len(addresses)], addresses)
    }

    print(airdrop)
    typer.confirm(f"Confirm airdrop details to {len(airdrop)} recipients:", abort=True)

    txer = SuiTransaction(
        client=sui.client,
        compress_inputs=True,
        merge_gas_budget=True,
    )

    for capsule_id, address in airdrop.items():
        txer.transfer_objects(
            transfers=[ObjectID(capsule_id)],
            recipient=SuiAddress(address),
        )

    result = handle_result(txer.execute(gas_budget=5_000_000_000))
    if isinstance(result, TxResponse):
        print(result.effects.status)
        print(f"TX Digest: {result.effects.transaction_digest}")

    return


@app.command()
def hello():
    return
