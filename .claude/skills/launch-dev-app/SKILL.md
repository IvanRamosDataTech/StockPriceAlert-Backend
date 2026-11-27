---
name: launch-dev-app
description: This skill should be used to launch the development environment application and make sure it is properly set up and running.
---

When the user asks about how to launch or set up the development environment application, use this skill to provide guidance and ensure the application is properly configured and running.

## When to Use This Skill

Activate this skill when the user:

- Asks setup or configuration questions about app launch or development environment
- Requests code snippets regarding configurations like environment variables, setup scripts, database connections or API integrations
- Needs to know how exactly Telegram bot is set up and integrated into the development environment
- Asks for available endpoints for watchlists, asset alerts, or other related API functionalities
- Asks to stop any running development environment processes

## How to Launch the app in development mode

### Step 1: Select virtual environment

- In a terminal, call `source venv/bin/activate`
- Then run `flask run`  (development server should point to http://127.0.0.1:5000)

### Step 2: Setup Reverse proxy for Telegram communication
- In a separated terminal, run  `ngrok http 127.0.0.1:5000 --url https://preverbal-ileen-overtimorously.ngrok-free.dev`

### Step 3: Send a test message to the Telegram bot
- Open the Telegram bot and send a test message to ensure it is properly receiving messages through the configured reverse proxy.
by calling in a third terminal:
curl --location 'https://api.telegram.org/bot8792260036:AAHLxJBtP-2yMnTdasDIDGiXXyWpIz1HtOA/sendMessage' \
--header 'Content-Type: application/json' \
--data '{
    "chat_id": 1593430808,
    "text": " Hey Bot, I'\''m here from claude code. Testing development environment."
}'


## Guidelines

- **Be specific**: If something goes wrong during launch, give a summary of what is happening.
- **Terminals** Leave each terminal open for its respective task (e.g., one for the Flask server, one for the reverse proxy, and one for sending test messages).
- **Stopping processes** Make sure to properly terminate any running development environment processes when they are no longer needed, such as the Flask server or the reverse proxy, when user asks to stop them.