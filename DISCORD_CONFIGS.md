# DISCORD BOT AND WEBHOOK SETUP

So if you want to controll the **Auto Clicker Pro** remotely and wants to receive notification through **Discord**.
Then you have to configure the **Webhooks** and Create a **Discord Bot**. So below is a guide how to do this.


## Creating Webhook 🪝

- Go to Any Server
- Go to Channel where you want the Notifications
- Click on Channel Setting -> Integrations -> Webhooks -> New Webhook -> Give any Name you want
- Copy Webhook URL (Paste this in the Auto Clicker Pro)


## Creating Discord Bot 🤖

- Go to [Discord Developer Portal](https://discord.com/developers/home) and Sign IN
- In left-hand menu Click on Applications -> New Application
- Give any name you want -> Click Create

### Getting Token And Configuring Permission
  
- In the left-hand menu -> click on Bot Tab
- Click Add Bot and confirm by clicking Yes
- Under the Token section -> click Reset Token
- Copy Token and paste this in the **Auto Clicker Pro**
- Scroll down in Bot page to Privileged Gateway Intents section
- Turn on the Message Content Intent

### Inviting bot To Server

- In left-hand menu -> click OAuth2 Tab
- Under Scopes, make sure to check the Bot box
- Under Bot Permissions -> Select View Channel, Send Messages, Read Message History, Use Slash Commands
- Then copy the generated URL paste it into the browser and add the Bot in the Server

  ### Important 🚨
  
  Don't share the token anywhere. Because anyone can access the Bot using it
