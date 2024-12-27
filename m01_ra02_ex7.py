# Llibreries necessaries
# pip install python-telegram-bot

# importa l'API de Telegram
from telegram.ext import Application, CommandHandler,ContextTypes
from telegram import Update
import datetime
from pymongo import MongoClient
import requests

# Connecta amb la base de dades
uri = "mongodb+srv://atarensi:supersayan123@testingsbd.1dxnn.mongodb.net/?retryWrites=true&w=majority&appName=TestingSBD"
client = MongoClient(uri, connectTimeoutMS=200, retryWrites=True)

client_db_supermercats = client.supermercats

# defineix una funció que saluda i que s'executarà quan el bot rebi el missatge /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    await update.message.reply_text(
    "👏👏 Felicitats! Tot el món mundial ja pot parlar amb el bot!!! 🎉 🎊")
    await update.message.reply_text(
        "Utilitza  /help per veure les comandes disponibles"
    )

    
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Soc un bot amb comandes /start, /help , /productes, /productaIMG, /llistaCompra, /supermercats")

async def productes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # El usuari ha de passar un codi en format string per a que el bot retorni la informació del producte
    # Exemple: /producta 1234
    try:
        producte = update.message.text.split(" ")[1]
        # Busca el producte a la base de dades
        producte = client_db_supermercats.productes.find_one({"id": producte})
        if producte:
            # Si el producte existeix, mostra la informació del producte
            await update.message.reply_text(f"ID: {producte['id']}")
            await update.message.reply_text(f"Nom: {producte['display_name']}")
            await update.message.reply_text(f"Preu per unitat: {producte['price_instructions']['unit_price']}")
            es_nou = "Si" if producte['price_instructions']['is_new'] else "No"
            await update.message.reply_text(f"Es nou: {es_nou}")
            await update.message.reply_text(f"Supermercat: {producte['supermarket']}")
        else:
            await update.message.reply_text("No s'ha trobat cap producte amb aquest codi")
    except IndexError:
        await update.message.reply_text("Per favor, proporciona un codi de producte després de la comanda /productes")

preuLlista = 0
async def llistaCompra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # El usuari ha de passar un codi en format string i la quantitat per a que el bot retorni la informació del producte
    # Exemple: /llistaCompra 1234 2
    try:
        params = update.message.text.split(" ")
        productaLlista = params[1]
        quantitat = int(params[2]) if len(params) > 2 else 1
        # Busca el producte a la base de dades
        productaLlista = client_db_supermercats.productes.find_one({"id": productaLlista})
        if productaLlista:
            # Suma el preu del producte a la llista de la compra
            global preuLlista
            preuLlista += float(productaLlista['price_instructions']['unit_price']) * quantitat
            # Si el producte existeix, mostra el preu total de la llista de la compra
            await update.message.reply_text(f"Preu total de la llista de la compra: {preuLlista:.2f}€")
        else:
            await update.message.reply_text("No s'ha trobat cap producte amb aquest codi")
    except IndexError:
        await update.message.reply_text("Per favor, proporciona un codi de producte i la quantitat després de la comanda /llistaCompra")


async def productaIMG(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # El usuari ha de passar un codi en format string per a que el bot retorni la informació del producte
    # Exemple: /producta 1234
    try:
        productaImg = update.message.text.split(" ")[1]
        # Busca el producte a la base de dades
        productaImg = client_db_supermercats.productes.find_one({"id": productaImg})
        if productaImg:
            # Si el producte existeix, mostra la imatge del producte
            await update.message.reply_photo(photo=productaImg['thumbnail'])
        else:
            await update.message.reply_text("No s'ha trobat cap producte amb aquest codi")
    except IndexError:
        await update.message.reply_text("Per favor, proporciona un codi de producte després de la comanda /productesIMG")

async def supermercats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Cuan posi la comanda /supermercats, el bot ha de retornar la llista de supermercats disponibles amb la quanityat de productes que tenen
    # Exemple: /supermercats
    col_supermercats = client_db_supermercats.productes
    supermercats = col_supermercats.distinct("supermarket")
    await update.message.reply_text("Supermercats disponibles:")
    for supermercat in supermercats:
        productes = col_supermercats.count_documents({"supermarket": supermercat})
        await update.message.reply_text(f"{supermercat}: {productes} productes")
    
def main():
    # declara una constant amb el access token que llegeix de token.txt
    TOKEN = open('./token.txt').read().strip()
    print(TOKEN)
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("productes", productes))
    application.add_handler(CommandHandler("productaIMG", productaIMG))
    application.add_handler(CommandHandler("llistaCompra", llistaCompra))
    application.add_handler(CommandHandler("supermercats", supermercats))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()