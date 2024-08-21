# ACNH Bot
ACNH Bot is a custom bot inspired by the video game series 
["Animal Crossing: New Horizons"](https://en.wikipedia.org/wiki/Animal_Crossing:_New_Horizons) (ACNH), to stimulate a 
game-like experience in Discord servers. This bot provides a unique experience by allowing users to participate in 
similar game features such as inviting and managing their island villagers, collecting museum specimens, and growing 
in-game economy. 

## Inviting ACNH Bot to Your Server
Use this link to add the bot to your server:
https://discord.com/oauth2/authorize?client_id=1265378367763386390

## Developing 
### Requirements
- Python 3.8+
- Google Firebase Database

### Setup
1. Clone the repository
   ```sh
   git clone https://github.com/claaudiaale/acnh-bot.git
   ```
2. Open the project in a Python virtual environment
3. Install the required dependencies
    ```sh
    pip install -r requirements.txt
    ```
4. Apply for an API key to the Nookipedia API: https://api.nookipedia.com/
5. Acquire your [Firebase Web App Credentials](https://firebase.google.com/docs/auth/web/start) and provide access to 
the JSON file in your project directory
6. Create an ```.env``` file with the following environment variables:
   ```sh
    BOT_TOKEN=<a discord bot token>
    FIREBASE_CREDENTIALS=<path to your Firebase Web App Credentials JSON file>
    ACNH_API_KEY=<an access Key to the Nookipedia API>
    ```
   - [Finding your discord bot token](https://guide.pycord.dev/getting-started/creating-your-first-bot)


