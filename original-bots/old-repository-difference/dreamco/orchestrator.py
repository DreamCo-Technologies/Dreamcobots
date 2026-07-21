from dreamco.core.bot_registry import list_bots, get_bot

def run_all():
    results = []

    for bot_name in list_bots():
        bot_class = get_bot(bot_name)
        bot = bot_class()

        try:
            result = bot.run()
            results.append((bot_name, result))
        except Exception as e:
            print(f"{bot_name} failed: {e}")

    return results

if __name__ == "__main__":
    run_all()