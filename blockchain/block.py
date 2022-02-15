# SHA256 hash-algorithm
from hashlib import sha256

from datetime import datetime
import json

# Add to path
from sys import path
import os
from wsgiref.validate import validator
path.insert(0, os.path.join(os.getcwd(), '../'))

# Project version
from __init__ import __version__

# Blockchain-classes
from blockchain import Transaction
# from blockchain import Blockchain

class Block:
    def __init__(self, transactions=[], validator=None, signature=None, previous_block=None):
        """Set the block-values up.

        :param transactions: All transactions included into the block.
        :type transactions: [ :py:class: Transaction ]
        :param validator: The public-key of the validator.
        :type validator: str (hex-digest)
        :param signature: Signed hash with the private-key of the validator.
        :type signature: str (hex-digest)
        :param previous_block: The last-block in the blockchain.
        :type previous_block: :py:class: blockchain.block.Block
        """

        # Check if there was a previous-block
        if previous_block:
            self.index = previous_block.index + 1
            self.previous_hash = previous_block.hash

        # Set values for the genesis-block
        else:
            self.index = 1
            self.previous_hash = \
            '0000000000000000000000000000000000000000000000000000000000000000'

        self.version = __version__

        # Create the timestamp of the block
        self.timestamp = datetime.now()

        self.base_fee = 1
        # TODO -> Calculate the base-fee of a transaction (maybe with current
        #         average block creation-time and node-count)

        self.tx = transactions

        self.validator = validator
        self.signature = signature

    @property
    def tx_json(self) -> list:
        """Creates json-version of the included transactions

        :return: str (stringified json)
        """

        # Add all transactions in json-format to a list
        tx_list = []
        for tx in self.tx:
            tx_list.append(tx.to_dict())

        return tx_list

    @property
    def hash(self) -> str:
        """Calculates the hash of the block with the SHA256 hash-algorithm.

        :return: Hex-digest of transaction-hash
        :rtype: str (hex-digest)
        """

        # Check if the block contains are important values
        if not self.validator or not self.signature:
            # Development logs
            print("WARNING!: Block incomplete, hash could be not right!")

        return sha256((str(self.index) + self.version + str(self.timestamp) + str(self.base_fee) + str(self.tx_json) + self.validator if self.validator else "" + self.signature if self.signature else "").encode()).hexdigest()


    def sign_block(self, key) -> str:
        """Signs the block with the private-key of the validators keypair

        :param key: The private-key of the validator
        :type key: str

        :return: Signature of the block-hash and private-key
        """
        return '' # TODO -> Add block signature-feature


    def to_json(self):
        """For data transportation/storing purposes, a json-format is created

        :return: Block in json-format
        :rtype: str (stringified json)
        """
        block_dict = {
            'index': self.index,
            'version': self.version,
            'base_fee': self.base_fee,
            'tx': self.tx_json,
            'timestamp': str(self.timestamp),
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'validator': self.validator,
            'signature': self.signature
        }

        return json.dumps(block_dict)


    def from_tx_dict(self, tx_dict) -> bool:
        """Create transactions from dict-data

        :param tx_dict: List that includes transaction-values as dict-object.
        :type tx_dict: list

        :return: A status wether the data-load was successful or not
        :rtype: bool
        """

        # Set transactions class-list up
        tx_list = []
        for tx in tx_dict:
            # Set transaction class up
            new_tx = Transaction("", "", 0)
            print(tx)
            success = new_tx.from_dict(tx)

            # Check if something did not seem to work
            if not success:
                return False

            # Add to list
            tx_list.append(new_tx)
            print(tx_list)

        # Parse the list
        self.tx = tx_list

        return True


    def from_json(self, json_data) -> bool:
        """Create block from json-data.

        :param json_data: String in json-format that includes the block-values
        :type json_data: str

        :return: A status wether the data-load was successful or not
        :rtype: bool
        """

        # Convert json to dictionary
        dict_data = json.loads(json_data)

        try:
            # Set the data to the transaction
            self.index = dict_data['index']
            self.version = dict_data['version']
            self.base_fee = dict_data['base_fee']

            self.from_tx_dict(dict_data['tx'])

            # Create datetime-object from string
            self.timestamp = datetime.strptime(dict_data['timestamp'], '%Y-%m-%d %H:%M:%S.%f')

            self.previous_hash = dict_data['previous_hash']

            # Check if the validator is included in the json-data
            if dict_data['validator']:
                self.validator = dict_data['validator']

            # Check if the signature is included in the json-data
            if dict_data['signature']:
                self.signature = dict_data['signature']

        # Return the status
        except KeyError or json.JSONDecodeError:
            return False

        return True
