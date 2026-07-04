# spinbetterInstructions_bot

This is a Telegram Bot built with Python 3.12 and aiogram 3.x. The bot acts as an Admin in a private Telegram channel and automatically sends a private message to users who request to join the channel (Chat Join Request).

## Project Structure
- `main.py`: The main bot script containing logic and error handlers.
- `config.py`: Configuration and cross-platform path management.
- `requirements.txt`: Minimal Python dependencies required for Railway and local deployment.
- `.env`: Environment variables (contains `BOT_TOKEN`). Make sure this is ignored by git!
- `images/`: Directory containing the `register.jpeg` image sent to users.
- `Procfile`: Command configuration for cloud platforms like Railway and Heroku.

---

## Local Setup Instructions

1. **Place your image:**
   Ensure you have an image named `register.jpeg` inside the `images` folder.

2. **Configure your Token:**
   Create a `.env` file and set your actual Telegram bot token:
   ```env
   BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
   ```

3. **Install Dependencies:**
   Create a virtual environment and install the required packages:
   ```bash
   python -m venv venv
   # Activate virtual environment on Windows:
   venv\Scripts\activate
   # Or on Mac/Linux:
   # source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run the Bot:**
   ```bash
   python main.py
   ```

---

## Deployment on Railway

The project is fully prepared to be deployed directly on [Railway.app](https://railway.app/). Follow these simple steps:

1. **Upload to GitHub:**
   - Commit your code and push it to a private GitHub repository.
   - *Note:* Do not upload the `.env` file! The `.gitignore` file takes care of this.

2. **Connect to Railway:**
   - Log in to your Railway dashboard.
   - Click **New Project** -> **Deploy from GitHub repo**.
   - Select your repository.

3. **Configure Environment Variables:**
   - In the Railway dashboard for your project, go to the **Variables** tab.
   - Add a new variable:
     - **Variable Name:** `BOT_TOKEN`
     - **Value:** `<Your_Telegram_Bot_Token>`

4. **Start the Bot:**
   - Railway will automatically detect the Python project via `requirements.txt` and `Procfile`.
   - It will build the image and run the bot 24/7.
   - You can monitor your bot logs under the **Deployments** -> **View Logs** section.
