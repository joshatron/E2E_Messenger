End-to-End Encrypted Messenger
==============================

This will be a simple E2E encrypted messaging command-line app.
There will be a server component and a client component.

Please note that this is designed for a class, and probably shouldn't be trusted in a production setting.

Usage
-----

To run this program, you need to have python >=3.8 installed, as well as pip.
On debian based systems, you probably will need to run:

    sudo apt install python3-pip

First you need to setup the environment.
The most basic way is to run the setup script:

    ./setup

If you want to use venv to keep the requirements contained to just the application, run:

    ./venvSetup

To start the server after you have set everything up:

    ./runServer

And to start the client, run:

    ./runClient

When running the client, if you don't want to see all the debugging messages for encrypting and decrypting, open the file e2emessenger/crypto/crypto.py and change:

    DETAILED_OUTPUT = True

to:

    DETAILED_OUTPUT = False

Server
------

The server will be very simple.
It uses a simple file in JSON format for storage, located at server_data/server_data.json, keeping everything in memory while it is running.
Below are all of the endpoints on it.


#### POST /v1/user/register

This endpoint registers a new user.
The user provides a username, their public key, and an initial timestamp.
The server makes sure that the username does not already exists and saves the information.

Request body:

    {
        "username": "[REQUESTED USERNAME]",
        "public_key": "[PUBLIC KEY IN PEM FORMAT]",
        "time": "[CURRENT TIME IN ISO FORMAT]"
    }

Server response:

    Success: 204 status code
    Failure: 
        Username exists: 409 status code
        Bad input: 400 status code

#### GET /v1/user/{username}

This endpoint returns all information about the user, their public key and username.

Request parameters:

    username=[REQUESTED USER TO SEARCH]

Server response:

    Success: 200 status code
    {
        "username": "[REQUESTED USERNAME]",
        "public_key": [REQUESTED USER'S PUBLIC KEY IN PEM FORMAT]
    }
    Failure:
        Username not found: 404 status code
        Bad input: 400 status code

#### PUT /v1/user/{username}/message/send

This endpoint is used to send a message from one user to another.
The body should contain the sender username with their signature, the recipient username, and the message, encrypted with the recipient's public key and base64 encoded.
If the sender is authenticated, the message gets put in the recipient's queue to read.

Request body:

    {
        "auth": {
            "username": "[REQUESTER USERNAME]",
            "time": "[CURRENT TIMESTAMP IN ISO FORMAT]",
            "signature": "[BASE64 ENCODED SIGNATURE OF USERNAME AND TIMESTAMP]"
        },
        "recipient": "[RECIPIENT USERNAME]"
        "message": "[BASE64 ENCODED ENCRYPTED MESSAGE BLOCK]"
    }

Server response:

    Success: 204 status code
    Failure:
        Auth failure: 401 status code
        Bad input: 400 status code

#### POST /v1/user/{username}/message/pull

At any time, a user can request all their unread messages.
They authenticate with their digital signature.
Once they are downloaded, the messages are deleted from the server.

Request body:

    {
        "username": "[REQUESTER USERNAME]",
        "time": "[CURRENT TIMESTAMP IN ISO FORMAT]",
        "signature": "[BASE64 ENCODED SIGNATURE OF USERNAME AND TIMESTAMP]"
    }

Server response:

    Success: 200 status code
    {
        "messages": [
            "[BASE64 ENCODED MESSAGE 1]",
            "[BASE64 ENCODED MESSAGE 2]",
            ...
        ]
    }
    Failure:
        Auth failure: 401 status code
        Bad input: 400 status code

Client
------

The client is a simple interactive command line application.
The first time it is run, it requests a username, generates a public/private key pair, and registers with the server.

To connect with other users, you request the server for their public key using their username.
The public key and username is saved locally to act as a contact book.

When you want to send a message, simply specify a recipient from your contact book and the text of the message and it will send it to the server.

You can also at any time pull down your latest messages.
Then you can view your conversations.

All data is stored in the client_data folder.
The private key is stored in key.private.
The server URL is stored in server.txt.
Your username is stored in username.txt.
All peer public keys are stored in the peers folder, with the name of the file being the username of the person.
Similarly, conversations are stored in the conversations folder, with the name of the file being the user the conversation is with.

Cryptography
------------

Below is a summary of the cryptography used in this application.

#### Authentication With Server

In order to authenticate the client with the server, first the client needs to generate an 2048 bit RSA keypair with a public exponent of e = 65537.
Next, the client shares the public key in PEM format, an associated username, and an initial timestamp with the server.
The server stores all this data for authentication with the user.

Later, when the client needs to perform an authenticated action, the send and read endpoints, it provides the following information:

 * The user's username
 * A current timestamp
 * A signature generated with the client's private key where the encrypted message is the username + " " + timestamp in iso format.

The server first checks that the username exists.
It then checks that the timestamp is later than the stored timestamp for that user.
Finally, it decrypts the signature with the public key to verify the message.
If the data matches, the client is authenticated, the server stores the new latest timestamp, and performs the requested action for the client.

The signature created used PSS with MGF1 for padding and SHA256 for hashing.

#### Send Message

The messages sent between users use the following scheme for encryption an decryption.

First, the messgage contents are generated.
This is made in a JSON format:

    {
        "from": "[CLIENT USERNAME]",
        "to": "[RECIPIENT USERNAME]",
        "time": "[CURRENT TIMESTAMP IN ISO FORMAT]",
        "message": "[MESSAGE SENT FROM USER]",
        "hash": "[HASH OF MESSAGE]"
        "signature": "[SIGNATURE OF HASH]"
    }

The contents to hash for [HASH OF MESSAGE] are from + " " + to + " " + time + " " + message and it uses the SHA256 hash.
The signature is a signature with the sender's private key using the hash as the message.
This JSON object is then encrypted with the recipient's public key and sent to the other user to the server.
Because of the limits for message length of RSA, if the JSON object is longer than 100 characters, it is split into 100 character chunks to be encrypted.
This scheme will ensure confidentiality, integrity, and non-repudiation.

When the recipient recieves the message, they start by decrypting it with their private key.
They then ensure that the to, from, and time fields make sense.
Then they generate the message hash and confirm it is identical to what was provided.
Finally, they decrypt the signature with the sender's public key and ensure the contents are identical to the hash.
If they don't already have the sender's public key, they first retrieve it from the server.
If any step fails, they discard the message.

Upgrades
--------

Below are a list of features that would be good to add, but I don't have time to implement before this program is due.
I will hopefully come back in the future and implement these.

 * The server should have a private key, and the client should send their auth encrypted with the server's public key.
 * The server is set up with plain HTTP currently. It should allow for HTTPS.
 * The server has a pretty simple backend, just in memory and file based. If it needs to be able to scale more, I should implement a database backend.
 * The client should encypt all local data with their public key so no one can read the data.
 * The client should have a way to export data, including private key, efficiently.
 * A GUI client should be created.
 * There currently could be problems with auth if a user changes time zones. This edge case should be dealt with.
