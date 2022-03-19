End-to-End Encrypted Messenger
==============================

This will be a simple E2E encrypted messaging command-line app.
There will be a server component and a client component.

Usage
-----

First you need to setup the environment.
The most basic way is to run the setup script:

    ./setup

If you want to use venv to keep the requirements contained to just the application, run:

    ./venvSetup

To start the server after you have set everything up:

    ./runServer

Server
------

The server will be very simple.
Below are all of the endpoints on it.

#### /v1/user/register

This endpoint registers a new user.
The user provides a username and their public key.
The server makes sure that the username does not already exists and saves the information.

#### /v1/user/info

This endpoint returns all information about the user, their public key and username.

#### /v1/message/send

This endpoint is used to send a message from one user to another.
The body should contain the sender username with their signature, the recipient username, and the message, encrypted with the recipient's public key and base64 encoded.
If the sender is authenticated, the message gets put in the recipient's queue to read.

#### /v1/message/read

At any time, a user can request all their unread messages.
They authenticate with their digital signature.
Once they are downloaded, the messages are deleted from the server.

Client
------

The client will be a simple interactive command line application.
The first time it is run, it requests a username, generates a public/private key pair, and registers with the server.

To connect with other users, you request the server for their public key using their username.
The public key and username is saved locally to act as a contact book.

When you want to send a message, simply specify a recipient from your contact book and the text of the message and it will send it to the server.

You can also at any time pull down your latest messages.
Then you can view your conversations.
