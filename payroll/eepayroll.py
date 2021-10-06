"""liteacc.py."""
# python3 eepayroll.py ssyHjfYWS5mw7s5SCvevuvBnNYXqC
# rpECnbnC25HKgweeDCkWaYN7AuFbn9CLsz
# ssyHjfYWS5mw7s5SCvevuvBnNYXqC
import os
import sys
import binascii
import time
import json

from xrpl.clients import WebsocketClient
from xrpl.wallet import Wallet
from xrpl.utils import xrp_to_drops
from xrpl.models.transactions import Payment, SetHook
from xrpl.transaction import (
    send_reliable_submission,
    safe_sign_and_autofill_transaction,
    get_transaction_from_hash
)
from xrpl.ledger import get_latest_validated_ledger_sequence
from xrpl.account import get_next_valid_seq_number

w3 = WebsocketClient('wss://hooks-testnet.xrpl-labs.com')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tax.py <source family seed>")
        sys.exit()

    secret = sys.argv[1]
    wallet = Wallet(secret, 0)
    hook_account = wallet.classic_address

    with w3 as client:
        print('CONNECTED')

        CONTRACT_PATH = os.path.join(BASE_DIR, 'eepayroll.wasm')
        with open(CONTRACT_PATH, 'rb') as f:
            content = f.read()
        binary = binascii.hexlify(content).decode('utf-8').upper()
        current_validated_ledger = get_latest_validated_ledger_sequence(w3)
        sequence = get_next_valid_seq_number(hook_account, w3)
        built_transaction = SetHook(
            account=hook_account,
            create_code=binary,
            hook_on='0000000000000000'
        )
        # print(built_transaction)
        signed_tx = safe_sign_and_autofill_transaction(
            transaction=built_transaction,
            wallet=wallet,
            client=w3,
        )
        response = send_reliable_submission(signed_tx, w3)
        tx_result = response.result['meta']['TransactionResult']
        print('{} The hook was set. Only final in a validated ledger.'.format(tx_result))
        print('CLOSING...')
        client.close()
